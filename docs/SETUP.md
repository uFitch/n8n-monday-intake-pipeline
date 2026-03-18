# Setup Guide

## Prerequisites

- n8n instance (self-hosted or cloud)
- Monday.com account with API token
- Form tool with webhook support (Tally, Typeform, etc.)
- Python 3.8+ (for board setup script)

## Step 1: Monday.com API Token

1. Go to Monday.com → Profile → Admin → API
2. Generate a personal API token
3. Copy the token

## Step 2: Environment Configuration
```bash
cp .env.example .env
# Edit .env with your Monday.com API token
```

## Step 3: Create Monday.com Boards
```bash
pip install requests python-dotenv
python scripts/monday_board_setup.py
```

Creates two boards: Intake Review and Project Pipeline.
Save the board IDs and add them to .env.

## Step 4: Import n8n Workflows

1. Open n8n → Workflows → Import from File
2. Import all JSON files from workflows/
3. Update credentials (Monday.com API token, Slack webhook)

## Step 5: Connect Your Form

Point your form webhook to:
```
https://your-n8n-instance.com/webhook/intake-form
```

## Step 6: Test

1. Submit a test entry through your form
2. Verify item appears in Monday.com
3. Change review status to Approved
4. Verify routing to Pipeline board