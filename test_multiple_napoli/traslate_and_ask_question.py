import csv

def read_translations_file(translation_file_path):
    """Read translations from a text file (one per line)"""
    translations = []
    try:
        with open(translation_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:  # Skip empty lines
                    translations.append(line)
        return translations
    except FileNotFoundError:
        print(f"Error: File '{translation_file_path}' not found.")
        return None

def read_csv_and_add_translations(csv_file_path, translations):
    """Read CSV file and add translations as a new field"""
    data = []
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for idx, row in enumerate(reader):
                row['Automated Translation'] = translations[idx] if idx < len(translations) else ""
                data.append(row)
        return data
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found.")
        return None

def save_csv_with_translations(output_file_path, data):
    """Save the enriched data to a new CSV file"""
    if not data:
        return
    
    # Define fieldnames - keep original plus add new field
    fieldnames = ['File Name', 'Domain', 'Neapolitan Text', 'Automated Translation']
    
    try:
        with open(output_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"✓ File saved to {output_file_path}")
    except IOError as e:
        print(f"Error writing file: {e}")

def main():
    # File paths
    csv_file = "transcripts.csv"  # Replace with your CSV file
    translations_file = "trad.csv"  # File with line-by-line translations
    output_file = "output_with_translations.csv"  # Output file
    
    # Read translations
    print(f"Reading translations from {translations_file}...")
    translations = read_translations_file(translations_file)
    if not translations:
        return
    print(f"✓ Loaded {len(translations)} translations\n")
    
    # Read CSV and add translations
    print(f"Reading CSV from {csv_file}...")
    data = read_csv_and_add_translations(csv_file, translations)
    if not data:
        return
    print(f"✓ Loaded {len(data)} rows\n")
    
    # Check if counts match
    if len(data) != len(translations):
        print(f"⚠ Warning: CSV has {len(data)} rows but {len(translations)} translations provided")
    
    # Save enriched CSV
    print(f"Saving to {output_file}...")
    save_csv_with_translations(output_file, data)
    
    # Display preview
    print("\nPreview of first row:")
    if data:
        for key, value in data[0].items():
            print(f"  {key}: {value}")


            

if __name__ == "__main__":
    main()