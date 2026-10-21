# 05 · Streaming: For the Person Watching, Not for the Pipeline

> Day 12 · Section 5 of 14 · [Chapter overview](README.md) · Previous: [04 · Tool use](04-tool-use.md) · Next: [06 · Retries, timeouts and rate limits](06-retries-timeouts-and-rate-limits.md)

---

## 5.1 What streaming changes, and what it does not

A streamed response arrives as a sequence of small events (server-sent events, in both Anthropic's and
OpenAI's APIs) instead of one body at the end. It changes **when the first words appear**. It does not
change when the last word arrives, how many tokens are generated or what the call costs.

So the question is never "is streaming faster?" It is "is a person waiting for this answer, reading as
it arrives?" At Godavari:

| Output | A person reading it live? | Stream? |
|---|---|---|
| fields from 1,282 pages in the 02:00 drop | no, nobody until 08:00 | no |
| the plain-language note beside a file on Lakshmi's screen (Day 11's `draft_note`) | yes | yes |
| the operator assistant's answer about a file (section 04) | yes | yes |

## 5.2 Measured on the fake provider

`code/streaming_demo.py` sends the same note three ways (virtual time, real output):

```text
large tier, non-streaming  first words on screen at  5.4 s, complete at  5.4 s, 313 output tokens (thinking included)
large tier, streaming      first words on screen at  4.1 s, complete at  5.4 s, 313 output tokens (thinking included)
small tier, streaming      first words on screen at  0.4 s, complete at  0.9 s, 93 output tokens (thinking included)

The same note in the 02:00 batch: nobody is watching, so streaming buys nothing and adds a parser that must survive a stream cut half way.
```

Read the second line carefully. Streaming the large tier moved the first word from 5.4 to 4.1 seconds,
not to half a second, because the fake model (like current reasoning models) spends its first few
seconds thinking before it writes anything visible. The big win came from the third line: a note that
only restates findings code has already decided does not need the large model or much thinking. For an
interface, time to first token is set by the model tier, the reasoning effort and the input size;
streaming only stops you hiding it behind a spinner.

> **The UPI picture again.** The "processing" screen does not make the banks faster. It tells you the
> request is alive. Streaming is that screen for a model.

## 5.3 What streaming makes harder

- **Errors can arrive after a 200.** Anthropic's error documentation notes that with server-sent
  events, an error can occur after the API has returned 200, and it arrives as an error event in the
  stream, not as a status code. Your retry logic must handle a stream that dies half way: discard the
  partial text and retry the whole call, or show the reader what arrived and a "retry" button.
- **Partial JSON is not JSON.** If you stream a structured output, the pieces only validate at the end.
  Do not act on half an object. Anthropic's fine-grained tool streaming, for example, delivers tool
  arguments as they are generated and leaves validation of the result to you.
- **Usage arrives at the end.** The ledger row is written when the stream closes; a stream abandoned by
  a closed browser tab must still be recorded, with an estimated count if necessary.

## 5.4 Rules

1. Stream only what a person reads as it arrives.
2. Never stream into code that acts on the result before it is complete.
3. Log the stream's final usage, or an estimate if it was cut.
4. For a faster first word, pick a smaller tier or lower effort first; stream second.
