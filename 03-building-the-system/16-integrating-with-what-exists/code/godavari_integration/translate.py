"""The metadata translation layer in code: load the mapping, check it, and translate in both directions.

The mapping file (mapping/godavari_core_mapping.toml) is the artefact; this module only obeys it.
  to_core()            canonical record -> the 61-field CreateApplication payload; fails closed BEFORE
                       the call on anything the core would reject, and on anything it would silently accept
                       wrongly (an unknown code, a system-computed field, a line too long)
  from_core()          a core record -> canonical names and values; an unknown code is an error, not a pass
  describe_for_model() a record in business language: "Applicant is salaried: yes", never "CUST_FLG_3: Y",
                       with direct identifiers left out
  fingerprint()        SHA-256 of the file with line endings normalised; must match mapping_signoff.json
"""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .corespec import CODE_TABLES, CREATE_APPLICATION_FIELDS, FIELD_BY_NAME, FIELD_CODE_TABLE, SYSTEM_COMPUTED

MAPPING_DIR = Path(__file__).resolve().parent / "mapping"
CORE_MAPPING = MAPPING_DIR / "godavari_core_mapping.toml"
SIGNOFF = MAPPING_DIR / "mapping_signoff.json"

_FILE_NO = re.compile(r"^GF-\d{5}$")
_PAN = re.compile(r"^[A-Z]{5}\d{4}[A-Z]$")


class MappingError(ValueError):
    """The translation cannot be done safely. Raised before any call to the core."""


@dataclass(frozen=True)
class FieldMap:
    core: str
    canonical: str | None
    business_name: str
    meaning: str
    transform: str
    data_class: str
    defaults: dict[str, str]

    @property
    def ours(self) -> bool:
        return self.canonical is not None


def _fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


