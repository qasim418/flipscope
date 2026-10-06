import json, math
from pathlib import Path
from mcp.server import MCPServer

ROOT = Path(__file__).resolve().parent
EVIDENCE_PATH = ROOT / "decision_probe_results/stable_search_412b57d59795/decision_probe_evidence.json"
if not EVIDENCE_PATH.exists():
    raise FileNotFoundError(f"Evidence file missing: {EVIDENCE_PATH}")

evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
records = {row["record_id"]: row for row in evidence["records"]}
mcp = MCPServer("FlipScope")

def attach_validation(candidate):
    result = dict(candidate)
    matches = [
        row for row in evidence["validation"]
        if row["record_id"] == candidate["record_id"] and row["feature"] == candidate["feature"]
        and math.isclose(row["new_value"], candidate["new_value"], rel_tol=0, abs_tol=1e-8)
    ]
    result["validation"] = (
        {"status": "tested", **matches[0]} if matches
        else {"status": "not_tested", "reason": "This exact edit was not included in frozen validation."}
    )
    return result

@mcp.tool()
def list_records() -> dict:
    """List cached high-risk records and experiment metadata."""
    return {"metadata": evidence["metadata"], "records": evidence["records"]}

@mcp.tool()
def find_edits(record_id: int, minimum_stability: float = 0.8,
               maximum_reduction: float = 1.0, feature: str = "either",
               require_margin: bool = False, limit: int = 5) -> dict:
    """Find smallest tested edits meeting SEARCH stability and reduction limits.
    Rates are fractions from 0 to 1. Report validation separately; never infer
    validation for an untested edit. These are hypothetical cached sensitivity tests.
    """
    if record_id not in records:
        raise ValueError("Unknown record_id. Use list_records().")
    if not math.isfinite(minimum_stability) or not 0 < minimum_stability <= 1:
        raise ValueError("minimum_stability must be in (0, 1].")
    if not math.isfinite(maximum_reduction) or not 0 < maximum_reduction <= 1:
        raise ValueError("maximum_reduction must be in (0, 1].")
    if feature not in ("either", "credit_amount", "duration"):
        raise ValueError("feature must be either, credit_amount, or duration.")
    if not 1 <= limit <= 20:
        raise ValueError("limit must be between 1 and 20.")
    metric = "margin_flip_rate" if require_margin else "paired_flip_rate"
    eligible = [
        row for row in evidence["candidates"]
        if row["record_id"] == record_id and row[metric] >= minimum_stability
        and row["relative_reduction"] <= maximum_reduction + 1e-9
        and (feature == "either" or row["feature"] == feature)
    ]
    eligible.sort(key=lambda row: (
        row["relative_reduction"], -row[metric], row["mean_modified_p"], row["feature"]
    ))
    return {
        "status": "found" if eligible else "no_qualifying_tested_edit",
        "record": records[record_id],
        "constraints": {"minimum_search_stability": minimum_stability,
                        "maximum_reduction": maximum_reduction, "feature": feature,
                        "require_margin": require_margin},
        "qualifying_count": len(eligible),
        "edits": [attach_validation(row) for row in eligible[:limit]],
        "limitations": [
            "Search and validation use subsets of the same training pool.",
            "Validation rates describe threshold crossings, not the margin criterion.",
            "Relative reduction is not a measure of real-world feasibility.",
            "Cached results; no predictions for new records or causal guarantees."
        ]
    }

@mcp.tool()
def inspect_edit(candidate_id: int) -> dict:
    """Inspect search results and exact-edit validation evidence."""
    matches = [row for row in evidence["candidates"] if row["candidate_id"] == candidate_id]
    if not matches:
        raise ValueError("Unknown candidate_id.")
    return attach_validation(matches[0])

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8765)