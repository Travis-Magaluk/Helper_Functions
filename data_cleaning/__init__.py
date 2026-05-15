"""
Standalone, NaN-safe text and data cleaning utilities.

All functions are safe to use with df.apply() on columns that may contain missing values —
NaN inputs are returned unchanged.

Public API — pipeline functions (apply multiple steps to DataFrame columns):
    full_address_clean                   — lowercase, strip, remove punctuation, abbreviations, directions
    standardize_text                     — title case and strip
    remove_periods_from_abbreviations_full — remove trailing periods from common abbreviations

Public API — domain-specific text normalization (text_clean.py):
    remove_some_punctuation              — strip commas, periods, double quotes
    replace_directionality               — expand cardinal abbreviations (n → north, etc.)
    replace_abbrivations                 — expand common street abbreviations
    replace_hashtag                      — normalize hash/number signs
    clean_hyphens_decisions              — normalize hyphens in decision strings
    replace_standardize_historic_district — standardize historic district name formatting
    remove_periods_from_abbreviations    — remove trailing periods from abbreviations
    standardize_phone_number             — normalize phone number formatting

Public API — NaN-safe primitive wrappers (safe_text_clean.py):
    safe_lower         — lowercase, NaN-safe
    safe_strip         — strip whitespace, NaN-safe
    safe_remove_quotes — remove double quotes, NaN-safe
    safe_title         — title case, NaN-safe

Public API — date and monetary cleaning:
    convert_address_date             — parse non-standard date strings to datetime
    full_money_clean                 — full monetary string cleaning pipeline
    remove_money_punc_and_decimals   — strip $, commas, and decimal places
    extract_highest                  — extract the highest dollar value from a string

"""
from Helper_Functions.data_cleaning.text_clean_pipeliness import (
    full_address_clean,
    standardize_text,
    remove_periods_from_abbreviations_full,
)
from Helper_Functions.data_cleaning.text_clean import (
    remove_some_punctuation,
    replace_directionality,
    replace_abbrivations,
    replace_hashtag,
    clean_hyphens_decisions,
    replace_standardize_historic_district,
    remove_periods_from_abbreviations,
    standardize_phone_number,
)
from Helper_Functions.data_cleaning.safe_text_clean import (
    safe_lower,
    safe_strip,
    safe_remove_quotes,
    safe_title,
)
from Helper_Functions.data_cleaning.money_clean import (
    full_money_clean,
    remove_money_punc_and_decimals,
    extract_highest,
)

__all__ = [
    # pipelines
    "full_address_clean",
    "standardize_text",
    "remove_periods_from_abbreviations_full",
    # text normalization
    "remove_some_punctuation",
    "replace_directionality",
    "replace_abbrivations",
    "replace_hashtag",
    "clean_hyphens_decisions",
    "replace_standardize_historic_district",
    "remove_periods_from_abbreviations",
    "standardize_phone_number",
    # NaN-safe primitives
    "safe_lower",
    "safe_strip",
    "safe_remove_quotes",
    "safe_title",
    # date / money
    "convert_address_date",
    "full_money_clean",
    "remove_money_punc_and_decimals",
    "extract_highest",
    # column splitting
    "split_check_date_column",
    "split_owner_name",
    "split_shpo_column",
    "split_decision_date",
]
