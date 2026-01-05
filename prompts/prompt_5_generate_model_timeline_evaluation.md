## INPUT FORMAT (exactly this order)
1) Groundtruth timeline (a Markdown table with columns like: Date/Time, Event Description, Involved Parties, Trace ID)
2) A line: MODEL: <model-name>
3) Model timeline (a Markdown table with similar columns)

## GOAL
Produce exactly one CSV line (NO header, NO extra text) with these columns in this order:
Model,Groundtruth,Model,Correct,Wrong,Wrong event,Wrong date,Missed

All numeric values must be integers.

## DEFINITIONS (disjoint categories)
- Correct (TP): A model event that matches a ground truth event in (a) core semantics (who did what to whom) AND (b) time.
  • Time match: same timestamp OR clearly the same calendar moment (e.g., same day and no competing GT candidate).  
- Wrong: A model event that has no matching GT event at all (off-topic, hallucinated, or contradictory). It does NOT cover any GT event.
- Wrong event (partial): Model event concerns the same situation/actors/topic window as some GT event (so we do consider it to “cover” that GT event), but core semantics are wrong (e.g., actor/recipient reversed, action materially incorrect).
- Wrong date (partial): Model event matches the GT event’s actors and action, but the time is wrong (different day or clearly not the same calendar moment).

These four buckets are mutually exclusive and must sum to the number of model events:
Correct + Wrong + Wrong event + Wrong date = Model

## MISSED (coverage on GT side)
Missed (FN) = Groundtruth − (Correct + Wrong event + Wrong date)
(Note: “Wrong” does NOT cover any GT event.)

## MATCHING POLICY
- One-to-one alignment: each model event can align to at most one GT event, and each GT event can be covered by at most one model event (via Correct, Wrong event, or Wrong date).
- Alignment priority when multiple candidates exist for a model event:
  1) Prefer Correct over Wrong date over Wrong event over Wrong.
  2) If two GT events could be Correct, choose the one with smallest time difference; if still tied, choose the one with the most overlapping actors; if still tied, pick the first in GT order.
- Event similarity:
  • Actors: names/entities must match or be an unambiguous alias.  
  • Action: verbs/objects must reflect the same real-world event (e.g., “Nerijus instructs Joseph to pick up Quan” ≈ “Instruction for Joseph to pick up Quan”).  
  • “Same situation/topic” for Wrong event means same participants/topic window (e.g., pickup/threat/payment) but key semantics flipped or materially wrong.
- Time rules:
  • Correct if identical timestamp OR clearly the same calendar moment (typically same day and unique).  
  • If actors/action match but time is off (e.g., different day), classify as Wrong date.  
  • If time matches but actors/action are wrong, classify as Wrong event (not Correct).

## NORMALIZATION & DEDUP
- Normalize names (trim spaces/case; treat obvious aliases as equal).
- Merge exact duplicate model events before scoring.
- If the model lists the same real-world event twice, only one can align to a GT event; the extra becomes Wrong.

## OUTPUT REQUIREMENTS
- Output exactly one CSV line with:
  Model,Groundtruth,Model,Correct,Wrong,Wrong event,Wrong date,Missed
- Model: use the exact <model-name> from the “MODEL:” line.
- Groundtruth: total number of GT events (rows) after normalization.
- Model: total number of model events (rows) after normalization.

## NOW EVALUATE
Return only the CSV line and a header line. Do not include explanations or quotes.

<BEGIN GROUNDTRUTH>
[PASTE the Groundtruth timeline table here]
<END GROUNDTRUTH>

MODEL: [PASTE MODEL NAME HERE]

<BEGIN MODEL TIMELINE>
[PASTE the Model timeline table here]
<END MODEL TIMELINE>
