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


def translate_it_to_parmigiano(text: str, csv_path: Optional[str] = None) -> str:
    """Translate Italian text to Parmigiano using the linked CSV resource.

    - Replaces matching Italian lemmas with the first Parmigiano candidate.
    - Preserves punctuation and capitalization; unknown tokens left unchanged.
    """
    if csv_path is None:
        base = os.path.join(os.path.dirname(__file__), '..', 'rdf', 'source', 'DialettoParmigiano_linked_WIP_final_cleaned.csv')
        csv_path = os.path.normpath(base)

    mapping = build_mapping_from_parm_csv(csv_path)

    def normalize_key(s: str) -> str:
        return re.sub(r"\s+", " ", s.strip().lower())

    keys = sorted(mapping.keys(), key=lambda s: len(s.split()), reverse=True)
    max_words = max((len(k.split()) for k in keys), default=1)

    parts = re.split(r'(\W+)', text, flags=re.UNICODE)
    output_parts: List[str] = []
    i = 0
    while i < len(parts):
        part = parts[i]
        if not part or re.match(r'\W+$', part, flags=re.UNICODE):
            output_parts.append(part)
            i += 1
            continue

        matched = False
        j = i
        word_tokens = []
        idxs = []
        while j < len(parts) and len(word_tokens) < max_words:
            if parts[j] and not re.match(r'\W+$', parts[j], flags=re.UNICODE):
                word_tokens.append(parts[j])
                idxs.append(j)
            j += 1

        for wcount in range(len(word_tokens), 0, -1):
            cand_words = [t for t in word_tokens[:wcount]]
            cand_key = normalize_key(' '.join(cand_words))
            if cand_key in mapping:
                parm_choice = mapping[cand_key][0]
                if cand_words[0] and cand_words[0][0].isupper():
                    parm_choice = parm_choice.capitalize()
                output_parts.append(parm_choice)
                i = idxs[wcount-1] + 1
                matched = True
                break

        if not matched:
            key = normalize_key(part)
            if key in mapping:
                parm_choice = mapping[key][0]
                if part and part[0].isupper():
                    parm_choice = parm_choice.capitalize()
                output_parts.append(parm_choice)
            else:
                output_parts.append(part)
            i += 1

    return ''.join(output_parts)


if __name__ == '__main__':
    sample = "Io lavoro in un azienda che si occupa di costruzioni e appalti, la mia azienda fattura molti soldi grazie agli appalti statali"
    try:
        out = translate_it_to_parmigiano(sample)
        print('IN :', sample)
        print('OUT:', out)
    except FileNotFoundError as e:
        print('CSV not found, please point to the file path:', e)
