import csv
import os
import re
from typing import Dict, List, Optional


def build_mapping_from_tsv(tsv_path: str) -> Dict[str, List[str]]:
    """Build a mapping Italian -> list of Sicilian lemmas from the TSV file.

    The TSV uses columns: ENTRATA (sicilian entry), traduzione1..traduzione9 (italian translations),
    and variant1..variantN (alternate sicilian forms). We invert translations to map Italian -> Sicilian.
    """
    mapping: Dict[str, List[str]] = {}
    if not os.path.isfile(tsv_path):
        raise FileNotFoundError(f"TSV file not found: {tsv_path}")

    with open(tsv_path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        # collect translation and variant column names dynamically
        trad_cols = [c for c in reader.fieldnames or [] if c.startswith("traduzione")]
        variant_cols = [c for c in reader.fieldnames or [] if c.startswith("variant")]

        for row in reader:
            sic_entry = (row.get("ENTRATA") or "").strip()
            if not sic_entry:
                continue
            # collect possible sicilian forms: main entry + variants
            sic_forms = [sic_entry]
            for vc in variant_cols:
                v = (row.get(vc) or "").strip()
                if v:
                    # some variant cells may contain multiple alternatives separated by ',' or ';'
                    for part in re.split(r"[;,/]", v):
                        p = part.strip()
                        if p and p not in sic_forms:
                            sic_forms.append(p)

            for tc in trad_cols:
                it = (row.get(tc) or "").strip()
                if not it:
                    continue
                # some italian translation cells may hold multiple alternatives separated by ',' or ';'
                for part in re.split(r"[;,/]", it):
                    it_norm = part.strip().lower()
                    if not it_norm:
                        continue
                    mapping.setdefault(it_norm, [])
                    for f in sic_forms:
                        if f not in mapping[it_norm]:
                            mapping[it_norm].append(f)

    return mapping


def try_parse_ttl_for_mappings(ttl_path: str) -> Dict[str, List[str]]:
    """Try to extract Italian->Sicilian mappings from a TTL glossary.

    This function attempts to use rdflib if available. If rdflib is not installed,
    it falls back to a lightweight heuristic (scanning for ""@it"" strings).

    The TTL format used in the project may contain vartrans links; an accurate parse
    requires rdflib. The heuristic here will only add simple direct matches found
    as Italian written forms ("..."@it) and map them to nothing unless rdflib can
    resolve links; thus it's optional and best-effort.
    """
    extra: Dict[str, List[str]] = {}
    if not os.path.isfile(ttl_path):
        return extra

    try:
        from rdflib import Graph, URIRef
        from rdflib.namespace import RDF

        g = Graph()
        g.parse(ttl_path, format="turtle")

        # Look for vartrans relations: vartrans:source -> italian entry, vartrans:target -> sicilian entry
        # We try a simple SPARQL-like approach using triples lookup.
        from rdflib.namespace import Namespace
        VAR = Namespace("http://www.w3.org/ns/lemon/vartrans#")
        ONTO = Namespace("http://www.w3.org/ns/lemon/ontolex#")

        # Build a map of lexical entry -> canonical writtenRep and language tag
        written = {}
        for lex in g.subjects(RDF.type, ONTO.LexicalEntry):
            for wf in g.objects(lex, ONTO.canonicalForm):
                for wr in g.objects(wf, ONTO.writtenRep):
                    sval = str(wr)
                    # language tag might be lost; we'll keep the string
                    written.setdefault(lex, []).append(sval)

        # Now look for vartrans triples linking entries
        for vt in g.subjects(RDF.type, VAR.Translation):
            src = next(g.objects(vt, VAR.source), None)
            tgt = next(g.objects(vt, VAR.target), None)
            if src and tgt and src in written and tgt in written:
                # try to determine which is italian and which is sicilian by language tag in string
                for sform in written[src]:
                    for tform in written[tgt]:
                        # naive detection: if sform contains '@it' or 'italian' substring, treat as italian
                        s_norm = sform.lower()
                        t_norm = tform
                        # strip language tag if present
                        s_norm = re.sub(r'"?@it$','', s_norm)
                        s_norm = s_norm.strip('"')
                        if s_norm:
                            extra.setdefault(s_norm, [])
                            if t_norm not in extra[s_norm]:
                                extra[s_norm].append(t_norm)

    except Exception:
        # fallback heuristic: extract all "..."@it occurrences and add as keys with empty values
        with open(ttl_path, encoding='utf-8') as fh:
            data = fh.read()
        for m in re.findall(r'"([^\"]+)"@it', data, flags=re.IGNORECASE):
            k = m.strip().lower()
            if k and k not in extra:
                extra[k] = []

    return extra


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
        base = os.path.join(os.path.dirname(__file__), '..', 'rdf', 'source', 'siciliano.tsv')
        tsv_path = os.path.normpath(base)

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


if __name__ == '__main__':
    # quick demonstration using the workspace TSV path relative to this file
    script_dir = os.path.dirname(__file__)
    default_tsv = os.path.normpath(os.path.join(script_dir, '..', 'rdf', 'source', 'siciliano.tsv'))
    sample = "Io lavoro in un azienda che si occupa di costruzioni e appalti, la mia azienda fattura molti soldi grazie agli appalti statali "
    try:
        out = translate_it_to_sicilian(sample, tsv_path=default_tsv)
        print('IN :', sample)
        print('OUT:', out)
    except FileNotFoundError as e:
        print('TSV not found, please point to the file path:', e)
