# Evaluation Protocol

This protocol defines how to evaluate Hizawye AI’s GNW dynamics and learning behavior in a repeatable, testable way.

## Metrics Tracked
- **Ignition rate**: ignitions / total cycles
- **Persistence rate**: persisted content / total cycles
- **Median persistence run**: median length of persistent content runs
- **Module win rates**: wins by module / total cycles
- **Learning success rate**: learned concepts / total concepts attempted
- **Reflection frequency**: reflection events per 1,000 cycles

## Baseline Experiment
**Goal:** Establish stable metrics for current behavior.

1. Run with a fresh mind.
2. Let it run for a fixed time window (e.g., 5–10 minutes).
3. Generate reports with `python analyze.py --format reports`.
4. Record the metrics above into a report.

## Intervention Experiments
**Goal:** Test how architectural parameters change behavior.

- **Ignition Threshold Sweep**
  - Modify `Workspace.ignition_threshold` in `workspace.py`.
  - Compare ignition rate, persistence rate, and goal completion.

- **Competition Weights Sweep**
  - Adjust evidence/salience/novelty/urgency weights.
  - Measure shifts in dominant module and learning success.

## Ablation Experiments
**Goal:** Identify which modules are critical to learning and stability.

- **Perception Off**
  - Remove/disable `PerceptionModule`.
  - Expectation: higher goal execution rates.

- **Reflection Off**
  - Remove/disable `ReflectionModule`.
  - Expectation: more repeated failures, less strategy switching.

## Retention Test
**Goal:** Validate stability of learned concepts.

1. Learn a concept in a session.
2. Restart and query the same concept later.
3. Compare definition consistency and accuracy.

## Report Template
Use `reports/evaluation_template.md` to capture results.

## External Judge (Optional)
Use `evaluate_learning.py` to verify whether learned concepts are acceptable to a second model.

Example:
`python evaluate_learning.py --mode both --model <judge-model>`
