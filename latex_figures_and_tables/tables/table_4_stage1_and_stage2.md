### Combined Performance Speeds with Stage-1 Stats

This table shows the runtime of all models in Stage-1 (summaries) and Stage-2 (reports).  
The Stage-1 times include both summarization and any associated *thinking* (thoughts) steps.  
Note that **gpt-oss-20b**, **qwen3-14b**, and **phi-4-reasoning** are reasoning models,  
which typically incur extra computation time compared to instruction-tuned models.  

| Model                       | Stage-1 Total | Shortest | Longest | Average | Stage-2 | Total   |
|------------------------------|---------------|----------|---------|---------|---------|---------|
| **gpt-oss-20b**             | 11m37s        | 44s      | 1m40s   | 1m10s   | 2m25s   | 14m2s   |
| **qwen3-14b**               | 15m57s        | 48s      | 2m4s    | 1m36s   | 2m27s   | 18m24s  |
| **google_gemma-3-12b-it-qat** | 18m54s        | 27s      | 5m30s   | 1m53s   | 2m47s   | 21m41s  |
| **phi-4-reasoning**         | 1h20m3s       | 1m59s    | 16m35s  | 8m0s    | 18m0s   | 1h38m3s |
| **google_gemma-3-27b-it-qat** | 9h27m21s      | 12m57s   | 2h13m20s| 56m44s  | 1h35m10s| 11h2m31s|
