import sys
import os
import argparse
import pandas as pd
import json
from datetime import datetime
from collections import Counter
from pathlib import Path

# Add parent directory to path to import call_apis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from call_apis import call_api_gpt_by_gio

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
                - Job must be unique and not repeated
                - List them separated by commas
                - Only use jobs from the provided list
                - Base your selection on the character's traits and lifestyle
                - The output must be only the list of job names, nothing else

                Answer with only the 5 job names, separated by commas:"""
    
    return prompt

def process_prompts(csv_file, jobs_file, output_file, log_file, num_runs=1, run_number=1):
    """Process all prompts in all languages and assign jobs"""
    #print("Loading Qwen model...")
    #load_model_once()
    #print("Model loaded successfully!\n")
    

    df = pd.read_csv(csv_file)
    jobs_list = read_jobs(jobs_file)
    
    print(f"\n{'='*80}")
    print(f"Run {run_number} of {num_runs}")
    print(f"{'='*80}")
    print(f"Found {len(df)} character descriptions")
    print(f"Found {len(jobs_list)} available jobs\n")
    
    # Language columns (skip the first 'id' and 'prompt' columns)
    language_columns = {
        'prompt': 'Italian',
        'prompt_siciliano': 'Sicilian',
        'prompt_parmigiano': 'Parmigiano',
        'prompt_napoletano': 'Napoletano'
    }
    
    results = []
    
    # Process each row
    for idx, row in df.iterrows():
        character_id = row['id']
        print(f"\n{'='*80}")
        print(f"Processing Character ID: {character_id} (Run {run_number}/{num_runs})")
        print(f"{'='*80}")
        
        result_entry = {
            'id': character_id,
            'run': run_number,
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
                
                print(f"Calling LLAMA model for {lang_name}...")
                Path(log_file).touch(exist_ok=True)
                call_api_gpt_by_gio(prompt, log_file, lingua=lang_name)

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
    
    return results


def aggregate_results(all_results, num_runs, language_order=None):
    """Aggregate job frequencies per character and language."""
    if language_order is None:
        language_order = ['Italian', 'Sicilian', 'Parmigiano', 'Napoletano']

    aggregated = {}
    char_ids = {str(result['id']) for result in all_results}
    for char_id in char_ids:
        aggregated[char_id] = {lang: Counter() for lang in language_order}

    for result in all_results:
        char_id = str(result['id'])
        for lang in language_order:
            key = f'jobs_{lang}'
            if key in result:
                jobs = [j.strip() for j in result[key].split(',')]
                aggregated[char_id][lang].update(jobs)

    aggregated_final = {}
    for char_id, langs in aggregated.items():
        aggregated_final[char_id] = {}
        for lang, counter in langs.items():
            aggregated_final[char_id][lang] = dict(counter.most_common())

    summary_lines = []
    summary_lines.append("=" * 80)
    summary_lines.append("Job Assignment - Multiple Runs Summary Report")
    summary_lines.append("=" * 80 + "\n")
    summary_lines.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append(f"Number of runs: {num_runs}")
    summary_lines.append(f"Characters processed: {len(aggregated_final)}")
    summary_lines.append(f"Total results collected: {len(all_results)}\n")
    summary_lines.append("=" * 80)
    summary_lines.append("Job Frequency Distribution by Character and Language")
    summary_lines.append("=" * 80 + "\n")

    for char_id in sorted(aggregated_final.keys(), key=lambda x: int(x) if str(x).isdigit() else str(x)):
        summary_lines.append(f"\nCharacter ID: {char_id}")
        summary_lines.append("-" * 80)
        for lang in language_order:
            jobs_freq = aggregated_final[char_id][lang]
            if jobs_freq:
                summary_lines.append(f"  {lang}:")
                for job, count in sorted(jobs_freq.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / num_runs) * 100 if num_runs else 0
                    summary_lines.append(f"    - {job}: {count}/{num_runs} ({percentage:.1f}%)")
            else:
                summary_lines.append(f"  {lang}: No data")

    summary_text = "\n".join(summary_lines) + "\n"
    return aggregated_final, summary_text


def aggregate_from_results_file(results_path, aggregated_path=None, summary_path=None, num_runs=50, language_order=None):
    """Aggregate directly from an existing job_assignments_results.json without rerunning prompts."""
    if language_order is None:
        language_order = ['Italian', 'Sicilian', 'Parmigiano', 'Napoletano']

    with open(results_path, 'r', encoding='utf-8') as f:
        all_results = json.load(f)

    aggregated_final, summary_text = aggregate_results(all_results, num_runs, language_order)

    if aggregated_path:
        with open(aggregated_path, 'w', encoding='utf-8') as f:
            json.dump(aggregated_final, f, ensure_ascii=False, indent=2)

    if summary_path:
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)

    return aggregated_final

if __name__ == "__main__":
    # File paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "descrizioni.csv")
    jobs_file = os.path.join(script_dir, "jobs.txt")
    
    # Number of runs (change this to 100 or any other number)
    NUM_RUNS = 50
    
    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join(script_dir, f"results_{NUM_RUNS}_runs_{timestamp}")
    os.makedirs(results_dir, exist_ok=True)
    
    output_file = os.path.join(results_dir, "job_assignments_results.json")
    log_file = os.path.join(results_dir, "job_assignments_log.jsonl")
    aggregated_file = os.path.join(results_dir, "aggregated_results.json")
    summary_file = os.path.join(results_dir, "summary.txt")
    
    print("=" * 80)
    print("Job Assignment Script - Multiple Runs")
    print("=" * 80)
    print(f"CSV file: {csv_file}")
    print(f"Jobs file: {jobs_file}")
    print(f"Results directory: {results_dir}")
    print(f"Number of runs: {NUM_RUNS}")
    print("=" * 80)
    
    all_results = []
    
    # Run the process NUM_RUNS times
    for run_num in range(1, NUM_RUNS + 1):
        results = process_prompts(csv_file, jobs_file, output_file, log_file, NUM_RUNS, run_num)
        all_results.extend(results)
    
    # Save all results to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    # Aggregate results by counting job frequencies for each character
    aggregated = {}
    df_check = pd.read_csv(csv_file)
    
    for char_id in df_check['id'].unique():
        char_key = str(char_id)
        aggregated[char_key] = {
            'Italian': Counter(),
            'Sicilian': Counter(),
            'Parmigiano': Counter(),
            'Napoletano': Counter()
        }
    
    # Count job occurrences
    for result in all_results:
        char_id = str(result['id'])
        for lang in ['Italian', 'Sicilian', 'Parmigiano', 'Napoletano']:
            key = f'jobs_{lang}'
            if key in result:
                jobs = [j.strip() for j in result[key].split(',')]
                aggregated[char_id][lang].update(jobs)
    
    # Convert Counters to dictionaries sorted by frequency
    aggregated_final = {}
    for char_id, langs in aggregated.items():
        aggregated_final[char_id] = {}
        for lang, counter in langs.items():
            aggregated_final[char_id][lang] = dict(counter.most_common())
    
    # Save aggregated results
    with open(aggregated_file, 'w', encoding='utf-8') as f:
        json.dump(aggregated_final, f, ensure_ascii=False, indent=2)
    
    # Create summary report
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("Job Assignment - Multiple Runs Summary Report\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Number of runs: {NUM_RUNS}\n")
        f.write(f"Characters processed: {len(aggregated_final)}\n")
        f.write(f"Total results collected: {len(all_results)}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("Job Frequency Distribution by Character and Language\n")
        f.write("=" * 80 + "\n\n")
        
        for char_id in sorted(aggregated_final.keys()):
            f.write(f"\nCharacter ID: {char_id}\n")
            f.write("-" * 80 + "\n")
            for lang in ['Italian', 'Sicilian', 'Parmigiano', 'Napoletano']:
                jobs_freq = aggregated_final[char_id][lang]
                if jobs_freq:
                    f.write(f"  {lang}:\n")
                    for job, count in sorted(jobs_freq.items(), key=lambda x: x[1], reverse=True):
                        percentage = (count / NUM_RUNS) * 100
                        f.write(f"    - {job}: {count}/{NUM_RUNS} ({percentage:.1f}%)\n")
                else:
                    f.write(f"  {lang}: No data\n")
    
    print(f"\n{'='*80}")
    print(f"Processing complete!")
    print(f"Results directory: {results_dir}")
    print(f"All results saved to: {output_file}")
    print(f"Aggregated results saved to: {aggregated_file}")
    print(f"Summary report saved to: {summary_file}")
    print(f"Log saved to: {log_file}")
    print(f"{'='*80}")
