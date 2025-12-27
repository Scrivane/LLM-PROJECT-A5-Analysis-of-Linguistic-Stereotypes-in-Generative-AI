import csv
from translation.translate import translate

INPUT_CSV = "test_multiple_napoli/output_with_translations.csv"
OUTPUT_CSV = "all_dialects_traslated.csv"

def main():
    with open(INPUT_CSV, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["Parmigiano", "Siciliano"]

        rows = []
        for row in reader:
            italiano = row["Automated Translation"]

            row["Parmigiano"] = translate(italiano, dialect="parmigiano")
            row["Siciliano"] = translate(italiano, dialect="siciliano")

            rows.append(row)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    main()
