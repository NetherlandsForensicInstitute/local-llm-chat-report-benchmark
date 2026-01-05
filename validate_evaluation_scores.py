import csv
import os
import math

# --- Define Weights as per the procedure ---
WEIGHTS = {
    'Entity_Accuracy_Score': 0.25,
    'Trace_ID_Retrieval_Score': 0.20,
    'Role_Attribution_Score': 0.15,
    'Timeline_Consistency_Score': 0.15,
    'Factual_Consistency_Score': 0.15,
    'Reasoning_Quality_Score': 0.10
}

# --- Define the file path ---
FILE_PATH = os.path.join('output', 'evaluation', 'report_evaluation.csv')

# --- Helper function for color-coded output ---
def print_status(message, is_correct):
    """Prints a color-coded status message."""
    C_GREEN = '\033[92m'
    C_RED = '\033[91m'
    C_END = '\033[0m'
    if is_correct:
        print(f"  [{C_GREEN}OK{C_END}] {message}")
    else:
        print(f"  [{C_RED}ERROR{C_END}] {message}")

def verify_scores():
    """Reads the specified CSV file and verifies the scores for each row."""
    
    # 1. Check if the file exists before attempting to open it
    if not os.path.exists(FILE_PATH):
        print(f"{C_RED}Error: File not found at '{FILE_PATH}'. Please ensure the file exists in the correct location.{C_END}")
        return

    print(f"Reading and verifying scores from: {FILE_PATH}\n")

    with open(FILE_PATH, mode='r', newline='') as infile:
        # Use DictReader to easily access columns by name
        reader = csv.DictReader(infile)
        
        for row in reader:
            model_name = row['Model']
            print(f"--- Verifying Model: {model_name} ---")
            
            # --- 1. Verify Entity Accuracy Score ---
            try:
                n = int(row['GT_Entities'])
                x = int(row['TP_Entities'])
                z = int(row['FP_Entities'])
                score_from_file = float(row['Entity_Accuracy_Score'])
                
                # Formula: Score = ((1/n) * x) - ((0.5/n) * z)
                calculated_score = ((1/n) * x) - ((0.5/n) * z) if n > 0 else 0.0
                
                is_correct = math.isclose(calculated_score, score_from_file, abs_tol=0.01)
                msg = f"Entity Accuracy: Calculated={calculated_score:.2f}, File={score_from_file:.2f}"
                print_status(msg, is_correct)

            except (ValueError, ZeroDivisionError, KeyError) as e:
                print(f"  [{C_RED}ERROR{C_END}] Could not calculate Entity Accuracy Score. Reason: {e}")

            # --- 2. Verify Trace ID Retrieval Score ---
            try:
                n_total = int(row['GT_Trace_IDs'])
                n_c = int(row['Complete_Trace_IDs'])
                n_p = int(row['Partial_Trace_IDs'])
                n_o = int(row['Root_Only_Trace_IDs'])
                score_from_file = float(row['Trace_ID_Retrieval_Score'])
                
                # Formula: Raw Score / Max Score
                raw_score = (n_c * 3) + (n_p * 2) + (n_o * 1)
                max_score = n_total * 3
                calculated_score = raw_score / max_score if max_score > 0 else 0.0

                is_correct = math.isclose(calculated_score, score_from_file, abs_tol=0.01)
                msg = f"Trace ID Retrieval: Calculated={calculated_score:.2f}, File={score_from_file:.2f}"
                print_status(msg, is_correct)

            except (ValueError, ZeroDivisionError, KeyError) as e:
                print(f"  [{C_RED}ERROR{C_END}] Could not calculate Trace ID Retrieval Score. Reason: {e}")

            # --- 3. Verify Final Weighted Score ---
            try:
                # Use the scores from the file for the final calculation
                # to isolate errors in the weighting step itself.
                scores = {key: float(row[key]) for key in WEIGHTS.keys()}
                score_from_file = float(row['Final_Weighted_Score'])

                calculated_weighted_score = sum(scores[key] * WEIGHTS[key] for key in WEIGHTS)

                is_correct = math.isclose(calculated_weighted_score, score_from_file, abs_tol=0.01)
                msg = f"Final Weighted Score: Calculated={calculated_weighted_score:.2f}, File={score_from_file:.2f}"
                print_status(msg, is_correct)

            except (ValueError, KeyError) as e:
                print(f"  [{C_RED}ERROR{C_END}] Could not calculate Final Weighted Score. Reason: {e}")
            
            print("-" * (len(model_name) + 24) + "\n")


if __name__ == "__main__":
    verify_scores()