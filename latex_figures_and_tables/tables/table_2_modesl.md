Here’s a **Markdown** version of Table 2.x; all non-cloud models ran on **NVIDIA RTX 4500 ADA**.

| Model                                                      | Hugging Face ID / File                                   |   Context | Quant.      |
| ---------------------------------------------------------- | -------------------------------------------------------- | --------: | ----------- |
| Gemini 2.5 Pro `\cite{gemini25studio}`                     | *(cloud-hosted)*                                         | 1,048,576 | NA          |
| gemma-3-27b-it-qat `\cite{bartowski_gemma3_27b_qat_2025}`  | `gemma-3-27B-it-qat-GGUF / gemma-3-27B-it-QAT-Q4_0.gguf` |    32,768 | Q4\_0 (QAT) |
| gemma-3-12b-it-qat `\cite{bartowski_gemma3_12b_gguf_2025}` | `gemma-3-12B-it-qat-GGUF / gemma-3-12B-it-QAT-Q4_0.gguf` |    32,768 | Q4\_0 (QAT) |
| Phi-4-Reasoning `\cite{phi4_reasoning_gguf_2025}`          | `Phi-4-reasoning-GGUF / Phi-4-reasoning-Q4_K_M.gguf`     |    32,768 | Q4\_K\_M    |
| qwen-3-14b `\cite{qwen3_14b_gguf_2025}`                    | `lmstudio-community/Qwen3-14B-GGUF`                      |    32,768 | Q4\_K\_M    |
| gpt-oss-20b `\cite{openai_gpt_oss_20b_2025}`               | `openai/gpt-oss-20b`                                     |    32,768 | MXFP4       |
