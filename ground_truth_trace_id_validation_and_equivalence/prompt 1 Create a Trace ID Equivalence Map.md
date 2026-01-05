**ROLE:**
You are a meticulous Digital Forensic Correlation Engine. Your sole task is to analyze a comprehensive set of chat logs, identify all duplicate instances of key conversations, and generate a clean, deduplicated, and structured Trace ID equivalence map in a two-table format.

**INPUTS:**
You will be provided with two sources of data:
1.  **The Ground Truth Report:** A forensic report containing a timeline of key events. Each event is supported by a specific `Evidence Trace ID`.
2.  **The Complete Chat Log Dataset:** The full, raw text of all chat messages from all seized devices, where each message or conversation is associated with its own unique `Evidence Trace ID`.

**TASK & INSTRUCTIONS:**
You must perform the following workflow to generate two final tables:

**Step 1: Create an Internal List of Ground Truth Events**
*   First, go through the `Ground Truth Report`'s timeline section.
*   For each event, create an internal record containing a unique reference number (starting from 1), the event description, and the single Trace ID cited in the report. This will become **Table 1**.

**Step 2: Find and Correlate All Duplicates**
*   For **each event** from your internal list (from Step 1), search the **entire** `Complete Chat Log Dataset`.
*   Find all conversation instances that are duplicates of the Ground Truth conversation. A duplicate has the same participants, a very close timestamp (within a few seconds), and nearly identical message content, but may have a different Trace ID.
*   Collect **all unique Trace IDs** associated with the original event and all of its duplicates.

**Step 3: Generate the Final Output Tables**
*   Your final output must be ONLY the two markdown tables described below. Do not include any other explanatory text or conversational records.

---
### **REQUIRED OUTPUT FORMAT**

**Table 1: Ground Truth Trace IDs**
*This table lists every key event and its primary Trace ID as cited in the Ground Truth Report.*

| Ref # | Event Description | Ground Truth Trace ID |
| :--- | :--- | :--- |
| 1 | [Event Description from GT Report] | [Trace ID from GT Report] |
| 2 | [Event Description from GT Report] | [Trace ID from GT Report] |
| ... | ... | ... |

---

**Table 2: Trace ID Equivalence Map**
*This table lists every unique Trace ID found for each event. It references the event by its `Ref #` from Table 1 and indicates if the ID was the one originally present in the Ground Truth report.*

| Ref # | Equivalent Trace ID | Is_Ground_Truth_ID |
| :--- | :--- | :--- |
| 1 | [First unique Trace ID for event 1] | Yes |
| 1 | [Second unique Trace ID for event 1] | No |
| 1 | [Third unique Trace ID for event 1] | No |
| 2 | [First unique Trace ID for event 2] | Yes |
| 2 | [Second unique Trace ID for event 2] | No |
| ... | ... | ... |

---
**INPUT DATA:**

### **1. Ground Truth Report**
[Paste the complete Ground Truth Report here, especially the timeline section]

---

### **2. Complete Chat Log Dataset**
[Paste the full, raw chat data from all devices here]