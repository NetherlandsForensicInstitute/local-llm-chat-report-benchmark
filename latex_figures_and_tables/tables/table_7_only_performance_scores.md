### Model Quality Score Comparison

| Model | Entity Accuracy | Trace ID Retrieval | Role Attribution | Timeline Consistency | Factual Consistency | Reasoning Quality | **Final Weighted** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **gemini-2.5-pro (staged)** | 0.88 | 0.93 | 0.86 | 0.93 | 0.60 | 0.70 | **0.83** |
| **gpt-oss-20b** | 0.81 | 0.93 | 0.71 | 0.64 | 0.77 | 0.60 | **0.77** |
| **phi-4-reasoning** | 0.88 | 0.76 | 0.43 | 0.79 | 0.73 | 0.50 | **0.71** |
| **qwen3-14b** | 0.81 | 0.50 | 0.43 | 0.43 | 0.73 | 0.60 | **0.60** |
| **gemma-3-27b-it-qat** | 0.81 | 0.10 | 0.71 | 0.57 | 0.69 | 0.50 | **0.57** |
| **gemma-3-12b-it-qat** | 0.69 | 0.17 | 0.33 | 0.29 | 0.61 | 0.40 | **0.43** |