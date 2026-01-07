# Structured Report Generation using Local LLMs for Chat-Based Digital Forensics — Reproduction Guide

This repository contains the code, prompts, and instructions to reproduce the experiments behind our paper submitted to the DFDS symposium which is hosted at the **[DFRWS EU 2026](https://dfrws.org/conferences/dfrws-eu-2026/)**.

> Order of operations: **Experiment 1 (ground truth)** → **Dataset split** → **Experiment 2 / Stage 1** → **Experiment 2 / Stage 2** → **Evaluation** → **Figures** → **Appendices**.

- 📄 **Draft paper (PDF):** [`DFRWS2026EU\ Structured\ Report\ Generation\ using\ Local\ LLMs\ for\ Chat-Based\ Digital\ Forensics.pdf`](DFRWS2026EU Structured Report Generation using Local LLMs for Chat-Based Digital Forensics.pdf)

---

## Introduction (adapted from the paper’s abstract)

We compare **global** (frontier) and **local** LLMs on a realistic digital-forensics task: creating a structured investigative report from a large multi-device chat corpus. To handle long evidence sequences on local models with limited context windows, we implement a **two-stage pipeline**: (1) per-part extraction of investigation-relevant records and (2) cross-part synthesis into a full report with an individuals/roles table and a chronological timeline that cites **verbatim** Trace IDs. We construct a **ground truth** using a capable global model and evaluate model reports with a combination of LLM-assisted grading and **deterministic validation** of Trace IDs (including an equivalence map for near-duplicates).

Our results highlight a practical trade-off between **quality** and **cost/latency**: global models deliver the strongest end-to-end accuracy out-of-the-box, while carefully prompted local models, run via an OpenAI-compatible REST endpoint, can approach useful performance with significantly lower cost and controllability—particularly when the pipeline enforces strong constraints on evidence citation and timeline consistency. We release our prompts, runner, and validation scripts to enable **fully reproducible** comparisons across model choices and hardware setups.

---

## Contents
- [Prerequisites](#prerequisites)
- [Data & Layout](#data--layout)
- [Experiment 1 — Ground truth creation](#experiment-1--ground-truth-creation)
- [Dataset split (prep for Exp. 2)](#dataset-split-prep-for-exp-2)
- [Experiment 2 — Two-stage pipeline](#experiment-2--two-stage-pipeline)
  - [Stage 1 — Per-part extraction](#stage-1--per-part-extraction)
  - [Stage 2 — Cross-part synthesis](#stage-2--cross-part-synthesis)
  - [Gemini 2.5 Pro — Two-stage (manual) comparison](#gemini-25-pro--two-stage-manual-comparison)
- [Evaluation](#evaluation)
  - [Whole-report scoring](#whole-report-scoring)
  - [Timeline-only scoring](#timeline-only-scoring)
  - [Recompute/verify evaluation math](#recomputeverify-evaluation-math)
  - [Tables](#tables)
- [Prompts — quick index](#prompts--quick-index)
- [Prompts used for figures](#prompts-used-for-figures)
- [Appendix A — Dataset](#appendix-a--dataset)
- [Appendix B — Per-model artifacts](#appendix-b--per-model-artifacts)
- [Appendix C — Hardware & runtime notes](#appendix-c--hardware--runtime-notes)
- [Gotchas & notes](#gotchas--notes)

---

## Prerequisites

- Python 3.10+
- (Optional) [LM Studio](https://lmstudio.ai/) or any OpenAI-compatible REST endpoint to run local models.
- A `.env` file (optional) with `HF_TOKEN` if you use tokenization via Hugging Face in the splitter.

```bash
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
```

---

## Data & Layout

- Corpus (full): [`chat_conversations/crystalclear_chats_10.v3.txt`](chat_conversations/crystalclear_chats_10.v3.txt)

Other key scripts and artifacts:
- Runner: [`experiment_2.py`](experiment_2.py)
- Splitter: [`split_chat_conversations.py`](split_chat_conversations.py)
- Ground truth report (generated in Exp. 1): [`ground_truth_report.md`](ground_truth_report.md)
- Evaluation helper (numeric check): [`validate_evaluation_scores.py`](validate_evaluation_scores.py)

> **Folders used by the pipeline:**
> - Split parts for Stage 1 are expected (by default) in `split_chatconversations/` with pattern `*_*.txt`.
> - Stage-1 outputs: `output/stage-1/<model>/...`
> - Stage-2 outputs: `output/stage-2/...`

---

## Experiment 1 — Ground truth creation

### 1.1 Generate the ground-truth report

- **Prompt:** [`prompts/prompt_1.md`](prompts/prompt_1.md)  
- **Input:** [`chat_conversations/crystalclear_chats_10.v3.txt`](chat_conversations/crystalclear_chats_10.v3.txt)  
- **Output:** [`ground_truth_report.md`](ground_truth_report.md)

- **Model thoughts (optional):** [`ground_truth_report_thoughts.md`](ground_truth_report_thoughts.md)

Run your chosen capable model (e.g., hosted or local) with the contents of `prompt_1.md` and the full corpus as instructed in the prompt. Save the result to `ground_truth_report.md` at repo root.

### 1.2 Create Trace-ID Equivalence Map (dedup near-duplicates)

- **Prompt:** [`ground_truth_trace_id_validation_and_equivalence/prompt 1 Create a Trace ID Equivalence Map.md`](ground_truth_trace_id_validation_and_equivalence/prompt%201%20Create%20a%20Trace%20ID%20Equivalence%20Map.md)  
- **Inputs:** `ground_truth_report.md` + the full chat corpus  
- **Output:** `ground_truth_trace_id_validation_and_equivalence/equivalence_map_tables.md`

This consolidates duplicate or near-duplicate trace IDs across devices/exports for fair scoring downstream.

### 1.3 Generate a validation script for trace IDs

- **Prompt:** [`ground_truth_trace_id_validation_and_equivalence/prompt 2 Create trace id validation script.md`](ground_truth_trace_id_validation_and_equivalence/prompt%202%20Create%20trace%20id%20validation%20script.md)  
- **Output (code):** `ground_truth_trace_id_validation_and_equivalence/validate_trace_ids.py`

This script cross-checks every ID from the equivalence tables against the full corpus.

```bash
python ground_truth_trace_id_validation_and_equivalence/validate_trace_ids.py \
  --equivalence ground_truth_trace_id_validation_and_equivalence/equivalence_map_tables.md \
  --corpus chat_conversations/crystalclear_chats_10.v3.txt \
  --out output/evaluation/validation_results.csv
```

---

## Dataset split (prep for Exp. 2)

We split the full corpus into token-limited parts for local-context models.

- **Script:** [`split_chat_conversations.py`](split_chat_conversations.py)
- **Default tokenizer:** The script loads a Hugging Face tokenizer (see code). Provide `HF_TOKEN` in `.env` if needed.
- **Outputs:** numbered parts. You have **two options** to match `experiment_2.py`’s default pattern:

### Option A — Write parts into `split_chatconversations/` (no extra flags later)
```bash
mkdir -p split_chatconversations
python split_chat_conversations.py \
  --split \
  --file chat_conversations/crystalclear_chats_10.v3.txt \
  --max-tokens 29000 \
  --outdir split_chatconversations
```

### Option B — Keep parts in `chat_conversations/` and tell the runner where they are
```bash
python split_chat_conversations.py \
  --split \
  --file chat_conversations/crystalclear_chats_10.v3.txt \
  --max-tokens 29000

# later: add --pattern "chat_conversations/crystalclear_chats_10.v3_*.txt" to experiment_2.py
```

---

## Experiment 2 — Two-stage pipeline

> The runner script **does both stages in one invocation**. It reads `prompts/stage_1.md` for Stage 1 and `prompts/stage_2.md` for Stage 2. Models are a **fixed list inside the script**:
>
> `["google_gemma-3-12b-it-qat", "qwen3-14b", "phi-4-reasoning", "gpt-oss-20b", "google_gemma-3-27b-it-qat"]`

### Stage 1 — Per-part extraction (inside the runner)

- **Runner:** [`experiment_2.py`](experiment_2.py)  
- **Prompt:** [`prompts/stage_1.md`](prompts/stage_1.md)  
- **Input default pattern:** `split_chatconversations/*_*.txt` (override with `--pattern`)  
- **Output:** `output/stage-1/<model>/<split_base>_summary.txt` (+ optional `<split_base>_thoughts.txt`)  
- **Stats CSV:** `output/stage-1/stage-1_summary_stats.csv` with columns  
  `model,input_file,summary_file,thoughts_file,seconds,tokens`

**What it does:** For each model and each split file, it posts `{system: stage_1.md, user: <split text>}` to the REST API, extracts an optional `<think>…</think>` block, writes the summary, and appends a row to the Stage‑1 CSV. **Recovery feature:** if a summary already exists, that file is skipped.

### Stage 2 — Cross-part synthesis (inside the runner)

- **Prompt:** [`prompts/stage_2.md`](prompts/stage_2.md)  
- **Inputs:** All `*_summary.txt` files from Stage 1 for the current model (concatenated in-order with clear START/END markers)  
- **Output:** `output/stage-2/<model>_<YYYYMMDDHHMM>_report.md` (+ optional `_thoughts.md`)  
- **Stats CSV:** `output/stage-2/stage-2_report_stats.csv` with columns  
  `model,report_file,thoughts_file,tokens,has_thoughts,duration`

**Recovery feature:** If a report for a model already exists in `output/stage-2/` (wildcard `<model>_*_report.md`), that model is **skipped** in Stage 2.

### Example run (default pattern in `split_chatconversations/`)

```bash
python experiment_2.py \
  --api-url "http://localhost:1234/v1/chat/completions"
```

### Example run (if your split parts are in `chat_conversations/`)

```bash
python experiment_2.py \
  --api-url "http://localhost:1234/v1/chat/completions" \
  --pattern "chat_conversations/crystalclear_chats_10.v3_*.txt"
```

### Gemini 2.5 Pro — Two-stage (manual) comparison

To compare a **global** model using the same two-stage logic, we ran **Gemini 2.5 Pro** manually (outside `experiment_2.py`):

1. **Stage 1 (manual):** Use [`prompts/stage_1.md`](prompts/stage_1.md) over the **full corpus** (or your preferred chunking in the UI) and save a **single concatenated file**:
   - [`output/stage-1/gemini-2.5-pro/gemini-2.5-pro-summaries.md`](output/stage-1/gemini-2.5-pro/gemini-2.5-pro-summaries.md)

2. **Stage 2 (manual):** Use [`prompts/stage_2.md`](prompts/stage_2.md) with that concatenated summary as input and save the final report under `output/stage-2/`:
   - [`output/stage-2/gemini-2.5-pro-report-from-summaries.md`](output/stage-2/gemini-2.5-pro-report-from-summaries.md)

> We keep the same output structure so that evaluation treats Gemini 2.5 Pro like any local model.

---

## Evaluation

### Whole-report scoring

* **Prompt:** [`prompts/prompt_4_evaluation.md`](prompts/prompt_4_evaluation.md)
* **Inputs:**

  * Ground truth: [`ground_truth_report.md`](ground_truth_report.md)
  * Trace-ID equivalence map: [`ground_truth_trace_id_validation_and_equivalence/equivalence_map_tables.md`](ground_truth_trace_id_validation_and_equivalence/equivalence_map_tables.md)

* **Output:**

  * Aggregated CSV: [`output/evaluation/report_evaluation.csv`](output/evaluation/report_evaluation.csv)
  * Per-model evaluation markdown:

    * [`output/evaluation/google_gemma-3-12b-it-qat_report_evaluation.md`](output/evaluation/google_gemma-3-12b-it-qat_report_evaluation.md)
    * [`output/evaluation/google_gemma-3-27b-it-qat_report_evaluation.md`](output/evaluation/google_gemma-3-27b-it-qat_report_evaluation.md)
    * [`output/evaluation/gpt-oss-20b_report_evaluation.md`](output/evaluation/gpt-oss-20b_report_evaluation.md)
    * [`output/evaluation/phi-4-reasoning_report_evaluation.md`](output/evaluation/phi-4-reasoning_report_evaluation.md)
    * [`output/evaluation/qwen3-14b_report_evaluation.md`](output/evaluation/qwen3-14b_report_evaluation.md)
    * [`output/evaluation/gemini-2.5-pro_report_evaluation.md`](output/evaluation/gemini-2.5-pro_report_evaluation.md)

### Timeline-only scoring

- **Prompt:** [`prompts/prompt_5_generate_model_timeline_evaluation.md`](prompts/prompt_5_generate_model_timeline_evaluation.md)  
- **Inputs:** GT timeline table; model name; model’s timeline table  
- **Output columns:** `Model,Groundtruth,Model,Correct,Wrong,Wrong event,Wrong date,Missed`

### Recompute/verify evaluation math

- **Script:** [`validate_evaluation_scores.py`](validate_evaluation_scores.py)

```bash
python validate_evaluation_scores.py
```

This re-computes key metrics and the final weighted score to sanity-check the LLM-graded outputs in `output/evaluation/report_evaluation.csv`.

### Tables

Below are the Markdown tables generated from the pipeline and used in the paper (kept under LaTeX assets).

- **Table 1 — Dataset overview**: dataset size, #devices, #conversations, and split statistics.  
  [`latex_figures_and_tables/tables/table_1_dataset.md`](latex_figures_and_tables/tables/table_1_dataset.md)

- **Table 2 — Models compared**: model names, parameter sizes, quantization, and serving details used in our runs.  
  [`latex_figures_and_tables/tables/table_2_modesl.md`](latex_figures_and_tables/tables/table_2_modesl.md)

- **Table 4 — Stage-1 and Stage-2 outputs**: counts of extracted records, unique trace IDs, and final report lengths per model.  
  [`latex_figures_and_tables/tables/table_4_stage1_and_stage2.md`](latex_figures_and_tables/tables/table_4_stage1_and_stage2.md)

- **Table 4 (timing) — Stage-1 runtime**: per-part/runtime aggregates for Stage-1 by model (median, p90, total).  
  [`latex_figures_and_tables/tables/table_4_stage_1_timing.md`](latex_figures_and_tables/tables/table_4_stage_1_timing.md)

- **Table 5 — Retrieved Trace IDs**: recall of Trace IDs relative to ground truth (with equivalence mapping), including graded credit.  
  [`latex_figures_and_tables/tables/table_5_Retrieved%20IDs.md`](latex_figures_and_tables/tables/table_5_Retrieved%20IDs.md)

- **Table 6 — Timeline comparison**: one-to-one alignment results (Correct, Wrong event, Wrong date, Missed) per model.  
  [`latex_figures_and_tables/tables/table_6_timeline_comparison.md`](latex_figures_and_tables/tables/table_6_timeline_comparison.md)

- **Table 7 — Performance scores only**: entity accuracy, trace-ID retrieval, role attribution, timeline and factual consistency, reasoning quality.  
  [`latex_figures_and_tables/tables/table_7_only_performance_scores.md`](latex_figures_and_tables/tables/table_7_only_performance_scores.md)

- **Table 7 — Performance + timing**: final weighted scores alongside runtime metrics.  
  [`latex_figures_and_tables/tables/table_7_performce_score_and_timing.md`](latex_figures_and_tables/tables/table_7_performce_score_and_timing.md)

---

## Prompts — quick index

**Core prompts (pipeline):**
- Ground truth: [`prompts/prompt_1.md`](prompts/prompt_1.md) → `ground_truth_report.md`
- Stage 1 (per split part): [`prompts/stage_1.md`](prompts/stage_1.md) → `*_summary.txt`
- Stage 2 (per model): [`prompts/stage_2.md`](prompts/stage_2.md) → `[model]_YYYYMMDDHHMM_report.md`
- Whole-report evaluation: [`prompts/prompt_4_evaluation.md`](prompts/prompt_4_evaluation.md)
- Timeline evaluation: [`prompts/prompt_5_generate_model_timeline_evaluation.md`](prompts/prompt_5_generate_model_timeline_evaluation.md)

---

## Prompts used for figures

> **Figure ordering:** **Figure 4 = Roles classification**, **Figure 5 = Scatterplot**.

- **Figure 4 — Roles classification JSON**  
  - Prompt:  
    [`latex_figures_and_tables/figures/prompt_for_converting_report_roles_to_json_for_figure_4.md`](latex_figures_and_tables/figures/prompt_for_converting_report_roles_to_json_for_figure_4.md)  
  - Output: `latex_figures_and_tables/figures/roles_classification.json`

- **Figure 5 — Scatterplot (performance vs. time)**  
  - Prompt file (repo may use one of these names):  
    - [`latex_figures_and_tables/figures/figure_5_prompt_to_turn_json_into_scatterplot.md`](latex_figures_and_tables/figures/figure_5_prompt_to_turn_json_into_scatterplot.md)  
    - or [`latex_figures_and_tables/figures/figure_4_prompt_to_turn_json_into_scatterplot.md`](latex_figures_and_tables/figures/figure_4_prompt_to_turn_json_into_scatterplot.md)

---

## Appendix A — Dataset

- **Full corpus:** [`chat_conversations/crystalclear_chats_10.v3.txt`](chat_conversations/crystalclear_chats_10.v3.txt)  
- **Dataset overview (Table 1):** [`latex_figures_and_tables/tables/table_1_dataset.md`](latex_figures_and_tables/tables/table_1_dataset.md)

**Split parts in `chat_conversations/`:**  
- [`chat_conversations/crystalclear_chats_10.v3_01.txt`](chat_conversations/crystalclear_chats_10.v3_01.txt)  
- [`chat_conversations/crystalclear_chats_10.v3_02.txt`](chat_conversations/crystalclear_chats_10.v3_02.txt)  
- [`chat_conversations/crystalclear_chats_10.v3_03.txt`](chat_conversations/crystalclear_chats_10.v3_03.txt)  
- [`chat_conversations/crystalclear_chats_10.v3_04.txt`](chat_conversations/crystalclear_chats_10.v3_04.txt)  
- [`chat_conversations/crystalclear_chats_10.v3_05.txt`](chat_conversations/crystalclear_chats_10.v3_05.txt)  
- [`chat_conversations/crystalclear_chats_10.v3_06.txt`](chat_conversations/crystalclear_chats_10.v3_06.txt)  
- [`chat_conversations/crystalclear_chats_10.v3_07.txt`](chat_conversations/crystalclear_chats_10.v3_07.txt)  
- [`chat_conversations/crystalclear_chats_10.v3_08.txt`](chat_conversations/crystalclear_chats_10.v3_08.txt)  
- [`chat_conversations/crystalclear_chats_10.v3_09.txt`](chat_conversations/crystalclear_chats_10.v3_09.txt)  
- [`chat_conversations/crystalclear_chats_10.v3_10.txt`](chat_conversations/crystalclear_chats_10.v3_10.txt)

> Each part corresponds to a token-bounded slice (~29k) while preserving device and conversation boundaries where possible.

---

## Appendix B — Per-model artifacts

For each model below, Stage 1 writes per-part summaries to `output/stage-1/<model>/` and Stage 2 writes the final report to `output/stage-2/`. Exact filenames from our runs are linked below.

### google_gemma-3-12b-it-qat
- **Stage-1 summaries:**  
  [`output/stage-1/google_gemma-3-12b-it-qat/crystalclear_chats_10.v3_01_summary.txt`](output/stage-1/google_gemma-3-12b-it-qat/crystalclear_chats_10.v3_01_summary.txt) ·
  [`02`](output/stage-1/google_gemma-3-12b-it-qat/crystalclear_chats_10.v3_02_summary.txt) ·
  [`03`](output/stage-1/google_gemma-3-12b-it-qat/crystalclear_chats_10.v3_03_summary.txt) ·
  [`04`](output/stage-1/google_gemma-3-12b-it-qat/crystalclear_chats_10.v3_04_summary.txt) ·
  [`05`](output/stage-1/google_gemma-3-12b-it-qat/crystalclear_chats_10.v3_05_summary.txt) ·
  [`06`](output/stage-1/google_gemma-3-12b-it-qat/crystalclear_chats_10.v3_06_summary.txt) ·
  [`07`](output/stage-1/google_gemma-3-12b-it-qat/crystalclear_chats_10.v3_07_summary.txt) ·
  [`08`](output/stage-1/google_gemma-3-12b-it-qat/crystalclear_chats_10.v3_08_summary.txt) ·
  [`09`](output/stage-1/google_gemma-3-12b-it-qat/crystalclear_chats_10.v3_09_summary.txt) ·
  [`10`](output/stage-1/google_gemma-3-12b-it-qat/crystalclear_chats_10.v3_10_summary.txt)  
- **Stage-2 report:** [`output/stage-2/google_gemma-3-12b-it-qat_202509171736_report.md`](output/stage-2/google_gemma-3-12b-it-qat_202509171736_report.md)

### qwen3-14b
- **Stage-1 summaries:**  
  [`output/stage-1/qwen3-14b/crystalclear_chats_10.v3_01_summary.txt`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_01_summary.txt) ·
  [`02`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_02_summary.txt) ·
  [`03`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_03_summary.txt) ·
  [`04`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_04_summary.txt) ·
  [`05`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_05_summary.txt) ·
  [`06`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_06_summary.txt) ·
  [`07`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_07_summary.txt) ·
  [`08`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_08_summary.txt) ·
  [`09`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_09_summary.txt) ·
  [`10`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_10_summary.txt)  
- **Stage-1 thoughts (if present):**  
  [`output/stage-1/qwen3-14b/crystalclear_chats_10.v3_01_thoughts.txt`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_01_thoughts.txt) ·
  [`02`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_02_thoughts.txt) ·
  [`03`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_03_thoughts.txt) ·
  [`04`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_04_thoughts.txt) ·
  [`05`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_05_thoughts.txt) ·
  [`06`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_06_thoughts.txt) ·
  [`07`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_07_thoughts.txt) ·
  [`08`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_08_thoughts.txt) ·
  [`09`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_09_thoughts.txt) ·
  [`10`](output/stage-1/qwen3-14b/crystalclear_chats_10.v3_10_thoughts.txt)  
- **Stage-2 report:** [`output/stage-2/qwen3-14b_202509171739_report.md`](output/stage-2/qwen3-14b_202509171739_report.md) · **Thoughts:** [`output/stage-2/qwen3-14b_202509171739_report_thoughts.md`](output/stage-2/qwen3-14b_202509171739_report_thoughts.md)

### phi-4-reasoning
- **Stage-1 summaries:**  
  [`output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_01_summary.txt`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_01_summary.txt) ·
  [`02`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_02_summary.txt) ·
  [`03`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_03_summary.txt) ·
  [`04`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_04_summary.txt) ·
  [`05`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_05_summary.txt) ·
  [`06`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_06_summary.txt) ·
  [`07`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_07_summary.txt) ·
  [`08`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_08_summary.txt) ·
  [`09`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_09_summary.txt) ·
  [`10`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_10_summary.txt)  
- **Stage-1 thoughts (if present):**  
  [`output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_01_thoughts.txt`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_01_thoughts.txt) ·
  [`02`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_02_thoughts.txt) ·
  [`03`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_03_thoughts.txt) ·
  [`04`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_04_thoughts.txt) ·
  [`05`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_05_thoughts.txt) ·
  [`06`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_06_thoughts.txt) ·
  [`07`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_07_thoughts.txt) ·
  [`08`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_08_thoughts.txt) ·
  [`09`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_09_thoughts.txt) ·
  [`10`](output/stage-1/phi-4-reasoning/crystalclear_chats_10.v3_10_thoughts.txt)  
- **Stage-2 report:** [`output/stage-2/phi-4-reasoning_202509171757_report.md`](output/stage-2/phi-4-reasoning_202509171757_report.md) · **Thoughts:** [`output/stage-2/phi-4-reasoning_202509171757_report_thoughts.md`](output/stage-2/phi-4-reasoning_202509171757_report_thoughts.md)

### gpt-oss-20b
- **Stage-1 summaries:**  
  [`output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_01_summary.txt`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_01_summary.txt) ·
  [`02`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_02_summary.txt) ·
  [`03`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_03_summary.txt) ·
  [`04`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_04_summary.txt) ·
  [`05`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_05_summary.txt) ·
  [`06`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_06_summary.txt) ·
  [`07`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_07_summary.txt) ·
  [`08`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_08_summary.txt) ·
  [`09`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_09_summary.txt) ·
  [`10`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_10_summary.txt)  
- **Stage-1 thoughts (if present):**  
  [`output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_01_thoughts.txt`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_01_thoughts.txt) ·
  [`02`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_02_thoughts.txt) ·
  [`03`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_03_thoughts.txt) ·
  [`04`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_04_thoughts.txt) ·
  [`05`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_05_thoughts.txt) ·
  [`06`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_06_thoughts.txt) ·
  [`07`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_07_thoughts.txt) ·
  [`08`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_08_thoughts.txt) ·
  [`09`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_09_thoughts.txt) ·
  [`10`](output/stage-1/gpt-oss-20b/crystalclear_chats_10.v3_10_thoughts.txt)  
- **Stage-2 report:** [`output/stage-2/gpt-oss-20b_202509171759_report.md`](output/stage-2/gpt-oss-20b_202509171759_report.md)

### google_gemma-3-27b-it-qat
- **Stage-1 summaries:**  
  [`output/stage-1/google_gemma-3-27b-it-qat/crystalclear_chats_10.v3_01_summary.txt`](output/stage-1/google_gemma-3-27b-it-qat/crystalclear_chats_10.v3_01_summary.txt) ·
  [`02`](output/stage-1/google_gemma-3-27b-it-qat/crystalclear_chats_10.v3_02_summary.txt) ·
  [`03`](output/stage-1/google_gemma-3-27b-it-qat/crystalclear_chats_10.v3_03_summary.txt) ·
  [`04`](output/stage-1/google_gemma-3-27b-it-qat/crystalclear_chats_10.v3_04_summary.txt) ·
  [`05`](output/stage-1/google_gemma-3-27b-it-qat/crystalclear_chats_10.v3_05_summary.txt) ·
  [`06`](output/stage-1/google_gemma-3-27b-it-qat/crystalclear_chats_10.v3_06_summary.txt) ·
  [`07`](output/stage-1/google_gemma-3-27b-it-qat/crystalclear_chats_10.v3_07_summary.txt) ·
  [`08`](output/stage-1/google_gemma-3-27b-it-qat/crystalclear_chats_10.v3_08_summary.txt) ·
  [`09`](output/stage-1/google_gemma-3-27b-it-qat/crystalclear_chats_10.v3_09_summary.txt) ·
  [`10`](output/stage-1/google_gemma-3-27b-it-qat/crystalclear_chats_10.v3_10_summary.txt)  
- **Stage-2 report:** [`output/stage-2/google_gemma-3-27b-it-qat_202509171934_report.md`](output/stage-2/google_gemma-3-27b-it-qat_202509171934_report.md)

### gemini-2.5-pro (manual two-stage)
- **Stage-1 concatenated summary:**  
  [`output/stage-1/gemini-2.5-pro/gemini-2.5-pro-summaries.md`](output/stage-1/gemini-2.5-pro/gemini-2.5-pro-summaries.md)
- **Stage-2 report:** [`output/stage-2/gemini-2.5-pro-report-from-summaries.md`](output/stage-2/gemini-2.5-pro-report-from-summaries.md)

> Notes: The runner also writes `_thoughts.txt`/`_thoughts.md` files if a model emits a `<think>…</think>` block; these are not used in Stage 2 or evaluation.

---

## Appendix C — Hardware & runtime notes

- **GPU:** NVIDIA **RTX 4500 Ada** (24 GB VRAM). This Ada-generation workstation GPU comfortably serves 12–20B class instruction-tuned models at interactive speeds with 4-bit quantization; larger 27B models run with reduced throughput. Your mileage may vary based on CPU, RAM, and storage bandwidth.
- **Serving:** **LM Studio** with **REST API** enabled, version **0.3.25 (Build 2)**. We used the default OpenAI-compatible endpoint at `http://localhost:1234/v1/chat/completions`.
- **Batching:** The runner sends one split file per request per model. Stage-2 concatenates Stage-1 summaries with START/END markers for deterministic parsing.

---

## Gotchas & notes

- **Paths & patterns:** The runner defaults to `split_chatconversations/*_*.txt`. Either place your split parts there (Option A) or pass `--pattern` to point at where your parts live (Option B).
- **Token budget:** Stage-1 splitting was tuned to ~29k tokens per part. If your local models differ, adjust `--max-tokens` during splitting to stay within their context window.
- **Trace IDs:** Stage-1 and Stage-2 prompts require that every timeline/event entry references **verbatim** Trace IDs. This is critical for evaluation alignment.
- **Thought tags:** If a model emits `<think>…</think>`, the runner saves it separately and excludes it from reports.

---

© 2025 — Reproduction guide for the “Global vs Local LLM” experiments.
