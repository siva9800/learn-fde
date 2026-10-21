"""The 2009 core lending system as its own documents describe it: the data dictionary behind the WSDL.

This is Godavari's knowledge, transcribed: field names, types, lengths, which fields the WSDL marks
mandatory, the code tables, the fault codes and the fourteen operations. It is what the stand-in enforces
and what the metadata translation layer (mapping/godavari_core_mapping.toml) must cover. Nothing here is
Kaagaz's design; when it disagrees with the mapping file, the mapping file is wrong. All of it is invented
for the course, in the shape such a system really has.
"""

from __future__ import annotations

from dataclasses import dataclass

NAMESPACE = "http://core.godavarifinance.example/lending/2009"
SERVICE_PATH = "/corelend/services/LendingService"

# The fourteen operations in Godavari's WSDL (Day 6: "Fourteen operations"). The stand-in implements the
# four the intake integration calls; the other ten are listed so the contract says what we do not use.
OPERATIONS_IN_REAL_WSDL: tuple[str, ...] = (
    "CreateApplication", "GetApplication", "GetApplicationByFileNumber", "UpdateApplication",
    "UpdateKYCStatus", "MarkSentBack", "GetApplicationStatus", "ListApplicationsByBranch", "AddCoApplicant",
    "GetCreditCheckResult", "CancelApplication", "GetBranchMaster", "GetCodeTable", "Ping",
)
OPERATIONS_USED: tuple[str, ...] = ("GetApplicationByFileNumber", "CreateApplication", "GetApplication",
                                    "UpdateKYCStatus")
WRITE_OPERATIONS: frozenset[str] = frozenset({"CreateApplication", "UpdateKYCStatus"})


@dataclass(frozen=True)
class CoreField:
    name: str
    kind: str              # "C" character, "N" number, "D" date as YYYYMMDD (everything travels as text)
    length: int
    mandatory: bool        # what the WSDL says (minOccurs="1")
    meaning: str           # the data dictionary's own words, as terse as the 2011 PDF


def _f(name: str, kind: str, length: int, mandatory: str, meaning: str) -> CoreField:
    return CoreField(name, kind, length, mandatory == "M", meaning)