class Mapping:
    def __init__(self, path: Path = CORE_MAPPING) -> None:
        self.path = path
        with path.open("rb") as fh:
            self.raw = tomllib.load(fh)
        self.version: str = self.raw["meta"]["version"]
        self.data_classes: dict[str, dict[str, Any]] = self.raw["data_classes"]
        self.codes: dict[str, dict[str, str]] = self.raw["codes"]
        self.fields: dict[str, FieldMap] = {name: self._field(name, spec) for name, spec in self.raw["core"]["fields"].items()}
        self.read_fields: dict[str, FieldMap] = {name: self._field(name, spec)
                                                 for name, spec in self.raw["core"]["read_fields"].items()}

    @staticmethod
    def _field(name: str, spec: dict[str, Any]) -> FieldMap:
        ours = spec.get("ours", True)
        return FieldMap(name, spec.get("canonical") if ours else None, spec["business_name"], spec["meaning"],
                        spec.get("transform", ""), spec.get("data_class", ""), dict(spec.get("default_by_product", {})))

    # ---- integrity ----------------------------------------------------------------------------------
    def fingerprint(self) -> str:
        return _fingerprint(self.path)

    def check_signoff(self, signoff: Path = SIGNOFF) -> dict[str, str]:
        record = json.loads(signoff.read_text(encoding="utf-8")).get(self.path.name)
        if record is None:
            raise MappingError(f"no sign-off record for {self.path.name}")
        if record.get("version") != self.version or record.get("fingerprint") != self.fingerprint():
            raise MappingError(f"{self.path.name} changed since it was reviewed (record {record.get('version')}, "
                               f"file {self.version}); bump the version and get the owner's review")
        return record

    def problems(self) -> list[str]:
        """Everything that is wrong with the mapping against the core's own data dictionary."""
        out: list[str] = []
        names = {f.name for f in CREATE_APPLICATION_FIELDS}
        out += [f"core field {n} has no mapping entry (map it, or mark ours = false with a meaning)"
                for n in sorted(names - set(self.fields))]
        out += [f"mapping entry {n} is not a core field" for n in sorted(set(self.fields) - names)]
        for name, fm in self.fields.items():
            spec = FIELD_BY_NAME.get(name)
            if spec is None:
                continue
            if spec.mandatory and not fm.ours:
                out.append(f"{name} is mandatory in the WSDL but marked not ours")
            if name in SYSTEM_COMPUTED and fm.ours:
                out.append(f"{name} is computed by the core and must never be sent")
            if fm.ours and fm.data_class not in self.data_classes:
                out.append(f"{name}: data class {fm.data_class!r} is not defined")
            if fm.transform.startswith("code:"):
                table = fm.transform.split(":", 1)[1]
                if table not in self.codes:
                    out.append(f"{name}: code table {table} missing from [codes]")
                    continue
                bad = sorted(set(self.codes[table].values()) - set(CODE_TABLES.get(table, {})))
                if bad:
                    out.append(f"{name}: codes {bad} are not in the core's CODE_MST {table}")
            if not fm.meaning.strip() or fm.meaning.strip().upper() == spec.meaning.upper():
                out.append(f"{name}: meaning is empty or just repeats the data dictionary")
        for name in FIELD_CODE_TABLE:
            fm = self.fields.get(name)
            if fm and fm.ours and not (fm.transform.startswith("code:") or (fm.transform == "yn" and FIELD_CODE_TABLE[name] == "YN")):
                out.append(f"{name} is a coded field but its transform is {fm.transform!r}")
        canon = [f.canonical for f in self.fields.values() if f.ours]
        dupes = sorted({c for c in canon if canon.count(c) > 1})
        out += [f"canonical name {c} is used by two core fields" for c in dupes]
        for dc, rules in self.data_classes.items():
            if dc == "direct_identifier" and rules.get("copy_out_of_godavari_systems"):
                out.append("direct identifiers must not be copied out of Godavari's systems")
        return out

    # ---- translation --------------------------------------------------------------------------------
    def to_core(self, record: dict[str, Any]) -> dict[str, str]:
        product = record.get("product")
        payload: dict[str, str] = {}
        for name, fm in self.fields.items():
            if not fm.ours:          # branch-keyed or system-computed: never sent by us
                continue
            value = record.get(fm.canonical or "")
            spec = FIELD_BY_NAME[name]
            if value in (None, ""):
                if product in fm.defaults:
                    payload[name] = fm.defaults[product]
                    continue
                if spec.mandatory:
                    raise MappingError(f"{name} ({fm.business_name}) is mandatory and {fm.canonical} is empty")
                continue
            core_value = self._to_core_value(name, fm, value)
            if spec.kind != "N" and len(core_value) > spec.length:
                raise MappingError(f"{name} ({fm.business_name}) is {len(core_value)} characters; the core allows "
                                   f"{spec.length} and would reject it (CL-E040)")
            payload[name] = core_value
        return payload

    def _to_core_value(self, name: str, fm: FieldMap, value: Any) -> str:
        t = fm.transform
        try:
            if t.startswith("code:"):
                table = self.codes[t.split(":", 1)[1]]
                key = str(value).strip().lower()
                if key not in table:
                    raise MappingError(f"{name}: {value!r} has no code in {t}; it is not on the list, so it is not sent")
                return table[key]
            if t == "text":
                return str(value).strip()
            if t == "upper":
                return " ".join(str(value).upper().split())
            if t == "file_no":
                v = str(value).strip().upper()
                if not _FILE_NO.match(v):
                    raise MappingError(f"{name}: {value!r} is not a Godavari file number")
                return v
            if t == "date":
                d = value if isinstance(value, date) else date.fromisoformat(str(value))
                return d.strftime("%Y%m%d")
            if t == "rupees" or t == "int":
                d = Decimal(str(value))
                if d != d.to_integral_value() or d < 0:
                    raise MappingError(f"{name}: {value!r} is not a whole non-negative number")
                return str(int(d))
            if t == "grams":
                return f"{Decimal(str(value)).quantize(Decimal('0.01'))}"
            if t == "yn":
                if not isinstance(value, bool):
                    raise MappingError(f"{name}: expected true or false, got {value!r}")
                return "Y" if value else "N"
            if t == "pan":
                v = str(value).strip().upper()
                if not _PAN.match(v):
                    raise MappingError(f"{name}: not a PAN")
                return v
            if t == "aadhaar_masked":
                v = str(value).strip().upper()
                if not re.fullmatch(r"X{8}\d{4}", v):
                    raise MappingError(f"{name}: only a masked reference (8 X and 4 digits) may be sent")
                return v
            if t == "mobile":
                v = re.sub(r"\D", "", str(value))
                if len(v) != 10:
                    raise MappingError(f"{name}: a mobile number has ten digits")
                return v
            if t == "pin":
                v = str(value).strip()
                if not re.fullmatch(r"\d{6}", v):
                    raise MappingError(f"{name}: a PIN code has six digits")
                return v
        except (InvalidOperation, ValueError) as exc:
            if isinstance(exc, MappingError):
                raise
            raise MappingError(f"{name}: cannot transform {value!r} with {t}: {exc}") from None
        raise MappingError(f"{name}: unknown transform {t!r}")

    def from_core(self, record: dict[str, str]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for name, value in record.items():
            fm = self.fields.get(name) or self.read_fields.get(name)
            if fm is None or not fm.ours or value in (None, ""):
                continue
            out[fm.canonical or name] = self._from_core_value(name, fm, value)
        return out

    def _from_core_value(self, name: str, fm: FieldMap, value: str) -> Any:
        t = fm.transform
        if t.startswith("code:"):
            inverse = {v: k for k, v in self.codes[t.split(":", 1)[1]].items()}
            if value not in inverse:
                raise MappingError(f"{name}: the core sent code {value!r}, which the mapping does not know; "
                                   "add it with the owner before anything reads it")
            return inverse[value]
        if t == "date":
            return date(int(value[:4]), int(value[4:6]), int(value[6:8]))
        if t in ("rupees", "int"):
            return int(Decimal(value))
        if t == "grams":
            return Decimal(value)
        if t == "yn":
            return value == "Y"
        return value

    def describe_for_model(self, record: dict[str, str]) -> list[str]:
        """Business language for a model's context: the meaning travels with the value, identifiers do not."""
        lines = []
        for name, value in record.items():
            fm = self.fields.get(name) or self.read_fields.get(name)
            if fm is None or value in (None, "") or fm.data_class in ("direct_identifier", "system"):
                continue
            if self.data_classes.get(fm.data_class, {}).get("show_to_model") == "no":
                continue
            shown: Any = self._from_core_value(name, fm, value) if fm.ours else value
            if isinstance(shown, bool):
                shown = "yes" if shown else "no"
            elif isinstance(shown, date):
                shown = shown.isoformat()
            shown = str(shown).replace("_", " ") if fm.transform.startswith("code:") else str(shown)
            lines.append(f"{fm.business_name}: {shown}")
        return lines

    def store_policy(self, core_field: str) -> dict[str, Any]:
        fm = self.fields.get(core_field) or self.read_fields.get(core_field)
        if fm is None or not fm.data_class:
            raise MappingError(f"{core_field} has no data class")
        return self.data_classes[fm.data_class]

    def direct_identifier_fields(self) -> set[str]:
        return {n for n, f in {**self.fields, **self.read_fields}.items() if f.data_class == "direct_identifier"}


def write_signoff(mapping: Mapping, reviewed_by: str, reviewed_on: str, status: str, path: Path = SIGNOFF) -> None:
    records = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    records[mapping.path.name] = {"version": mapping.version, "fingerprint": mapping.fingerprint(),
                                  "status": status, "reviewed_by": reviewed_by, "reviewed_on": reviewed_on}
    path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8", newline="\n")
