# FlipScope

Find the flip. Check its stability.

FlipScope explores single-feature changes that flip TabPFN predictions, searches for edits meeting an observed stability requirement, and reports fresh-subset validation separately.

The project includes German Credit experiments, synthetic ground-truth validation, interactive notebook dashboards, and MCP tools for querying cached evidence.

## Notebooks

- `01_decision_probe_experiments.ipynb`: baseline predictions, initial flip search, and synthetic validation.
- `02_decision_probe_demo.ipynb`: initial results explorer.
- `03_stable_decision_search.ipynb`: full candidate stability search, fresh-subset validation, dashboard, and MCP checks.

## Results

- Baseline ROC-AUC: 0.828; accuracy: 79.5%.
- 1,485 candidate edits across 45 predicted high-risk records.
- 19 records had an edit meeting 8/10 search-subset flips.
- 14 of those 19 frozen edits met 8/10 flips on fresh validation subsets.

## Model and scope

Experiments used the TabPFN hosted API with automatic default model selection and tabpfn-client 0.6.1. The exact server model version was not recorded.

The MCP tools query saved experiments; they do not perform inference for new records. Stability rates describe resampling of the same training pool. Edits are hypothetical model sensitivity tests, not causal effects or financial recommendations.