# CreateApplication: sixty-one fields, twenty-three mandatory (Day 6, Day 7 inputs inventory).
CREATE_APPLICATION_FIELDS: tuple[CoreField, ...] = (
    _f("FILE_NO", "C", 12, "M", "file number assigned at branch"),
    _f("BRANCH_CD", "C", 5, "M", "branch code"),
    _f("PROD_CD", "C", 3, "M", "product code (CODE_MST PROD)"),
    _f("SCHM_CD", "C", 6, "O", "scheme code"),
    _f("SRC_CHNL", "C", 2, "M", "source channel (CODE_MST CHNL)"),
    _f("APPL_DT", "D", 8, "M", "application date"),
    _f("EXT_REF", "C", 20, "O", "external reference"),
    _f("ENTRY_USR", "C", 16, "M", "maker user id"),
    _f("VRFY_USR", "C", 16, "O", "checker user id"),
    _f("APPL_NM", "C", 60, "M", "applicant name"),
    _f("APPL_DOB", "D", 8, "M", "applicant date of birth"),
    _f("APPL_GNDR", "C", 1, "O", "gender M/F/T"),
    _f("PAN_NO", "C", 10, "M", "PAN"),
    _f("AADH_REF", "C", 12, "O", "aadhaar ref, masked"),
    _f("MOB_NO", "C", 10, "M", "mobile"),
    _f("ALT_MOB_NO", "C", 10, "O", "alternate mobile"),
    _f("EMAIL_ID", "C", 60, "O", "email"),
    _f("ADDR_LN1", "C", 40, "M", "address line 1"),
    _f("ADDR_LN2", "C", 40, "O", "address line 2"),
    _f("ADDR_LN3", "C", 40, "O", "address line 3"),
    _f("CITY_NM", "C", 30, "M", "city"),
    _f("DIST_CD", "C", 4, "O", "district code"),
    _f("STATE_CD", "C", 2, "M", "state (CODE_MST STATE)"),
    _f("PIN_CD", "C", 6, "M", "PIN code"),
    _f("ADDR_PRF_CD", "C", 2, "M", "address proof type (CODE_MST ADDRPRF)"),
    _f("RES_TYP", "C", 1, "O", "residence type O/R/F"),
    _f("YRS_AT_ADDR", "N", 2, "O", "years at address"),
    _f("CUST_FLG_1", "C", 1, "O", "flag 1"),
    _f("CUST_FLG_2", "C", 1, "O", "flag 2"),
    _f("CUST_FLG_3", "C", 1, "M", "flag 3"),
    _f("CUST_FLG_4", "C", 1, "O", "flag 4"),
    _f("EMP_NM", "C", 60, "O", "employer"),
    _f("EMP_TYP", "C", 2, "O", "employment type"),
    _f("MNTH_INC", "N", 9, "M", "monthly income"),
    _f("INC_PRF_CD", "C", 2, "M", "income proof type (CODE_MST INCPRF)"),
    _f("BANK_ACC_LST4", "C", 4, "O", "bank a/c last 4"),
    _f("BANK_IFSC", "C", 11, "O", "IFSC"),
    _f("LOAN_AMT", "N", 9, "M", "loan amount requested"),
    _f("TENOR_MM", "N", 3, "M", "tenor in months"),
    _f("ROI_PCT", "N", 5, "O", "rate of interest (system)"),
    _f("EMI_AMT", "N", 9, "O", "EMI (system)"),
    _f("PURP_CD", "C", 2, "O", "purpose code"),
    _f("DLR_CD", "C", 11, "O", "dealer code"),
    _f("ONRD_PRC", "N", 9, "O", "on-road price"),
    _f("QTN_DT", "D", 8, "O", "quotation date"),
    _f("VEH_MAKE", "C", 20, "O", "vehicle make"),
    _f("VEH_MODEL", "C", 30, "O", "vehicle model"),
    _f("GOLD_GRS_WT", "N", 7, "O", "gross weight g"),
    _f("GOLD_NET_WT", "N", 7, "O", "net weight g"),
    _f("GOLD_PURITY", "N", 2, "O", "purity carat"),
    _f("APPR_DT", "D", 8, "O", "appraisal date"),
    _f("APPR_ID", "C", 10, "O", "appraiser id"),
    _f("CO_APPL_FLG", "C", 1, "O", "co-applicant Y/N"),
    _f("CO_APPL_NM", "C", 60, "O", "co-applicant name"),
    _f("CO_APPL_PAN", "C", 10, "O", "co-applicant PAN"),
    _f("CO_APPL_REL", "C", 2, "O", "co-applicant relation"),
    _f("KYC_STAT", "C", 1, "M", "KYC status (CODE_MST KYC)"),
    _f("DOC_CNT", "N", 3, "M", "pages in file"),
    _f("RMK_TXT", "C", 200, "O", "remarks"),
    _f("RM_CD", "C", 8, "O", "branch officer code"),
    _f("CNSNT_FLG", "C", 1, "M", "consent Y/N"),
)
FIELD_BY_NAME: dict[str, CoreField] = {f.name: f for f in CREATE_APPLICATION_FIELDS}

# Fields the core computes itself. Sending them is not an error in 2009; it silently overwrites them,
# which the owner says has happened. The integration must leave them empty.
SYSTEM_COMPUTED: frozenset[str] = frozenset({"ROI_PCT", "EMI_AMT"})

