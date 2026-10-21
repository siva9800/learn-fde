# AI-written draft, kept for exercise 3.1 in 13-exercises.md. DO NOT RUN, DO NOT COPY.
# Prompt given to the agent: "Write a production-ready Python client that extracts loan fields from a page
# image with Claude, with retries, JSON validation and cost tracking."
# It looks finished. It has at least twelve problems. Find them before reading the solution.

import json
import logging
import time
import uuid

import anthropic
from pydantic import BaseModel, ConfigDict, ValidationError

logging.basicConfig(level=logging.INFO)
client = anthropic.Anthropic()
PRICE_PER_TOKEN = 3.0 / 1_000_000          # Claude pricing


class LoanFields(BaseModel):
    model_config = ConfigDict(extra="ignore")
    applicant_name: str = ""
    applicant_pan: str = ""
    requested_amount: int = 0


def extract_page(file_id: str, image_b64: str, prompt: str) -> LoanFields:
    request_id = f"{file_id}-{uuid.uuid4()}"                # idempotency key
    for attempt in range(5):
        try:
            response = client.messages.create(
                model="claude-sonnet-5-5",
                max_tokens=1024,
                temperature=0,                               # deterministic, so safe to cache
                system=prompt + f"\nToday is {time.strftime('%Y-%m-%d %H:%M:%S')}.",
                messages=[{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_b64}},
                    {"type": "text", "text": "Extract the fields as JSON."}]}],
                output_format={"type": "json_schema", "schema": LoanFields.model_json_schema()},
            )
            text = response.content[0].text
            logging.info("request %s prompt=%s response=%s", request_id, prompt, text)
            if not text.rstrip().endswith("}"):
                text = text + '"}'                            # repair truncated JSON
            cost = (1024 + len(text)) * PRICE_PER_TOKEN
            logging.info("cost for %s: $%.4f", file_id, cost)
            try:
                return LoanFields.model_validate(json.loads(text))
            except (ValidationError, json.JSONDecodeError):
                return LoanFields()                          # fall back to empty fields
        except Exception as e:                               # retry anything that goes wrong
            logging.warning("attempt %d failed: %s", attempt, e)
            time.sleep(2 ** attempt)
    raise RuntimeError(f"extraction failed for {file_id}")


def extract_file(file_id: str, pages: list[str], prompt: str) -> dict:
    results = [extract_page(file_id, p, prompt) for p in pages]       # every page, one at a time
    best = max(results, key=lambda r: r.requested_amount)              # the largest amount is the request
    if best.requested_amount > 0 and best.applicant_pan:
        return {"status": "APPROVED_FOR_CORE", **best.model_dump()}     # push straight to the core system
    for _ in range(3):                                                  # model was wrong: ask again
        results = [extract_page(file_id, p, prompt) for p in pages]
    return {"status": "NEEDS_REVIEW", **best.model_dump()}
