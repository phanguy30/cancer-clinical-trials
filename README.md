# Clinical Cancer Trials Dataset

This project builds a reproducible data pipeline for clinical cancer trials
using the ClinicalTrials.gov REST API (v2).

The dataset contains over 130,000 trials retrieved by querying the term
**"cancer"**, and is normalized into multiple relational tables suitable for
analysis.

## Data Source

- ClinicalTrials.gov API v2
- Query term: `cancer`
- Data retrieved via paginated REST requests

The raw API responses are downloaded as JSON and transformed into a structured
relational schema.

## Pipeline Overview

1. **Download**
   - `download_trials.py` retrieves all matching studies from the API.

2. **Parsing / Transformation**
   - `parse_trials.ipynb` extracts relevant fields from the nested JSON and
     normalizes them into multiple tables (trials, conditions, interventions,
     arms, outcomes, locations, sponsors, etc.).

3. **Validation**
   - `validate.py` checks internal consistency and integrity of the dataset,
     including:
     - primary identifiers (`nct_id`)
     - foreign key relationships across tables
     - schema consistency
     - absence of complex (dict/list) types for each attribute
     - null-rate thresholds for key fields
     - basic date consistency checks

4. **Analysis / Visualization**
   - Example analyses and visualizations are provided in notebooks and scripts.

## Data Model

The dataset is normalized into a relational schema.
An Entity–Relationship Diagram (ERD) is provided below to illustrate table
structure and relationships.

Key design decisions:
- One row per trial in the `trials` table.
- Many-to-many relationships (e.g. arms ↔ interventions) are modeled using
  bridge tables.
## Notes on Data Quality

- Some fields that are composite primary keys may contain NULL values.
  This reflects inconsistencies in how trials are reported in the registry.
- Null rates for key descriptive fields are constrained via validation
  (typically ≤ 5%).
- Duplicate entries may appear in source data (e.g. locations or interventions);
  these are handled explicitly during parsing and validation.


## Requirements

Dependencies are listed in `requirements.txt`.

## Reproducibility

To reproduce the dataset from scratch:

```bash
python src/download_trials.py
jupyter notebook src/parse_trials.ipynb
python src/validate.py
```

```mermaid
erDiagram
  TRIALS {
    string nct_id PK
    string brief_title
    string official_title
    string overall_status
    date start_date
    date primary_completion_date
    date completion_date
    string study_type
    string phases
  }

  CONDITIONS {
    string nct_id FK
    string condition
  }

  INTERVENTIONS {
    string nct_id FK
    string intervention_type
    string intervention_name
  }

  ARMS {
    string nct_id FK
    string arm_label
    string arm_type
  }

  ARM_INTERVENTIONS {
    string nct_id FK
    string arm_label FK
    string intervention_name
  }

  PRIMARY_OUTCOMES {
    string nct_id FK
    string outcome_measure
    string time_frame
  }

  SECONDARY_OUTCOMES {
    string nct_id FK
    string outcome_measure
    string time_frame
  }

  LOCATIONS {
    string nct_id FK
    string facility_name
    string city
    string country
  }

  SPONSORS {
    string nct_id FK
    string lead_sponsor_name
    string lead_sponsor_class
  }

  COLLABORATORS {
    string nct_id FK
    string collaborator_name
    string collaborator_class
  }

  TRIALS ||--o{ CONDITIONS : has
  TRIALS ||--o{ INTERVENTIONS : has
  TRIALS ||--o{ ARMS : has
  TRIALS ||--o{ PRIMARY_OUTCOMES : has
  TRIALS ||--o{ SECONDARY_OUTCOMES : has
  TRIALS ||--o{ LOCATIONS : has
  TRIALS ||--o{ SPONSORS : has
  TRIALS ||--o{ COLLABORATORS : has

  ARMS ||--o{ ARM_INTERVENTIONS : maps
  INTERVENTIONS ||--o{ ARM_INTERVENTIONS : used_in
