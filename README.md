# n8n-monday-intake-pipeline

Automated intake-to-project pipeline: web form → n8n orchestration → Monday.com project management with multi-phase routing.

![Pipeline](assets/pipeline-diagram.svg)

## What It Does

A complete workflow automation system that:

1. **Captures** structured intake submissions via webhook (compatible with Tally, Typeform, or custom forms)
2. **Processes** and validates incoming data through n8n
3. **Creates** organized project entries in Monday.com with mapped fields
4. **Notifies** internal team for review
5. **Routes** approved projects into multi-phase development workflow automatically

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Intake Form │────▶│  n8n Webhook │────▶│  Data Processing │────▶│ Monday.com  │
│  (Tally /    │     │  Trigger     │     │  & Validation    │     │ API         │
│  Typeform)   │     └─────────────┘     └──────────────────┘     └──────┬──────┘
└─────────────┘                                                          │
                                                                         ▼
                    ┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
                    │  Slack/Email │◀────│  Notification    │◀────│ Review Board │
                    │  Alert       │     │  Node            │     │ (Internal)   │
                    └─────────────┘     └──────────────────┘     └──────┬───────┘
                                                                        │
                                                              On Approval ▼
                                                                 ┌──────────────┐
                                                                 │ Multi-Phase  │
                                                                 │ Pipeline     │
                                                                 │ (Auto-setup) │
                                                                 └──────────────┘
```

## Tech Stack

| Component | Tool | Why |
|-----------|------|-----|
| Orchestration | n8n (self-hosted) | Visual workflows, unlimited executions, full control |
| Form | Tally / Typeform | Professional multi-step forms with file uploads |
| Project Management | Monday.com | Team visibility, native boards & automations |
| Notifications | Slack / Email | Real-time alerts for new submissions |
| Data Processing | Python (optional) | Complex validation or transformation logic |

## Project Structure

```
├── workflows/
│   ├── intake-webhook-processor.json     # Main n8n workflow
│   ├── approval-routing.json             # Review → pipeline routing
│   └── error-handler.json                # Error logging & alerts
├── scripts/
│   ├── monday_board_setup.py             # Auto-create Monday.com boards
│   └── field_mapping.py                  # Form fields → Monday.com columns
├── docs/
│   ├── SETUP.md                          # Installation & configuration
│   ├── FIELD_MAPPING.md                  # Data mapping reference
│   └── MONDAY_BOARD_STRUCTURE.md         # Board & column setup
└── assets/
    └── pipeline-diagram.svg              # Architecture diagram
```

## Quick Start

### Prerequisites

- n8n instance (self-hosted or cloud)
- Monday.com account with API token
- Form tool with webhook support (Tally, Typeform, etc.)

### 1. Set Up Monday.com Boards

```bash
# Install dependencies
pip install requests python-dotenv

# Configure your API token
cp .env.example .env
# Edit .env with your Monday.com API token

# Create board structure automatically
python scripts/monday_board_setup.py
```

### 2. Import n8n Workflows

Import the workflow JSON files from `workflows/` into your n8n instance:

1. Open n8n → Workflows → Import
2. Upload `intake-webhook-processor.json`
3. Upload `approval-routing.json`
4. Upload `error-handler.json`
5. Update credentials (Monday.com API token, Slack webhook)

### 3. Connect Your Form

Point your form's webhook to the n8n webhook URL:

```
https://your-n8n-instance.com/webhook/intake-form
```

### 4. Test

Submit a test entry through your form and verify:
- [ ] Monday.com item created with correct field mapping
- [ ] Team notification received
- [ ] Approval trigger works
- [ ] Pipeline phases auto-populate

## Field Mapping

| Form Field | Monday.com Column | Type |
|------------|-------------------|------|
| Company Name | `company_name` | Text |
| Contact Email | `contact_email` | Email |
| Project Title | `project_title` | Text |
| Project Description | `description` | Long Text |
| Development Stage | `dev_stage` | Status |
| Budget Range | `budget` | Dropdown |
| Timeline | `timeline` | Timeline |
| Technical Requirements | `tech_requirements` | Long Text |
| File Uploads | `files` | File |

## Customization

### Adding New Form Fields

1. Add the field in your form tool
2. Update `scripts/field_mapping.py` with the new mapping
3. Add corresponding column in Monday.com (or run `monday_board_setup.py`)
4. Update the n8n workflow to process the new field

### Modifying Pipeline Phases

Edit the `PIPELINE_PHASES` config in `scripts/monday_board_setup.py`:

```python
PIPELINE_PHASES = [
    {"name": "Intake Review", "color": "#FDAB3D"},
    {"name": "Discovery", "color": "#00C875"},
    {"name": "Design & Engineering", "color": "#0086C0"},
    {"name": "Prototyping", "color": "#A25DDC"},
    {"name": "Testing & QA", "color": "#E2445C"},
    {"name": "Production", "color": "#037F4C"},
]
```

## Error Handling

The pipeline includes built-in error handling:

- **Validation errors** → logged + admin notification
- **Monday.com API failures** → retry with exponential backoff (3 attempts)
- **Webhook timeout** → queued for reprocessing
- **Missing required fields** → form submission rejected with feedback

## License

MIT
