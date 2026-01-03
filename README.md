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