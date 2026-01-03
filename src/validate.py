import pandas as pd
from pathlib import Path

DATA = Path("data/processed")

trials = pd.read_csv(DATA / "trials.csv")
conditions = pd.read_csv(DATA / "conditions.csv")
interventions = pd.read_csv(DATA / "interventions.csv")
arms = pd.read_csv(DATA / "arms.csv")
primary_outcomes = pd.read_csv(DATA / "primary_outcomes.csv")
secondary_outcomes = pd.read_csv(DATA / "secondary_outcomes.csv")
locations = pd.read_csv(DATA / "locations.csv")
sponsors = pd.read_csv(DATA / "sponsors.csv")
collaborators = pd.read_csv(DATA / "collaborators.csv")

arm_interventions_path = DATA / "arm_interventions.csv"
arm_interventions = (
    pd.read_csv(arm_interventions_path)
    if arm_interventions_path.exists()
    else None
)


def assert_nonempty(df, name):
    assert df is not None, f"{name} is None"
    assert len(df) > 0, f"{name} is empty"


def assert_required_nonnull(df, col, name):
    assert col in df.columns, f"{name}: missing required column {col}"
    assert df[col].notnull().all(), f"{name}: required column {col} has NULLs"
    blanks = df[col].dropna().astype(str).str.strip().eq("").sum()
    assert blanks == 0, f"{name}: required column {col} has blank strings"

def assert_composite_key_mostly_present(df, cols, name, max_null_rate=0.01):
    missing = set(cols) - set(df.columns)
    assert not missing, f"{name}: missing key columns {sorted(missing)}"

    # null-rate check per key column (soft)
    for c in cols:
        rate = df[c].isna().mean()
        assert rate <= max_null_rate, f"{name}: key column {c} null rate {rate:.2%} > {max_null_rate:.2%}"

    # uniqueness check only on rows where all key parts exist
    key_df = df.dropna(subset=cols)
    dupes = key_df.duplicated(subset=cols).sum()
    assert dupes == 0, f"{name}: {dupes} duplicate keys on {cols} (excluding NULL-key rows)"


def assert_no_complex_types(df, name):
    bad_cols = [
        c for c in df.columns
        if df[c].map(lambda x: isinstance(x, (dict, list))).any()
    ]
    assert not bad_cols, f"{name}: complex types in columns {bad_cols}"


def assert_fk(df, col, ref_keys, name):
    missing = set(df[col].dropna()) - ref_keys
    assert not missing, f"{name}: orphan values in {col} ({len(missing)})"


def assert_null_rate_below(df, col, max_rate, name):
    if col not in df.columns:
        return
    rate = df[col].isna().mean()
    assert rate <= max_rate, f"{name}.{col} null rate {rate:.2%} > {max_rate:.2%}"


for df, name in [
    (trials, "trials"),
    (conditions, "conditions"),
    (interventions, "interventions"),
    (arms, "arms"),
    (primary_outcomes, "primary_outcomes"),
    (secondary_outcomes, "secondary_outcomes"),
    (locations, "locations"),
    (sponsors, "sponsors"),
    (collaborators, "collaborators"),
    (arm_interventions, "arm_interventions")
]:
    assert_nonempty(df, name)


assert_required_nonnull(trials, "nct_id", "trials")
assert trials["nct_id"].is_unique, "trials: nct_id not unique"

assert_required_nonnull(conditions, "nct_id", "conditions")
assert_composite_key_mostly_present(conditions, ["nct_id", "condition"], "conditions", max_null_rate=0.01)

assert_required_nonnull(interventions, "nct_id", "interventions")


# allow some missing intervention_name; set a reasonable threshold (e.g., 5%)
assert_composite_key_mostly_present(
    interventions,
    ["nct_id", "intervention_name", "intervention_type"],
    "interventions",
    max_null_rate=0.05,
)

assert_required_nonnull(arms, "nct_id", "arms")
assert_composite_key_mostly_present(arms, ["nct_id", "arm_label"], "arms", max_null_rate=0.01)

