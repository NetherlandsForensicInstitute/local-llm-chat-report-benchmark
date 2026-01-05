Here’s the **Markdown** version of the timeline comparison table.
**GT** = number of ground-truth events; **Model** = number of model events.
**Correct (TP)**: matches GT in actors/action and time. **Wrong (FP)**: no matching GT event.
**Wrong event (partial)**: same situation/actors but core semantics wrong. **Wrong date (partial)**: actors/action match but time wrong.
**Missed (FN)**: GT events not covered by Correct/Wrong event/Wrong date.
By design: `Correct + Wrong + Wrong event + Wrong date = Model`, and `Missed = GT − (Correct + Wrong event + Wrong date)`.

|                         | GT | Model | Correct | Wrong | Wrong event | Wrong date | Missed |
| ----------------------- | -: | ----: | ------: | ----: | ----------: | ---------: | -----: |
| gemma-3-12b             | 14 |    12 |       3 |     6 |           1 |          2 |      8 |
| gemini-2.5-pro (staged) | 14 |    19 |      12 |     6 |           0 |          1 |      1 |
| gemma-3-27b             | 15 |    22 |       5 |    14 |           3 |          0 |      7 |
| gpt-oss-20b             | 14 |    23 |       8 |    13 |           2 |          0 |      4 |
| phi-4-reasoning         | 14 |    20 |       9 |     8 |           1 |          2 |      2 |
| qwen-3-14b              | 14 |     8 |       2 |     2 |           4 |          0 |      8 |
