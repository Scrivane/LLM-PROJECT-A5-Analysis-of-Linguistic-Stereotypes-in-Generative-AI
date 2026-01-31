from datetime import time
import json
from pathlib import Path
import random
import sys

from mistralai import Mistral
from collections import OrderedDict

workspace_root = Path(__file__).resolve().parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))
from translation.translate import translate
import call_apis
import csv


api_key_google="placeholder"
groq_token="placeholder"
api_key_minstral="placeholder"


def convert_prompt_silvia_to_csv(input_path: str = "translation/prompt_criminality.md", output_path: str = "translation/prompt_Silvia.csv") -> int:

    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    prompts = []
    current_lines = []

    with p.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if stripped.startswith("```"):
                continue
            if stripped.startswith("## "):
                # store previous prompt
                if current_lines:
                    text = " ".join([l.strip() for l in current_lines]).strip()
                    if text:
                        prompts.append(text)
                current_lines = []
            else:
                if line.strip() != "":
                    current_lines.append(line)

    # append last
    if current_lines:
        text = " ".join([l.strip() for l in current_lines]).strip()
        if text:
            prompts.append(text)

    outp = Path(output_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", encoding="utf-8", newline="") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(["prompt"])
        for t in prompts:
            writer.writerow([t])

    return len(prompts)


def expand_prompts_with_dialects(input_csv: str = "prompt_criminality.csv", output_csv: str = "prompt_criminality_expanded.csv") -> int:

    inp = Path(input_csv)
    if not inp.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    # read prompts 
    prompts = []
    with inp.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        start = 0
        if rows and len(rows[0]) == 1 and rows[0][0].strip().lower() == "prompt":   #header
            start = 1
        for r in rows[start:]:
            if not r:
                continue
            text = r[0].strip()
            if text:
                prompts.append(text)

    outp = Path(output_csv)
    outp.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with outp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for prompt in prompts:
            try:
                sic = translate(prompt, dialect="siciliano")
            except Exception as e:
                sic = f"<translation_error: {e}>"
            writer.writerow([prompt, sic, "siciliano"])
            written += 1

            try:
                parm = translate(prompt, dialect="parmigiano")
            except Exception as e:
                parm = f"<translation_error: {e}>"
            writer.writerow([prompt, parm, "parmigiano"])
            written += 1

    return written


def group_expanded_prompts(expanded_csv: str = "prompt_criminality_expanded.csv", output_csv: str | None = None) -> int:

    inp = Path(expanded_csv)
    if not inp.exists():
        raise FileNotFoundError(f"Expanded CSV not found: {expanded_csv}")

    rows = []
    with inp.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for r in reader:
            if not r:
                continue
            # ensure row has 3 columns
            if len(r) < 3:
                continue
            italian = r[0].strip()
            dialect_prompt = r[1].strip()
            dialect_name = r[2].strip().lower()
            rows.append((italian, dialect_prompt, dialect_name))

    # preserve original order of Italian prompts
    grouped: dict[str, dict[str, str]] = OrderedDict()
    order_of_dialects: dict[str, list[str]] = {}
    for italian, dprompt, dname in rows:
        if italian not in grouped:
            grouped[italian] = {}
            order_of_dialects[italian] = []
        grouped[italian][dname] = dprompt
        if dname not in order_of_dialects[italian]:
            order_of_dialects[italian].append(dname)

    # desired order
    preferred = ["siciliano", "parmigiano", "napoletano"]

    out_path = Path(output_csv) if output_csv else inp.with_suffix('.tmp')

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        written = 0
        for italian, dmap in grouped.items():
            # write preferred dialects first if present
            for d in preferred:
                if d in dmap:
                    writer.writerow([italian, dmap[d], d])
                    written += 1
            # write any other dialects in original  order
            for d in order_of_dialects[italian]:
                if d in preferred:
                    continue
                writer.writerow([italian, dmap[d], d])
                written += 1


    if output_csv is None:
        tmp = out_path
        inp.unlink()
        tmp.rename(inp)

    return written


def analyze_results(input_json):
    with open(input_json, 'r', encoding='utf-8') as f:
        count_a = 0
        count_b = 0
        total = 0
        count_per_dialect = {
            "siciliano": {"total": 0, "persona_a": 0, "persona_b": 0},
            "parmigiano": {"total": 0, "persona_a": 0, "persona_b": 0},
            "napoletano": {"total": 0, "persona_a": 0, "persona_b": 0},
        }
        for line_number, line in enumerate(f):
            # Skip header
            if line_number == 0:
                continue
            line = line.strip()
            if not line:
                continue

            data = json.loads(line)
            response = data.get("response", "").strip().upper()
            dialetto = data.get("language", "").strip().lower()

            if response == "PERSONA A":
                count_a += 1
                total += 1
                count_per_dialect[dialetto]["persona_a"] += 1
                count_per_dialect[dialetto]["total"] += 1
            elif response == "PERSONA B":
                count_b += 1
                total += 1
                count_per_dialect[dialetto]["persona_b"] += 1
                count_per_dialect[dialetto]["total"] += 1

    print(f"CUMULATIVE results - total responses: {total}")
    print(f"    PERSONA A: {count_a} ({(count_a / total * 100) if total > 0 else 0:.2f}%)")
    print(f"    PERSONA B: {count_b} ({(count_b / total * 100) if total > 0 else 0:.2f}%)")
    for dialetto, counts in count_per_dialect.items():
        d_total = counts["total"]
        d_a = counts["persona_a"]
        d_b = counts["persona_b"]
        print(f"Risultati {dialetto} - total responses: {d_total}")
        print(f"    PERSONA A: {d_a} ({(d_a / d_total * 100) if d_total > 0 else 0:.2f}%)")
        print(f"    PERSONA B: {d_b} ({(d_b / d_total * 100) if d_total > 0 else 0:.2f}%)")
    return total, count_a, count_b
    
