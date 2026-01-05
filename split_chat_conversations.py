import re
import argparse
from transformers import AutoTokenizer
from huggingface_hub import login
import os
from dotenv import load_dotenv
import csv
from collections import namedtuple, Counter

# Load environment variables from .env file
load_dotenv()
hf_token = os.getenv("HF_TOKEN")
if hf_token:
    login(token=hf_token)
else:
    print("Hugging Face token not found in .env file.")

# A simple structure to hold conversation data
Conversation = namedtuple('Conversation', ['text', 'tokens', 'header', 'device_name'])

def extract_device_header_and_name_from_conv(conv_text):
    """
    Extracts the device header line and device name from a conversation block.
    Returns (header_line, device_name) or (None, None).
    """
    match = re.search(r"^(Conversations found on device ([^(]+)\(.*\))$", conv_text, re.MULTILINE)
    if match:
        header_line = match.group(1).strip()
        device_name = match.group(2).strip()
        return header_line, device_name
    return None, None

def split_conversations_by_token_limit(text, tokenizer, max_tokens, base_filename, cli_device_name):
    # Split the entire text by device first
    device_chunks = re.split(r'\n(?=Conversations found on device)', text.strip())
    
    print("\n--- Scanning conversations and devices ---")
    processed_conversations = []
    last_seen_header = None
    last_seen_device = cli_device_name

    for device_chunk in device_chunks:
        if not device_chunk.strip():
            continue

        header_match = re.search(r"^(Conversations found on device ([^(]+)\(.*\))", device_chunk, re.MULTILINE)
        if header_match:
            last_seen_header = header_match.group(1).strip()
            last_seen_device = header_match.group(2).strip()
            content_after_header = device_chunk[header_match.end(0):].strip()
            print(f">>> Encountered new device: '{last_seen_device}'")
        else:
            content_after_header = device_chunk.strip()

        conversation_platforms = ["WhatsApp", "Telegram", "Snapchat", "Native Messages", "Instagram", "TikTok", "Signal"]
        platform_pattern = "|".join(conversation_platforms)
        split_pattern = fr'\n(?=(?:{platform_pattern}) conversation about)'
        
        individual_convs = [conv for conv in re.split(split_pattern, content_after_header) if conv.strip()]
        
        print(f"... Found {len(individual_convs)} conversations for device '{last_seen_device}'")

        for conv_text in individual_convs:
            tokens = len(tokenizer.encode(conv_text))
            processed_conversations.append(Conversation(conv_text, tokens, last_seen_header, last_seen_device))

    print("--- Scan complete ---")
    
    if not processed_conversations:
        return [], [], [], [], [], []

    chunks = []
    current_chunk_convs = []
    current_chunk_tokens = 0
    
    for conv in processed_conversations:
        if current_chunk_convs and (current_chunk_tokens + conv.tokens > max_tokens):
            chunks.append(list(current_chunk_convs))
            current_chunk_convs = [conv]
            current_chunk_tokens = conv.tokens
        else:
            current_chunk_convs.append(conv)
            current_chunk_tokens += conv.tokens
            
    if current_chunk_convs:
        chunks.append(list(current_chunk_convs))

    output_files, file_token_counts, chunk_devices, chunk_conv_counts, chunk_device_reports = [], [], [], [], []

    print(f"\n--- Preparing to create {len(chunks)} files ---")

    for idx, chunk_convs in enumerate(chunks, 1):
        # **CHANGE HERE:** Use :02d for zero-padded two-digit numbering
        out_path = f"{os.path.splitext(base_filename)[0]}_{idx:02d}.txt"
        print(f"--- Creating new file: {out_path} ---")
        
        header_for_file = chunk_convs[0].header
        primary_device_for_file = chunk_convs[0].device_name
        
        chunk_content = '\n\n'.join([c.text for c in chunk_convs])
        
        final_content_for_file = chunk_content
        if header_for_file and not chunk_content.strip().startswith(header_for_file):
            final_content_for_file = f"{header_for_file}\n\n{chunk_content}"

        chunk_token_count = len(tokenizer.encode(final_content_for_file))

        if len(chunk_convs) == 1 and chunk_token_count > max_tokens:
             print(f"  [WARNING] File '{out_path}' exceeds token limit because it contains a single large conversation block ({chunk_token_count} tokens).")

        device_counts = Counter(conv.device_name for conv in chunk_convs)
        report_parts = [f"'{device}' ({count} convos)" for device, count in device_counts.items()]
        device_report_str = ", ".join(report_parts)
        
        output_files.append(out_path)
        file_token_counts.append(chunk_token_count)
        chunk_devices.append(primary_device_for_file)
        chunk_conv_counts.append(len(chunk_convs))
        chunk_device_reports.append(device_report_str)

        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write(final_content_for_file)
            
    return output_files, file_token_counts, chunk_devices, chunk_conv_counts, chunk_device_reports


