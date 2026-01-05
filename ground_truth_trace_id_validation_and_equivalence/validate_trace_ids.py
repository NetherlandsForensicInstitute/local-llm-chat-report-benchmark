import os
import csv
import re

def validate_trace_ids():
    """
    Validates the presence of trace IDs from Markdown tables within a chat conversation file,
    extracts metadata, and generates a CSV report and console output.
    """

    # --- Data Source (from Markdown tables) ---

    # Table 1: Ground Truth Trace IDs
    ground_truth_data = {
        1: "Antonio Gotta informs Nerijus Bos about a deal with the UK that requires a lab inspection.",
        2: "Nerijus Bos instructs Quan Xiuan that Joseph Prinse will pick him up on July 21.",
        3: "Rosie Boudica advises Nerijus Bos to use freight routes instead of mules for transporting goods.",
        4: "Antonio Gotta informs Nerijus Bos that drugs delivered to Ibiza will be paid for in Bitcoins.",
        5: "Figo Johnson gives Quan Xiuan instructions for the drug transfer, including buying a suitcase and taking photos of the drugs and lab.",
        6: "Nerijus Bos instructs Joseph Prinse to pick up Quan at the airport on July 21st and provides an address in IJmuiden.",
        7: "Nerijus Bos confirms to Antonio Gotta that a payment has been received and they can proceed with a delivery.",
        8: "Rosie Boudica provides bank account details for \"Rosie Fashion\" to Nerijus Bos for a transfer.",
        9: "Liss informs Joseph Prinse that she was stopped by authorities near the depot while driving his car.",
        10: "Rosie Boudica reports to Nerijus Bos that Liss was seen in one of Joseph's cars at the depot, causing issues.",
        11: "Liss threatens to go to the police with evidence of Joseph Prinse's \"business\" if he doesn't sign divorce papers.",
        12: "Joseph Prinse tells Nerijus Bos that \"Lizz knows too much.\"",
        13: "Nerijus Bos sends a threatening message to Liss, warning her not to contact the police.",
        14: "Quan Xiuan messages Joseph Prinse that he has landed at the airport."
    }

    # Table 2: Trace ID Equivalence Map
    trace_id_map = [
        {'Ref #': 1, 'Equivalent Trace ID': '6c5099cb-f06f-40ca-8051-57f392137ed4:0-0-0-1-0-1-2-86-2-3-0', 'Is_Ground_Truth_ID': 'Yes'},
        {'Ref #': 1, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-7-1a', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 1, 'Equivalent Trace ID': '6c5099cb-f06f-40ca-8051-57f392137ed4:0-0-0-4-1', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 2, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-1-0-0-0-2-1-1-0-24-a-6', 'Is_Ground_Truth_ID': 'Yes'},
        {'Ref #': 2, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-7-6', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 2, 'Equivalent Trace ID': '34e8c539-94b9-41bc-95df-fec503e31153:0-0-0-1-0-2-0-8-2-6-2ea', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 2, 'Equivalent Trace ID': '34e8c539-94b9-41bc-95df-fec503e31153:0-0-0-1-0-2-7-0-0-1-0-0-8e', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 2, 'Equivalent Trace ID': '34e8c539-94b9-41bc-95df-fec503e31153:0-0-0-4-4f', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 3, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-1-0-0-0-2-1-1-0-24-a-3', 'Is_Ground_Truth_ID': 'Yes'},
        {'Ref #': 3, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-7-3', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 3, 'Equivalent Trace ID': '2fbd9c9e-e242-46cb-910f-64c7c314b310:0-0-0-1-0-0-2-9-1-7-1a', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 3, 'Equivalent Trace ID': '2fbd9c9e-e242-46cb-910f-64c7c314b310:0-0-0-6-92', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 4, 'Equivalent Trace ID': '6c5099cb-f06f-40ca-8051-57f392137ed4:0-0-0-1-0-1-2-86-2-3-0', 'Is_Ground_Truth_ID': 'Yes'},
        {'Ref #': 4, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-7-1a', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 4, 'Equivalent Trace ID': '6c5099cb-f06f-40ca-8051-57f392137ed4:0-0-0-4-1', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 5, 'Equivalent Trace ID': 'a0518702-3584-4b83-a97e-de437493e4de:0-0-0-1-0-0-0-1-1-1-0-19-a-1', 'Is_Ground_Truth_ID': 'Yes'},
        {'Ref #': 5, 'Equivalent Trace ID': '34e8c539-94b9-41bc-95df-fec503e31153:0-0-0-1-0-2-0-8-2-6-2e4', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 5, 'Equivalent Trace ID': '34e8c539-94b9-41bc-95df-fec503e31153:0-0-0-4-3d', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 5, 'Equivalent Trace ID': 'a0518702-3584-4b83-a97e-de437493e4de:0-0-0-6-c', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 6, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-1-0-0-0-2-1-1-0-24-a-7', 'Is_Ground_Truth_ID': 'Yes'},
        {'Ref #': 6, 'Equivalent Trace ID': '9f4a2008-2d40-44e8-90f8-beee7dbf1822:0-0-0-1-0-0-0-2-1-1-0-5-a-3', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 6, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-7-7', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 6, 'Equivalent Trace ID': '9f4a2008-2d40-44e8-90f8-beee7dbf1822:0-0-0-7-3', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 7, 'Equivalent Trace ID': '6c5099cb-f06f-40ca-8051-57f392137ed4:0-0-0-1-0-1-2-86-2-3-0', 'Is_Ground_Truth_ID': 'Yes'},
        {'Ref #': 7, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-7-1a', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 7, 'Equivalent Trace ID': '6c5099cb-f06f-40ca-8051-57f392137ed4:0-0-0-4-1', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 8, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-1-0-0-0-2-1-1-0-24-a-3', 'Is_Ground_Truth_ID': 'Yes'},
        {'Ref #': 8, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-7-3', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 8, 'Equivalent Trace ID': '2fbd9c9e-e242-46cb-910f-64c7c314b310:0-0-0-1-0-0-2-9-1-7-1a', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 8, 'Equivalent Trace ID': '2fbd9c9e-e242-46cb-910f-64c7c314b310:0-0-0-6-92', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 9, 'Equivalent Trace ID': '9194b1ef-8411-4295-a793-0d4475f95d2d:0-0-0-1-0-0-0-5-2-6-38', 'Is_Ground_Truth_ID': 'Yes'},
        {'Ref #': 9, 'Equivalent Trace ID': '9f4a2008-2d40-44e8-90f8-beee7dbf1822:0-0-0-1-0-0-0-2-1-1-0-5-a-1', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 9, 'Equivalent Trace ID': '9f4a2008-2d40-44e8-90f8-beee7dbf1822:0-0-0-7-1', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 9, 'Equivalent Trace ID': '9194b1ef-8411-4295-a793-0d4475f95d2d:0-0-0-4-c', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 10, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-1-0-0-0-2-1-1-0-24-a-3', 'Is_Ground_Truth_ID': 'Yes'},
        {'Ref #': 10, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-7-3', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 10, 'Equivalent Trace ID': '2fbd9c9e-e242-46cb-910f-64c7c314b310:0-0-0-1-0-0-2-9-1-7-1a', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 10, 'Equivalent Trace ID': '2fbd9c9e-e242-46cb-910f-64c7c314b310:0-0-0-6-92', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 11, 'Equivalent Trace ID': '9194b1ef-8411-4295-a793-0d4475f95d2d:0-0-0-1-0-0-0-5-2-6-38', 'Is_Ground_Truth_ID': 'Yes'},
        {'Ref #': 11, 'Equivalent Trace ID': '9f4a2008-2d40-44e8-90f8-beee7dbf1822:0-0-0-1-0-0-0-2-1-1-0-5-a-1', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 11, 'Equivalent Trace ID': '9f4a2008-2d40-44e8-90f8-beee7dbf1822:0-0-0-7-1', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 11, 'Equivalent Trace ID': '9194b1ef-8411-4295-a793-0d4475f95d2d:0-0-0-4-c', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 12, 'Equivalent Trace ID': '9f4a2008-2d40-44e8-90f8-beee7dbf1822:0-0-0-1-0-0-0-2-1-1-0-5-a-3', 'Is_Ground_Truth_ID': 'Yes'},
        {'Ref #': 12, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-1-0-0-0-2-1-1-0-24-a-7', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 12, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-7-7', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 12, 'Equivalent Trace ID': '9f4a2008-2d40-44e8-90f8-beee7dbf1822:0-0-0-7-3', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 13, 'Equivalent Trace ID': '9194b1ef-8411-4295-a793-0d4475f95d2d:0-0-0-4-a0', 'Is_Ground_Truth_ID': 'Yes'},
        {'Ref #': 13, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-7-29', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 13, 'Equivalent Trace ID': 'bca33c09-0be5-4729-9c2a-1634e5e20915:0-0-0-7-33', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 14, 'Equivalent Trace ID': '34e8c539-94b9-41bc-95df-fec503e31153:0-0-0-4-72', 'Is_Ground_Truth_ID': 'Yes'},
        {'Ref #': 14, 'Equivalent Trace ID': '9f4a2008-2d40-44e8-90f8-beee7dbf1822:0-0-0-7-14', 'Is_Ground_Truth_ID': 'No'},
        {'Ref #': 14, 'Equivalent Trace ID': '9f4a2008-2d40-44e8-90f8-beee7dbf1822:0-0-0-7-c', 'Is_Ground_Truth_ID': 'No'},
    ]
    
    # --- File and Directory Paths ---
    input_file_path = os.path.join('chat_conversations', 'crystalclear_chats_10.v3.txt')
    output_dir = os.path.join('output', 'evaluation')
    output_csv_path = os.path.join(output_dir, 'validation_results.csv')

    # --- Processing Logic ---
    results_for_csv = []
    
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_file_path}'")
        return

    print("--- Starting Trace ID Validation ---\n")

    for item in trace_id_map:
        ref_num = item['Ref #']
        trace_id = item['Equivalent Trace ID']
        is_gt = item['Is_Ground_Truth_ID']
        
        event_description = ground_truth_data.get(ref_num, "Unknown Event")
        
        found = "No"
        sender = "N/A"
        receiver = "N/A"

        for i, line in enumerate(lines):
            if trace_id in line:
                found = "Yes"
                # Check if there is a next line to read
                if i + 1 < len(lines):
                    next_line = lines[i+1].strip()
                    
                    # Regex to find sender and receiver
                    from_match = re.search(r"From:\s*(.*?)(?:\s*\||$)", next_line)
                    to_match = re.search(r"To:\s*(.*?)(?:\s*\||$)", next_line)
                    
                    if from_match:
                        sender = from_match.group(1).strip()
                    if to_match:
                        receiver = to_match.group(1).strip()
                break # Stop searching once the first occurrence is found

        # --- Console Output ---
        print(f"--- [Ref #{ref_num}] ---")
        print(f"Event: {event_description}")
        print(f"Trace ID: {trace_id}")
        print(f"Found in Report: {found}")
        if found == "Yes":
            print(f"  -> From: {sender}")
            print(f"  -> To: {receiver}")
        print("-" * 20 + "\n")

        # Prepare data for CSV
        results_for_csv.append({
            'Ref #': ref_num,
            'Event Description': event_description,
            'Equivalent Trace ID': trace_id,
            'Is_Ground_Truth_ID': is_gt,
            'Occurs_in_Report': found,
            'From': sender,
            'To': receiver
        })

    # --- CSV Output ---
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        headers = ['Ref #', 'Event Description', 'Equivalent Trace ID', 'Is_Ground_Truth_ID', 'Occurs_in_Report', 'From', 'To']
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(results_for_csv)
            
        print(f"--- Validation Complete ---")
        print(f"Results have been saved to '{output_csv_path}'")
        
    except IOError as e:
        print(f"Error writing to CSV file: {e}")


if __name__ == '__main__':
    validate_trace_ids()