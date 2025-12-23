import csv
import os
import re
from typing import Dict, List, Optional


def build_mapping_from_parm_csv(csv_path: str) -> Dict[str, List[str]]:
    """Build a mapping Italian -> list of Parmigiano lemmas from the linked CSV.

    Expected columns: `lemma_it`, `lemma_parm`, `lemma_parm_2`, ...
    Entries with '_' are ignored.
    """
    mapping: Dict[str, List[str]] = {}
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with open(csv_path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        # find all lemma_parm columns
        parm_cols = [c for c in (reader.fieldnames or []) if c.startswith("lemma_parm")]
        for row in reader:
            it = (row.get("lemma_it") or "").strip().lower()
            if not it:
                continue
            parm_forms: List[str] = []
            for c in parm_cols:
                v = (row.get(c) or "").strip()
                if not v or v == "_":
                    continue
                # some cells may hold multiple alternatives separated by ',' or ';'
                for part in re.split(r"[;,/]", v):
                    p = part.strip()
                    if p and p not in parm_forms:
                        parm_forms.append(p)

            if not parm_forms:
                continue
            mapping.setdefault(it, [])
            for f in parm_forms:
                if f not in mapping[it]:
                    mapping[it].append(f)

    return mapping


"""
if __name__ == '__main__':
    sample = "Io lavoro in un azienda che si occupa di costruzioni e appalti, la mia azienda fattura molti soldi grazie agli appalti statali"
    try:
        out = translate_it_to_parmigiano(sample)
        print('IN :', sample)
        print('OUT:', out)
    except FileNotFoundError as e:
        print('CSV not found, please point to the file path:', e)
"""