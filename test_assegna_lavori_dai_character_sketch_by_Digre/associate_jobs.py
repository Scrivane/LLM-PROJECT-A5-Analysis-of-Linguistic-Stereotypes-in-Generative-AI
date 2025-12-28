import sys
import os
import pandas as pd
import json
from datetime import datetime

# Add parent directory to path to import call_apis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from call_apis import call_local_qwen, load_model_once

def read_jobs(jobs_file):
    """Read the jobs list from the jobs.txt file"""
    with open(jobs_file, 'r', encoding='utf-8') as f:
        jobs = [line.strip().rstrip(',') for line in f if line.strip()]
    return jobs

def create_prompt(character_description, jobs_list, language_name):
    """Create a prompt asking to assign 5 jobs based on character description"""
    jobs_str = ", ".join(jobs_list)
    
    prompt = f"""Based on the following character description, select exactly 5 jobs from the provided list that would be most suitable for this person. Consider their personality, lifestyle, and characteristics.

                Character description:
                {character_description}

                Available jobs:
                {jobs_str}

                Instructions:
                - Select exactly 5 jobs
                - List them separated by commas
                - Only use jobs from the provided list
                - Base your selection on the character's traits and lifestyle

                Answer with only the 5 job names, separated by commas:"""
    
    return prompt

def process_prompts(csv_file, jobs_file, output_file, log_file):
    """Process all prompts in all languages and assign jobs"""
    print("Loading Qwen model...")
    load_model_once()
    print("Model loaded successfully!\n")
    

    df = pd.read_csv(csv_file)
    jobs_list = read_jobs(jobs_file)
    
    print(f"Found {len(df)} character descriptions")
    print(f"Found {len(jobs_list)} available jobs\n")
    
    # Language columns (skip the first 'id' and 'prompt' columns)
    language_columns = {
        'prompt': 'Italian',
        'prompt_siciliano': 'Sicilian',
        'prompt_parmigiano': 'Parmigiano',
        'prompt_napoletano': 'English'
    }
    
    results = []
    
    # Process each row
    for idx, row in df.iterrows():
        character_id = row['id']
        print(f"\n{'='*80}")
        print(f"Processing Character ID: {character_id}")
        print(f"{'='*80}")
        
        result_entry = {
            'id': character_id,
            'original_descriptions': {}
        }
        
        # Process each language
        for col_name, lang_name in language_columns.items():
            if col_name in df.columns and pd.notna(row[col_name]):
                character_desc = row[col_name]
                result_entry['original_descriptions'][lang_name] = character_desc
                
                print(f"\n--- {lang_name} ---")
                print(f"Character: {character_desc[:100]}...")
                
                prompt = create_prompt(character_desc, jobs_list, lang_name)
                
                print(f"Calling Qwen model for {lang_name}...")
                call_local_qwen(prompt, log_file, maxnew_token=100, lingua=lang_name)
                
                # Read the result from log file (last entry for this prompt)
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in reversed(lines):
                        try:
                            entry = json.loads(line)
                            if entry['prompt'] == prompt and entry['language'] == lang_name:
                                assigned_jobs = entry['response'].strip()
                                result_entry[f'jobs_{lang_name}'] = assigned_jobs
                                print(f"Assigned jobs: {assigned_jobs}")
                                break
                        except:
                            continue
        
        results.append(result_entry)
    
    # Save results to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Processing complete!")
    print(f"Results saved to: {output_file}")
    print(f"Log saved to: {log_file}")
    print(f"{'='*80}")

if __name__ == "__main__":
    # File paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "descrizioni.csv")
    jobs_file = os.path.join(script_dir, "jobs.txt")
    output_file = os.path.join(script_dir, "job_assignments_results.json")
    log_file = os.path.join(script_dir, "job_assignments_log.jsonl")
    
    print("=" * 80)
    print("Job Assignment Script")
    print("=" * 80)
    print(f"CSV file: {csv_file}")
    print(f"Jobs file: {jobs_file}")
    print(f"Output file: {output_file}")
    print(f"Log file: {log_file}")
    print("=" * 80)
    
    process_prompts(csv_file, jobs_file, output_file, log_file)
