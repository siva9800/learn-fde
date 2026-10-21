"""Field labels and screen words in English and Telugu.

The three labels the application form itself prints in Telugu (applicant name, address, monthly income) are copied
from the form as Day 11's generator writes it, so the screen and the paper use the same words. The rest are draft
translations by the FDE, marked as such, for Lakshmi and the Vijayawada team lead to correct before the pilot. A
label nobody at Godavari has read is not finished, in either language.
"""

from __future__ import annotations

LABELS_STATUS = "draft: form labels copied from the form; the rest to be reviewed by Lakshmi and the Vijayawada team lead"

FIELD_LABELS: dict[str, tuple[str, str, str]] = {
    # field: (English, Telugu, source of the Telugu)
    "applicant_name": ("Applicant name", "దరఖాస్తుదారు పేరు", "form"),
    "address": ("Residential address", "చిరునామా", "form"),
    "monthly_income": ("Monthly income", "నెలసరి ఆదాయం", "form"),
    "date_of_birth": ("Date of birth", "పుట్టిన తేదీ", "draft"),
    "pan": ("PAN", "పాన్ నంబర్", "draft"),
    "mobile": ("Mobile", "మొబైల్ నంబర్", "draft"),
    "requested_amount": ("Loan amount requested", "కోరిన రుణ మొత్తం", "draft"),
    "tenure_months": ("Tenure (months)", "కాలవ్యవధి (నెలలు)", "draft"),
    "application_date": ("Application date", "దరఖాస్తు తేదీ", "draft"),
    "on_road_price": ("On-road price", "ఆన్-రోడ్ ధర", "draft"),
    "dealer_code": ("Dealer code", "డీలర్ కోడ్", "draft"),
    "quotation_date": ("Quotation date", "కొటేషన్ తేదీ", "draft"),
    "gross_weight_g": ("Gross weight (g)", "స్థూల బరువు (గ్రా)", "draft"),
    "net_weight_g": ("Net weight (g)", "నికర బరువు (గ్రా)", "draft"),
    "purity_carat": ("Purity (carat)", "స్వచ్ఛత (క్యారెట్)", "draft"),
    "appraisal_date": ("Appraisal date", "మదింపు తేదీ", "draft"),
}

BAND_WORDS: dict[str, tuple[str, str]] = {
    # Every band is said in words, never by colour alone (WCAG 2.2, 1.4.1).
    "auto_accept": ("Accepted: no action needed", "ఆమోదించబడింది"),
    "review": ("Check: confirm or correct", "తనిఖీ చేయండి"),
    "reject": ("Key in from the page", "పేజీ నుండి నమోదు చేయండి"),
    "forced": ("Look at this first", "ముందుగా ఇది చూడండి"),
}


def label(field_name: str) -> tuple[str, str]:
    en, te, _src = FIELD_LABELS.get(field_name, (field_name, field_name, "missing"))
    return en, te
