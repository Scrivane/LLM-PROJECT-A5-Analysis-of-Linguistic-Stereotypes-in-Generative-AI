import pandas as pd
import re
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV = str(BASE_DIR / "result_silvia_Mistral.csv")
OUTPUT_CSV = str(BASE_DIR / "result_silvia_Mistral_normalized.csv")

df = pd.read_csv(
    INPUT_CSV,
    engine="python",
    on_bad_lines="skip"
)

# -------------------------
# Processing functions
# -------------------------
def split_answer_and_motivation(text):
    if not isinstance(text, str):
        return "", ""
    parts = re.split(r"\bmotivazione\b", text, flags=re.IGNORECASE, maxsplit=1)
    risposta = parts[0].strip()
    motivazione = parts[1].strip() if len(parts) > 1 else ""
    return risposta, motivazione

def normalize_risposta(risposta_raw):
    if not isinstance(risposta_raw, str):
        return "Altro"
    r = risposta_raw.lower()
    r = re.sub(r"[*_:`\"'\-\n]", " ", r)
    r = re.sub(r"\s+", " ", r).strip()
    if re.search(r"\bpersona\s*a\b", r):
        return "Persona A"
    elif re.search(r"\bpersona\s*b\b", r):
        return "Persona B"
    else:
        return "Altro"

# -------------------------
# Apply processing
# -------------------------
df[["risposta_raw", "motivazione"]] = df["risposta"].apply(
    lambda x: pd.Series(split_answer_and_motivation(x))
)

df["risposta_norm"] = df["risposta_raw"].apply(normalize_risposta)

normalized = df[["prompt", "risposta_norm", "motivazione", "dialetto"]]
normalized.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

# -------------------------
# Filtered counts & percentages
# -------------------------
def filter_by_motivazione_and_compute(df_normalized, *,
                                     counts_out: str = str(BASE_DIR / "persona_counts_filtered.csv"),
                                     perc_out: str = str(BASE_DIR / "persona_percentages_filtered.csv")) -> None:
    """Remove rows where `motivazione` is empty, then compute and save
    counts and percentages of `risposta_norm` per `dialetto`.

    Produces two CSVs: counts and percentages. Prints concise tables.
    """
    # ensure column exists
    if "motivazione" not in df_normalized.columns:
        raise KeyError("DataFrame must contain 'motivazione' column")

    filtered = df_normalized[df_normalized["motivazione"].astype(str).str.strip() != ""]

    if filtered.empty:
        print("Warning: no rows with non-empty 'motivazione' after filtering.")

    counts = (
        filtered
        .groupby(["dialetto", "risposta_norm"])
        .size()
        .unstack(fill_value=0)
    )

    percentages = counts.div(counts.sum(axis=1).replace(0, 1), axis=0) * 100

    # save outputs
    counts.to_csv(counts_out, encoding="utf-8")
    percentages.round(2).to_csv(perc_out, encoding="utf-8")



# run filter+counts and save
filter_by_motivazione_and_compute(normalized)