def main():
    parser = argparse.ArgumentParser(description="Estimate or split chat conversations by token count.")
    parser.add_argument("--split", action="store_true", help="Split the chat file into multiple files with at most 32k tokens each.")
    parser.add_argument("--count-tokens", action="store_true", help="Count tokens and words in the chat file.")
    parser.add_argument("--file", type=str, required=True, help="Input chat file path.")
    parser.add_argument("--device", type=str, default="Unknown Device", help="Default device name if not found in file.")
    parser.add_argument("--max-tokens", type=int, default=32000, help="Maximum number of tokens per file.")
    args = parser.parse_args()

    file_path = args.file
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    if args.split:
        print(f"Splitting file by {args.max_tokens} tokens per file...")
        
        conversation_platforms = ["WhatsApp", "Telegram", "Snapchat", "Native Messages", "Instagram", "TikTok", "Signal"]
        platform_pattern = "|".join(conversation_platforms)
        split_pattern = fr'(?:{platform_pattern}) conversation about'
        total_conversation_count = len(re.findall(split_pattern, text))
        print(f"\nVerification: Found a total of {total_conversation_count} conversations in the input file (matching 'conversation about').")

        gemma_model = "google/gemma-2b-it" 
        try:
            tokenizer = AutoTokenizer.from_pretrained(gemma_model)
        except Exception as e:
            print(f"Could not load tokenizer. Please check model name or network connection. Error: {e}")
            return
            
        output_files, file_token_counts, chunk_devices, chunk_conv_counts, chunk_device_reports = split_conversations_by_token_limit(
            text, tokenizer, args.max_tokens, file_path, args.device
        )
        
        if not output_files:
            print("No conversations found or file is empty. No files were created.")
            return

        print(f"\n--- Splitting complete: Summary ---")
        for f, conv_count, tcount, report_str in zip(output_files, chunk_conv_counts, file_token_counts, chunk_device_reports):
            print(f"- {f} | conversations: {conv_count:<3} | tokens: {tcount:<5} | Contains: {report_str}")

        csv_path = f"{os.path.splitext(file_path)[0]}_split_token_count.csv"
        with open(csv_path, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["filename", "conversations", "tokens", "primary_device", "device_breakdown"])
            for f, conv_count, tcount, device_name, report_str in zip(output_files, chunk_conv_counts, file_token_counts, chunk_devices, chunk_device_reports):
                writer.writerow([f, conv_count, tcount, device_name, report_str])
            
            writer.writerow([])
            total_split_convs = sum(chunk_conv_counts)
            total_split_tokens = sum(file_token_counts)
            writer.writerow(["TOTAL (from split files)", total_split_convs, total_split_tokens, "", ""])
            writer.writerow(["VERIFICATION (from original file)", total_conversation_count, "", "", ""])

        print(f"\nFull breakdown saved to: {csv_path}")
        return

    if args.count_tokens:
        word_count = len(re.findall(r"\w+", text, re.UNICODE))
        print(f"Word count: {word_count}")

        models = {
            "Llama 3.1 8B DeepSeek": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
            "Gemma 3 12B": "google/gemma-3-12b-it",
            "Gemma 3 27B": "google/gemma-3-27b-it",
            "Phi-4 Reasoning": "microsoft/Phi-4-reasoning",
            "GPT-OSS:20B": "openai/gpt-oss-20b"
        }

        for model_label, model_id in models.items():
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_id)
                model_token_count = len(tokenizer.encode(text))
                print(f"{model_label} token count (official tokenizer): {model_token_count}")
            except Exception as e:
                print(f"Could not compute tokens for {model_id}: {e}")
        return


if __name__ == "__main__":
    main()