### Prompt:

Write a Python script that validates the presence of trace IDs within a chat conversation file. The script's primary function is to cross-reference trace IDs from a given table with a text file and report on their occurrence, extracting relevant conversational metadata.

**Script Requirements:**

1.  **Input File:** The script must read a text file named `chat_conversations\crystalclear_chats_10.v3.txt`. It should handle the case where the file might not be found.

2.  **Data Source:** The logic will be driven by the two Markdown tables provided below:
    *   **Table 1: Ground Truth Trace IDs:** This table maps a `Ref #` to an `Event Description`.
    *   **Table 2: Trace ID Equivalence Map:** This table lists all trace IDs to be searched, their corresponding `Ref #`, and a flag indicating if it's the primary ground truth ID.

3.  **Processing Logic:**
    For each row in **Table 2**, the script must:
    a. Take the `Equivalent Trace ID` and search for its exact string within the input text file.
    b. Determine if the trace ID was found (`Yes` or `No`).
    c. If the trace ID is found, the script must read the **line immediately following** the line containing the ID.
    d. From this next line, parse the text to extract the sender (e.g., "From: Nerijus Bos") and the receiver (e.g., "To: Quan Xiuan"). If these details are not present on the line, they should be marked as "N/A".
    e. Use the `Ref #` to look up the corresponding `Event Description` from **Table 1**.

4.  **Output Requirements:**
    The script must produce two forms of output:
    a. **CSV File:**
        *   Create a directory `output\evaluation` if it does not already exist.
        *   Generate a CSV file named `validation_results.csv` inside this directory.
        *   The CSV file must contain the following headers: `Ref #`, `Event Description`, `Equivalent Trace ID`, `Is_Ground_Truth_ID`, `Occurs_in_Report`, `From`, `To`.
    b. **Console Output:**
        *   Print a human-readable summary to the console for each trace ID processed. This summary should clearly show the `Ref #`, `Event Description`, the trace ID, whether it was found, and the extracted `From` and `To` information.

Please use the two Markdown tables below to build the script's internal data structures.

---

