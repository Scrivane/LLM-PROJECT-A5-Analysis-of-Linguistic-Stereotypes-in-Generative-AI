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




"""
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
"""