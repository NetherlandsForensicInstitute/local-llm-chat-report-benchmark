import os
import glob
import argparse
import requests
import json
import time
import csv
import re
import datetime

def summarize_file(file_path, api_url, model, stage1_prompt):
    with open(file_path, "r", encoding="utf-8") as f:
        user_content = f.read()

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": stage1_prompt},
            {"role": "user", "content": user_content}
        ],
        "max_tokens": -1,
        "stream": False
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    
    token_count = None
    if "usage" in data and "completion_tokens" in data["usage"]:
        token_count = data["usage"]["completion_tokens"]
    else:
        token_count = len(content.split())
        
    return content, token_count

def extract_think_block(text):
    match = re.match(r"\s*<think>(.*?)</think>\s*(.*)", text, re.DOTALL)
    if match:
        thoughts = match.group(1).strip()
        summary = match.group(2).lstrip()
        return thoughts, summary
    return None, text

def main():
    parser = argparse.ArgumentParser(description="Summarize split chat files using LM Studio REST API.")
    parser.add_argument(
        "--pattern",
        type=str,
        default="split_chatconversations/*_*.txt",
        help="Glob pattern for split files (default: 'split_chatconversations/*_*.txt')."
    )
    parser.add_argument("--api-url", type=str, default="http://localhost:1234/v1/chat/completions", help="LM Studio API URL.")
    args = parser.parse_args()

    prompt_path = os.path.join("prompts", "stage_1.md")
    with open(prompt_path, "r", encoding="utf-8") as pf:
        stage1_prompt = pf.read()

    files = sorted(glob.glob(args.pattern))
    if not files:
        print(f"No files found matching pattern: {args.pattern}")
        return

    models = ["google_gemma-3-12b-it-qat", "qwen3-14b", "phi-4-reasoning", "gpt-oss-20b", "google_gemma-3-27b-it-qat"]

    # === Stage 1: Individual Summaries ===
    stage1_dir = os.path.join("output", "stage-1")
    os.makedirs(stage1_dir, exist_ok=True)
    csv_path = os.path.join(stage1_dir, "stage-1_summary_stats.csv")
    write_header = not os.path.exists(csv_path)
    
    with open(csv_path, "a", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(["model", "input_file", "summary_file", "thoughts_file", "seconds", "tokens"])
        
        for model in models:
            print(f"\n=== Processing Stage 1 for model: {model} ===")
            model_folder = os.path.join(stage1_dir, model)
            os.makedirs(model_folder, exist_ok=True)
            
            for file_path in files:
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                summary_path = os.path.join(model_folder, f"{base_name}_summary.txt")
                thoughts_path = os.path.join(model_folder, f"{base_name}_thoughts.txt")

                # --- RECOVERY FEATURE FOR STAGE 1 ---
                if os.path.exists(summary_path):
                    print(f"Output file already exists, skipping: {summary_path}")
                    continue
                # --- END RECOVERY FEATURE ---

                print(f"Summarizing: {file_path}")
                t0 = time.time()
                try:
                    content, token_count = summarize_file(
                        file_path,
                        args.api_url,
                        model,
                        stage1_prompt
                    )
                    t1 = time.time()
                    seconds = round(t1 - t0, 2)
                    thoughts, summary = extract_think_block(content)
                    
                    with open(summary_path, "w", encoding="utf-8") as out_f:
                        out_f.write(summary)
                    
                    if thoughts:
                        with open(thoughts_path, "w", encoding="utf-8") as tf:
                            tf.write(thoughts)
                    else:
                        # Ensure thoughts_path is empty if no thoughts block is found
                        thoughts_path = ""
                    
                    print(f"Summary saved to: {summary_path} ({seconds}s)")
                    writer.writerow([model, file_path, summary_path, thoughts_path, seconds, token_count])
                    csvfile.flush()
                except Exception as e:
                    print(f"Error summarizing {file_path} with {model}: {e}")

    # === Stage 2: Investigative Report Generation ===
    print("\n\n=== Starting Stage 2: Final Report Generation ===")
    stage2_prompt_path = os.path.join("prompts", "stage_2.md")
    with open(stage2_prompt_path, "r", encoding="utf-8") as pf:
        stage2_prompt = pf.read()

    stage2_dir = os.path.join("output", "stage-2")
    os.makedirs(stage2_dir, exist_ok=True)
    csv_path2 = os.path.join(stage2_dir, "stage-2_report_stats.csv")
    write_header2 = not os.path.exists(csv_path2)

    with open(csv_path2, "a", newline='', encoding="utf-8") as csvfile2:
        writer2 = csv.writer(csvfile2)
        if write_header2:
            writer2.writerow(["model", "report_file", "thoughts_file", "tokens", "has_thoughts", "duration"])

        for model in models:
            print(f"\n--- Processing Stage 2 for model: {model} ---")
            
            # --- RECOVERY FEATURE FOR STAGE 2 ---
            report_pattern = os.path.join(stage2_dir, f"{model}_*_report.md")
            existing_reports = glob.glob(report_pattern)
            if existing_reports:
                print(f"Report for model '{model}' already exists, skipping. Found: {existing_reports[0]}")
                continue
            # --- END RECOVERY FEATURE ---

            model_folder = os.path.join(stage1_dir, model)
            summary_files = sorted(glob.glob(os.path.join(model_folder, "*_summary.txt")))
            
            if not summary_files:
                print(f"No summary files found for model '{model}'. Skipping report generation.")
                continue

            summaries_content = ""
            for sf in summary_files:
                with open(sf, "r", encoding="utf-8") as f:
                    summaries_content += f"--- START OF SUMMARY FROM {os.path.basename(sf)} ---\n"
                    summaries_content += f.read().strip() + "\n--- END OF SUMMARY ---\n\n"

            payload2 = {
                "model": model,
                "messages": [
                    {"role": "system", "content": stage2_prompt},
                    {"role": "user", "content": summaries_content}
                ],
                "max_tokens": -1,
                "stream": False
            }

            headers = {"Content-Type": "application/json"}
            print("Generating final report...")
            try:
                t0 = time.time()
                response2 = requests.post(args.api_url, headers=headers, data=json.dumps(payload2))
                response2.raise_for_status()
                data2 = response2.json()
                content2 = data2["choices"][0]["message"]["content"]
                t1 = time.time()
                duration = t1 - t0
                duration_str = time.strftime('%H:%M:%S', time.gmtime(duration))

                thoughts2, report2 = extract_think_block(content2)

                now = datetime.datetime.now().strftime("%Y%m%d%H%M")
                base_report_name = f"{model}_{now}_report"
                report_path = os.path.join(stage2_dir, f"{base_report_name}.md")
                thoughts_path2 = ""
                has_thoughts = "no"
                
                with open(report_path, "w", encoding="utf-8") as rf:
                    rf.write(report2)
                
                if thoughts2:
                    thoughts_path2 = os.path.join(stage2_dir, f"{base_report_name}_thoughts.md")
                    with open(thoughts_path2, "w", encoding="utf-8") as tf:
                        tf.write(thoughts2)
                    has_thoughts = "yes"

                if "usage" in data2 and "completion_tokens" in data2["usage"]:
                    token_count2 = data2["usage"]["completion_tokens"]
                else:
                    token_count2 = len(content2.split())

                writer2.writerow([model, report_path, thoughts_path2, token_count2, has_thoughts, duration_str])
                csvfile2.flush()
                print(f"Stage 2 report saved to: {report_path} ({duration_str})")
                
            except Exception as e:
                print(f"Error generating Stage 2 report for {model}: {e}")

if __name__ == "__main__":
    main()