import os
import re
from typing import Dict, List, Optional
from .Siciliano.scripts.translate_it_to_sicilian import build_mapping_from_tsv, try_parse_ttl_for_mappings
from .Parmigiano.scripts.translate_it_to_parmigiano import build_mapping_from_parm_csv


def translate (text: str,
               dialect: str,
               resource_path: Optional[str] = None,
               ttl_path: Optional[str] = None) -> str:
    """Translate Italian text to the specified dialect using the appropriate resource.

    Supported dialects: 'siciliano', 'parmigiano'.
    - For Sicilian, uses TSV (and optionally TTL) resources.
    - For Parmigiano, uses the linked CSV resource.
    """
    dialect = dialect.lower()
    if dialect == 'siciliano':
        return translate_it_to_sicilian(text, tsv_path=resource_path, ttl_path=ttl_path)
    elif dialect == 'parmigiano':
        return translate_it_to_parmigiano(text, csv_path=resource_path)
    else:
        raise ValueError(f"Unsupported dialect: {dialect}. Supported dialects are 'sicilian' and 'parmigiano'.")


def translate_it_to_sicilian(text: str,
                             tsv_path: Optional[str] = None,
                             ttl_path: Optional[str] = None) -> str:
    """Translate Italian text to Sicilian using the TSV (and optionally TTL) resources.

    - Words/phrases found in the resources are replaced by the first Sicilian candidate.
    - Unknown tokens are left unchanged.
    - Capitalization of the first letter is preserved.
    """
    # default TSV path relative to this script (matches workspace structure)
    if tsv_path is None:
        base = os.path.join(os.path.dirname(__file__), 'Siciliano', 'rdf', 'source', 'siciliano.tsv')
        tsv_path = os.path.normpath(base)
    # default TTL path (optional) inside the Siciliano rdf folder
    if ttl_path is None:
        ttl_default = os.path.join(os.path.dirname(__file__), 'Siciliano', 'rdf', 'sicilianoLemmabank.ttl')
        ttl_path = os.path.normpath(ttl_default)

    mapping = build_mapping_from_tsv(tsv_path)
    if ttl_path:
        extra = try_parse_ttl_for_mappings(ttl_path)
        for k, vals in extra.items():
            if k in mapping:
                # extend without duplicates
                for v in vals:
                    if v and v not in mapping[k]:
                        mapping[k].append(v)
            else:
                mapping[k] = vals

    # Prepare keys sorted by descending word count (longest-first matching)
    def normalize_key(s: str) -> str:
        return re.sub(r"\s+", " ", s.strip().lower())

    keys = sorted(mapping.keys(), key=lambda s: len(s.split()), reverse=True)
    max_words = max((len(k.split()) for k in keys), default=1)

    # Tokenize preserving separators
    parts = re.split(r'(\W+)', text, flags=re.UNICODE)

    output_parts: List[str] = []
    i = 0
    # For matching we need a list of indices of word tokens
    while i < len(parts):
        part = parts[i]
        if not part or re.match(r'\W+$', part, flags=re.UNICODE):
            output_parts.append(part)
            i += 1
            continue

        # attempt to match up to max_words words ahead
        matched = False
        # build sequence of next word tokens skipping non-word tokens
        # create arrays of (index, token)
        j = i
        word_tokens = []
        idxs = []
        # collect tokens up to max_words words
        while j < len(parts) and len(word_tokens) < max_words:
            if parts[j] and not re.match(r'\W+$', parts[j], flags=re.UNICODE):
                word_tokens.append(parts[j])
                idxs.append(j)
            j += 1

        # try longest match down to single word
        for wcount in range(len(word_tokens), 0, -1):
            cand_words = [t for t in word_tokens[:wcount]]
            cand_key = normalize_key(' '.join(cand_words))
            if cand_key in mapping:
                # choose first sicilian candidate
                sic_choice = mapping[cand_key][0]
                # preserve capitalization of first character
                if cand_words[0] and cand_words[0][0].isupper():
                    sic_choice = sic_choice.capitalize()

                # replace from parts[idxs[0]] up to idxs[wcount-1]
                start_idx = idxs[0]
                end_idx = idxs[wcount-1]
                # append any separators that were before start_idx
                output_parts.append(sic_choice)

                # advance i to the token after end_idx
                i = end_idx + 1
                matched = True
                break

        if not matched:
            # no phrase match, try single-word lowercased lookup
            key = normalize_key(part)
            if key in mapping:
                sic_choice = mapping[key][0]
                if part and part[0].isupper():
                    sic_choice = sic_choice.capitalize()
                output_parts.append(sic_choice)
            else:
                output_parts.append(part)
            i += 1

    return ''.join(output_parts)



def translate_it_to_parmigiano(text: str, csv_path: Optional[str] = None) -> str:
    """Translate Italian text to Parmigiano using the linked CSV resource.

    - Replaces matching Italian lemmas with the first Parmigiano candidate.
    - Preserves punctuation and capitalization; unknown tokens left unchanged.
    """
    if csv_path is None:
        base = os.path.join(os.path.dirname(__file__), 'Parmigiano', 'rdf', 'source', 'DialettoParmigiano_linked_WIP_final_cleaned.csv')
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
    A = "Mi chiamo Francesca, ho 23 anni e studio filosofia all'università. Lavoro part-time come barista in un bar, ho turni regolari che mi permettono di pagare l'affitto senza troppi problemi, così da poter proseguire gli studi, continuo a sognare di scrivere un romanzo."
    Parm  = translate(A, dialect='parmigiano')
    Sic = translate(A, dialect='siciliano')
    print('SIC :', Sic)
    #print('IN :', A)
    print('PARM:', Parm)