assert_required_nonnull(primary_outcomes, "nct_id", "primary_outcomes")
assert_composite_key_mostly_present(
    primary_outcomes,
    ["nct_id", "outcome_measure", "time_frame"],
    "primary_outcomes",
    max_null_rate=0.10,  # outcomes/timeframes can be missing sometimes
)

assert_required_nonnull(secondary_outcomes, "nct_id", "secondary_outcomes")
assert_composite_key_mostly_present(
    secondary_outcomes,
    ["nct_id", "outcome_measure", "time_frame"],
    "secondary_outcomes",
    max_null_rate=0.10,
)

assert_required_nonnull(locations, "nct_id", "locations")
assert_composite_key_mostly_present(
    locations,
    ["nct_id", "facility_name", "city", "country"],
    "locations",
    max_null_rate=0.10,  # locations are messy; cities/ facilities can be missing
)



assert_required_nonnull(sponsors, "nct_id", "sponsors")

# sponsors is often 1 per trial; allow some missing sponsor name if dataset is incomplete
assert_composite_key_mostly_present(sponsors, ["nct_id", "lead_sponsor_name"], "sponsors", max_null_rate=0.05)

assert_required_nonnull(collaborators, "nct_id", "collaborators")
assert_composite_key_mostly_present(collaborators, ["nct_id", "collaborator_name"], "collaborators", max_null_rate=0.10)


trial_ids = set(trials["nct_id"])

for df, name in [
    (conditions, "conditions"),
    (interventions, "interventions"),
    (arms, "arms"),
    (primary_outcomes, "primary_outcomes"),
    (secondary_outcomes, "secondary_outcomes"),
    (locations, "locations"),
    (sponsors, "sponsors"),
    (collaborators, "collaborators"),
]:
    assert_fk(df, "nct_id", trial_ids, name)

if arm_interventions is not None:
    # schema
    required = {"nct_id", "arm_label", "intervention_name"}
    missing = required - set(arm_interventions.columns)
    assert not missing, f"arm_interventions missing columns {missing}"

    # FK integrity, it's foreign key refers to arms[nct_id, arm_label] table
    if len(arm_interventions) > 0:
        arm_keys = set(zip(arms["nct_id"], arms["arm_label"]))
        bridge_keys = set(
            zip(arm_interventions["nct_id"], arm_interventions["arm_label"])
        )
        missing = bridge_keys - arm_keys
        assert not missing, "arm_interventions has unknown arm references"

for df, name in [
    (trials, "trials"),
    (conditions, "conditions"),
    (interventions, "interventions"),
    (arms, "arms"),
    (primary_outcomes, "primary_outcomes"),
    (secondary_outcomes, "secondary_outcomes"),
    (locations, "locations"),
    (sponsors, "sponsors"),
    (collaborators, "collaborators"),
]:
    assert_no_complex_types(df, name)

if arm_interventions is not None:
    assert_no_complex_types(arm_interventions, "arm_interventions")


assert_null_rate_below(trials, "overall_status", 0.05, "trials")
assert_null_rate_below(trials, "study_type", 0.05, "trials")
assert_null_rate_below(trials, "brief_title", 0.10, "trials")


t = trials.copy()
t["start_date"] = pd.to_datetime(t.get("start_date"), errors="coerce")
t["completion_date"] = pd.to_datetime(t.get("completion_date"), errors="coerce")

bad = t.dropna(subset=["start_date", "completion_date"])
bad = bad[bad["completion_date"] < bad["start_date"]]
assert bad.empty, f"{len(bad)} trials have completion_date < start_date"

if "primary_completion_date" in t.columns:
    t["primary_completion_date"] = pd.to_datetime(
        t["primary_completion_date"], errors="coerce"
    )
    bad2 = t.dropna(subset=["start_date", "primary_completion_date"])
    bad2 = bad2[bad2["primary_completion_date"] < bad2["start_date"]]
    assert bad2.empty, (
        f"{len(bad2)} trials have primary_completion_date < start_date"
    )



print("Validation passed")