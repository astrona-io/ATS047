# Reusable Question Banks

`assessments/index.yaml` lists banks in teaching order. Each bank uses schema
version 1 and the contract in `schemas/question-bank.schema.json`. This is an
authoring format for future application integration, not an existing Astrona
quiz API. No YAML question file is registered as a Markdown reading.

Banks follow their declared module summaries. Larger domains use an intermediate
checkpoint after the third section and a final domain review; smaller domains
use a final domain review. The index records covered sections and teaching order. Banks contain 5–15 original single-choice
questions, scoped to concepts taught in the course. They remain draft for review.

## Fields And Rendering

- `id`: stable bank or question identity; preserve it when editing wording.
- `scope`: section or domain checkpoint.
- `placement`: relative reading path after which the checkpoint belongs.
- `learning_objective`: the measurable outcome checked by the question.
- `source_readings`: author traceability to the teaching; not learner navigation.
- `prompt`: learner-visible question text.
- `options`: stable option IDs, answer text and per-option feedback.
- `correct_option`: the ID of the single correct option.
- `explanation`: feedback reinforcing the supported answer.

The application should send only the question ID, prompt and option IDs/text to
the learner before submission. Keep `correct_option`, `explanation` and option
explanations on the server until feedback is permitted. Match answers by option
ID, not display position, so a later renderer can shuffle choices safely.

The banks contain answer keys and are public learning material, so this is not
a secure examination bank. Do not treat scores as an official PCA result.

## Hands-On Coverage

This course has 6 ungraded playgrounds and 6 independent draft labs. Tasks, launch entries and solutions follow their teaching reading. Guided practice precedes the summary. Static and offline checks are separate from live execution, which remains pending.

| Module | Labs in reading order |
| --- | --- |
| 010/01 | Distinguish A Counter From A Gauge |
| 020/01 | Correlate A Request Log With Its Response |
| 030/01 | Carry Trace Context Into A Logged Span |
| 040/01 | Observe A Pulled Target |
| 050/01 | Inspect Discovered Target Labels |
| 060/01 | Calculate A Traffic Weighted Error Ratio |