# What GetApplication returns beyond the create fields.
READ_ONLY_FIELDS: tuple[CoreField, ...] = (
    _f("APPL_ID", "C", 12, "O", "application id (system)"),
    _f("APPL_STAT", "C", 1, "O", "application status (CODE_MST APPLSTAT)"),
    _f("CR_CHK_RSLT", "C", 2, "O", "credit check result"),
    _f("CRT_TS", "C", 14, "O", "created YYYYMMDDHHMISS"),
    _f("LST_UPD_TS", "C", 14, "O", "last updated YYYYMMDDHHMISS"),
)
DETAIL_FIELDS: tuple[str, ...] = ("APPL_ID", "FILE_NO", "BRANCH_CD", "PROD_CD", "APPL_STAT", "KYC_STAT",
                                  "LOAN_AMT", "TENOR_MM", "MNTH_INC", "CUST_FLG_3", "DLR_CD", "EXT_REF",
                                  "ENTRY_USR", "VRFY_USR", "APPL_NM", "PAN_NO", "MOB_NO", "CR_CHK_RSLT",
                                  "CRT_TS", "LST_UPD_TS")
SUMMARY_FIELDS: tuple[str, ...] = ("APPL_ID", "FILE_NO", "BRANCH_CD", "APPL_STAT", "EXT_REF", "CRT_TS")

CODE_TABLES: dict[str, dict[str, str]] = {
    "PROD": {"TW": "TWO WHEELER", "GL": "GOLD LOAN", "PL": "PERSONAL", "SB": "SMALL BUSINESS"},
    "CHNL": {"SC": "SCANNED AT BRANCH", "PP": "PHONE PHOTO", "MX": "MIXED"},
    "STATE": {"TS": "TELANGANA", "AP": "ANDHRA PRADESH"},
    "ADDRPRF": {"AA": "AADHAAR MASKED", "VI": "VOTER ID", "DL": "DRIVING LICENCE", "PP": "PASSPORT",
                "EB": "ELECTRICITY BILL", "PT": "PROPERTY TAX RCPT", "RR": "REGD RENT AGRMT"},
    "INCPRF": {"SS": "SALARY SLIP", "SD": "SELF DECLARATION", "BS": "BANK STATEMENT", "NA": "NOT APPLICABLE"},
    "KYC": {"P": "PENDING", "C": "COMPLETE", "D": "DEFICIENT"},
    "APPLSTAT": {"S": "SHELL", "K": "KEYED", "B": "IN BATCH", "Q": "QUERY TO BRANCH", "A": "SANCTIONED",
                 "R": "REJECTED", "X": "CANCELLED"},
    "YN": {"Y": "YES", "N": "NO"},
}
FIELD_CODE_TABLE: dict[str, str] = {
    "PROD_CD": "PROD", "SRC_CHNL": "CHNL", "STATE_CD": "STATE", "ADDR_PRF_CD": "ADDRPRF",
    "INC_PRF_CD": "INCPRF", "KYC_STAT": "KYC", "CUST_FLG_3": "YN", "CNSNT_FLG": "YN", "CO_APPL_FLG": "YN",
}

# Production release R26.08 (August 2026) made the dealer code mandatory for two-wheeler loans in the
# application code, not in the WSDL. The sandbox was refreshed in July, so it does not enforce it.
PRODUCTION_CONDITIONAL_MANDATORY: dict[str, tuple[str, str]] = {"DLR_CD": ("PROD_CD", "TW")}

# The fault catalogue: code -> (SOAP faultcode side, retryable, the text the core actually sends).
FAULTS: dict[str, tuple[str, bool, str]] = {
    "CL-E001": ("Client", False, "AUTHENTICATION FAILED"),
    "CL-E017": ("Server", True, "BATCH IN PROGRESS - WRITES NOT PERMITTED"),
    "CL-E023": ("Client", False, "MANDATORY FIELD MISSING"),
    "CL-E031": ("Client", False, "INVALID CODE"),
    "CL-E040": ("Client", False, "FIELD TOO LONG"),
    "CL-E041": ("Client", False, "INVALID FORMAT"),
    "CL-E052": ("Client", False, "FILE NOT REGISTERED"),
    "CL-E060": ("Client", False, "APPLICATION NOT FOUND"),
    "CL-E099": ("Server", True, "SERVICE BUSY, TRY LATER"),
}
