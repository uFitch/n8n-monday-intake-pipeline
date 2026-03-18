"""
Field Mapping Module
Maps incoming form data to Monday.com column values.
Used by n8n Function nodes or standalone processing.
"""

from datetime import datetime
from typing import Any


# === FORM FIELD → MONDAY.COM COLUMN MAPPING ===

FIELD_MAP = {
    # Form field key          → Monday.com column ID
    "company_name":            "company_name",
    "company":                 "company_name",       # alias
    "contact_email":           "contact_email",
    "email":                   "contact_email",      # alias
    "project_title":           "project_title",
    "title":                   "project_title",      # alias
    "project_description":     "description",
    "description":             "description",        # alias
    "development_stage":       "dev_stage",
    "dev_stage":               "dev_stage",          # alias
    "budget_range":            "budget",
    "budget":                  "budget",             # alias
    "timeline":                "timeline",
    "technical_requirements":  "tech_requirements",
    "tech_requirements":       "tech_requirements",  # alias
    "file_uploads":            "files",
    "files":                   "files",              # alias
}

# Valid development stages (must match Monday.com status labels)
VALID_DEV_STAGES = [
    "Idea / Concept",
    "Design Phase",
    "Prototype Ready",
    "Testing Phase",
    "Production Ready",
]

# Valid budget ranges
VALID_BUDGETS = [
    "Under $10K",
    "$10K - $50K",
    "$50K - $100K",
    "$100K - $500K",
    "$500K+",
]

# Required fields for a valid submission
REQUIRED_FIELDS = [
    "company_name",
    "contact_email",
    "project_title",
    "description",
    "dev_stage",
]


def normalize_field_name(field_name: str) -> str:
    """Convert form field name to Monday.com column ID."""
    clean = field_name.strip().lower().replace(" ", "_").replace("-", "_")
    return FIELD_MAP.get(clean, clean)


def validate_submission(data: dict) -> dict:
    """
    Validate incoming form data.
    Returns: {"valid": bool, "errors": list, "mapped_data": dict}
    """
    errors = []
    mapped = {}

    for key, value in data.items():
        col_id = normalize_field_name(key)
        if value is not None and str(value).strip():
            mapped[col_id] = str(value).strip()

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in mapped or not mapped[field]:
            errors.append(f"Missing required field: {field}")

    # Validate email format
    email = mapped.get("contact_email", "")
    if email and "@" not in email:
        errors.append(f"Invalid email format: {email}")

    # Validate dev stage
    stage = mapped.get("dev_stage", "")
    if stage and stage not in VALID_DEV_STAGES:
        errors.append(
            f"Invalid development stage: '{stage}'. "
            f"Must be one of: {', '.join(VALID_DEV_STAGES)}"
        )

    # Add metadata
    mapped["submitted_at"] = datetime.utcnow().isoformat()
    mapped["review_status"] = "New"

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "mapped_data": mapped,
    }


def to_monday_column_values(mapped_data: dict) -> dict:
    """
    Convert mapped data to Monday.com column_values format.
    Ready to use in Monday.com API create_item mutation.
    """
    column_values = {}

    for col_id, value in mapped_data.items():
        if col_id == "contact_email":
            column_values[col_id] = {"email": value, "text": value}
        elif col_id == "submitted_at":
            column_values[col_id] = {"date": value[:10]}
        elif col_id in ("dev_stage", "review_status"):
            column_values[col_id] = {"label": value}
        elif col_id == "budget":
            column_values[col_id] = {"labels": [value]}
        elif col_id in ("description", "tech_requirements"):
            column_values[col_id] = {"text": value}
        elif col_id == "files":
            continue  # Files handled separately via Monday.com file upload API
        else:
            column_values[col_id] = value

    return column_values


# === FOR USE IN N8N FUNCTION NODES ===
# Copy the logic below into n8n Function node if not using Python directly

N8N_FUNCTION_CODE = """
// n8n Function Node: Map form fields to Monday.com columns
const formData = $input.first().json;

const fieldMap = {
  'company_name': 'company_name',
  'company': 'company_name',
  'contact_email': 'contact_email',
  'email': 'contact_email',
  'project_title': 'project_title',
  'title': 'project_title',
  'project_description': 'description',
  'description': 'description',
  'development_stage': 'dev_stage',
  'budget_range': 'budget',
  'timeline': 'timeline',
  'technical_requirements': 'tech_requirements',
  'file_uploads': 'files',
};

const requiredFields = ['company_name', 'contact_email', 'project_title', 'description', 'dev_stage'];

const mapped = {};
const errors = [];

for (const [key, value] of Object.entries(formData)) {
  const cleanKey = key.trim().toLowerCase().replace(/[\\s-]/g, '_');
  const colId = fieldMap[cleanKey] || cleanKey;
  if (value && String(value).trim()) {
    mapped[colId] = String(value).trim();
  }
}

for (const field of requiredFields) {
  if (!mapped[field]) {
    errors.push(`Missing required field: ${field}`);
  }
}

mapped.submitted_at = new Date().toISOString();
mapped.review_status = 'New';

return [{
  json: {
    valid: errors.length === 0,
    errors,
    mapped_data: mapped
  }
}];
"""


if __name__ == "__main__":
    # Test with sample data
    sample = {
        "Company Name": "Acme Corp",
        "Email": "john@acme.com",
        "Project Title": "Smart Widget v2",
        "Project Description": "IoT-enabled widget with BLE connectivity",
        "Development Stage": "Prototype Ready",
        "Budget Range": "$50K - $100K",
        "Technical Requirements": "Must support BLE 5.0, IP67 rated",
    }

    result = validate_submission(sample)
    print(f"Valid: {result['valid']}")
    print(f"Errors: {result['errors']}")
    print(f"Mapped: {result['mapped_data']}")

    if result["valid"]:
        col_values = to_monday_column_values(result["mapped_data"])
        print(f"\nMonday.com column_values:")
        import json
        print(json.dumps(col_values, indent=2))
