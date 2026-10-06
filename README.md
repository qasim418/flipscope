# FlipScope

**Find the flip. Check its stability.**

FlipScope explores single-feature edits that change a TabPFN prediction, checks their stability across training subsets, and reports fresh-subset validation separately. It includes notebook dashboards and MCP tools for querying saved experiment evidence.

## Requirements

- Git
- Python and pip
- VS Code with Python and Jupyter extensions for notebooks
- An MCP-compatible client, such as VS Code Copilot Agent, for the agent demo

The local MCP demo was verified on Windows with Python 3.14.2. Dependencies are pinned in `requirements.txt`; `pip check` passed in that environment.
## Install on Windows

Run in PowerShell:

```powershell
git clone https://github.com/qasim418/flipscope.git
cd flipscope
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m ipykernel install --user --name flipscope --display-name "Python (FlipScope)"
```

If `python` is unavailable, use the full path to your installed Python executable when creating the virtual environment.

Open the project in VS Code and select **Python (FlipScope)** as the notebook kernel.

## Saved-results demo

Saved evidence is included in `decision_probe_results/`. Querying it through MCP does not require a TabPFN API key or rerunning inference.

Start the server:

```powershell
.\.venv\Scripts\python.exe mcp_server.py
```

Keep this terminal running. The MCP endpoint is:

```text
http://127.0.0.1:8765/mcp
```

The root URL is not a webpage; a 404 at `/` is expected.

### Connect VS Code

The repository includes `.vscode/mcp.json`. Use **MCP: List Servers**, select **flipscope**, and start the connection. Accept any server trust prompt.

Open Copilot Chat in Agent mode and allow the FlipScope tools:

- `list_records`: list cached records and experiment metadata
- `find_edits`: search tested edits under user constraints
- `inspect_edit`: inspect an exact edit and its validation evidence

Try:

```text
Use only the FlipScope MCP tools. Do not read or modify project files.

For record 431, find the smallest tested edit with at least 80% search stability and at most 50% relative reduction.

Report the exact edit, search flip rate, and fresh-subset validation flip rate separately. Identify alternatives without validation.

Repeat with at most 40% relative reduction. If no tested edit qualifies, say so.
```

Expected saved result:

- Credit amount: 11328 → 6230, a 45.0035% reduction
- Search paired flip rate: 80%
- Fresh-subset validation paired flip rate: 60%
- At most 40% reduction: no qualifying tested edit

The selected edit meets the search requirement but falls below an 80% validation requirement.

## Reproduce the experiments

Obtain your own Prior Labs / TabPFN API key before running inference.

The notebook authentication cell checks `TABPFN_TOKEN`. If it is absent, it prompts for the key using `getpass`, which hides the input. Enter your key at that prompt. Do not put your key directly in notebook code or commit it.

Run notebooks in this order:

1. `01_decision_probe_experiments.ipynb`: baseline predictions, candidate edits, stability experiments, and synthetic validation.
2. `02_decision_probe_demo.ipynb`: interactive presentation of saved results.
3. `03_stable_decision_search.ipynb`: stability-constrained search, frozen-edit validation, and evidence queries.

For local use, replace any `/homes/mxqasim/Hackathon` paths with your local project directory. Check artifact paths before running cells that save results, and preserve the supplied evidence if you want to compare new runs against it.

The classifier uses the hosted default model through `TabPFNClassifier()`. Pinning the client version does not pin the server-selected model. New runs may therefore differ from the saved results and consume API quota.

## Results

The saved German Credit experiment uses 1,000 records, with 800 training and 200 held-out test records.

- Held-out ROC-AUC: 0.828
- Accuracy at threshold 0.50: 0.795
- Candidate edits tested: 1,485
- Records with a single-run tested flip: 29 of 45 high-risk records
- Frozen search-selected edits: 19
- Frozen edits reaching at least 8/10 paired flips on fresh subsets: 14 of 19

## Interpretation

A flip means the original prediction is at or above the 0.50 threshold and the edited prediction is below it.

“Smallest” means the smallest tested relative reduction among qualifying candidates, not a global minimum.

Search and validation use resampled subsets of the same training pool. Validation is not an external-dataset evaluation, and observed rates are not future-outcome guarantees.

Edits measure hypothetical model sensitivity. They do not establish causal effects, feasible financial actions, or lending recommendations. MCP tools query cached evidence; they do not predict outcomes for new applicants.
