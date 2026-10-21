"""The metadata translation layer: complete against the data dictionary, versioned, owned, fail-closed."""

from __future__ import annotations

import shutil
from datetime import date

import pytest

from godavari_integration.canonical import split_address
from godavari_integration.corespec import CREATE_APPLICATION_FIELDS, SYSTEM_COMPUTED
from godavari_integration.translate import CORE_MAPPING, SIGNOFF, Mapping, MappingError


def test_the_mapping_has_no_problems_against_the_data_dictionary(mapping):
    assert mapping.problems() == []
    assert len(mapping.fields) == 61
    assert sum(fm.ours for fm in mapping.fields.values()) == 40


def test_the_reviewed_fingerprint_matches_the_file(mapping):
    record = mapping.check_signoff()
    assert record["version"] == mapping.version == "1.3.0" and record["reviewed_by"] == "the core-system owner"


def test_an_edit_without_review_refuses_to_run(tmp_path):
    copy = tmp_path / CORE_MAPPING.name
    shutil.copy(CORE_MAPPING, copy)
    copy.write_text(copy.read_text(encoding="utf-8").replace('"two-wheeler" = "TW"', '"two-wheeler" = "TW"\n"ev" = "TW"'),
                    encoding="utf-8")
    with pytest.raises(MappingError, match="changed since it was reviewed"):
        Mapping(copy).check_signoff(SIGNOFF)


def test_every_mandatory_field_is_ours_or_defaulted(mapping):
    for spec in CREATE_APPLICATION_FIELDS:
        if spec.mandatory:
            assert mapping.fields[spec.name].ours, spec.name


def test_cust_flg_3_means_salaried_and_the_model_sees_the_meaning(mapping, writable):
    fm = mapping.fields["CUST_FLG_3"]
    assert fm.canonical == "is_salaried" and "salary" in fm.meaning
    f, rec = next((f, r) for f, r in writable if r["is_salaried"] is True)
    lines = mapping.describe_for_model(mapping.to_core(rec))
    assert "Applicant is salaried: yes" in lines
    text = "\n".join(lines)
    assert "CUST_FLG_3" not in text and rec["pan"] not in text and rec["applicant_name"] not in text


def test_unknown_codes_fail_closed_in_both_directions(mapping, writable):
    _, rec = writable[0]
    with pytest.raises(MappingError, match="not on the list"):
        mapping.to_core({**rec, "address_proof_kind": "gas bill"})
    with pytest.raises(MappingError, match="does not know"):
        mapping.from_core({"APPL_STAT": "H"})                   # added in production R26.08; not yet mapped


def test_round_trip_keeps_the_business_meaning(mapping, writable):
    _, rec = writable[0]
    back = mapping.from_core(mapping.to_core(rec))
    for k in ("product", "channel", "kyc_status", "requested_amount", "tenure_months", "application_date",
              "consent_given", "state", "address_proof_kind"):
        assert back[k] == rec[k], k


def test_gold_conventions_come_from_the_mapping_not_the_code(mapping, writable):
    _, rec = next((f, r) for f, r in writable if f.bundle.product == "gold")
    core = mapping.to_core(rec)
    assert (core["MNTH_INC"], core["INC_PRF_CD"], core["CUST_FLG_3"]) == ("0", "NA", "N")


def test_system_computed_fields_are_never_ours(mapping):
    assert all(not mapping.fields[n].ours for n in SYSTEM_COMPUTED)


def test_lengths_are_checked_before_the_core_does(mapping, writable):
    _, rec = writable[0]
    with pytest.raises(MappingError, match="CL-E040"):
        mapping.to_core({**rec, "address_line1": "X" * 41})


def test_address_split_respects_forty_and_fails_closed_without_a_pin():
    parts = split_address("47-18, KPHB Colony, Kukatpally, Hyderabad 500072")
    assert parts == {"address_line1": "47-18, KPHB Colony, Kukatpally", "address_line2": None, "address_line3": None,
                     "city": "Hyderabad", "pin": "500072"}
    assert split_address("near the water tank, Guntur")["pin"] is None


def test_file_numbers_are_normalised_or_refused(mapping, writable):
    _, rec = writable[0]
    assert mapping.to_core({**rec, "file_number": " gf-25001 "})["FILE_NO"] == "GF-25001"
    with pytest.raises(MappingError):
        mapping.to_core({**rec, "file_number": "GF-2503"})


def test_direct_identifiers_may_not_leave_godavari_systems(mapping):
    rules = mapping.data_classes["direct_identifier"]
    assert rules["copy_out_of_godavari_systems"] is False and rules["write_to_logs"] is False
    assert {"APPL_NM", "PAN_NO", "MOB_NO", "APPL_DOB", "AADH_REF"} <= mapping.direct_identifier_fields()


def test_dates_go_out_as_yyyymmdd(mapping, writable):
    _, rec = writable[0]
    assert mapping.to_core({**rec, "application_date": date(2026, 11, 2)})["APPL_DT"] == "20261102"
