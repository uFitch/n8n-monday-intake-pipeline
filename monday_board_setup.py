"""
Monday.com Board Setup Script
Automatically creates the board structure for the intake pipeline.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

MONDAY_API_URL = "https://api.monday.com/v2"
MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")

HEADERS = {
    "Authorization": MONDAY_API_TOKEN,
    "Content-Type": "application/json",
}

# === CONFIGURATION ===

REVIEW_BOARD = {
    "name": "Intake Review",
    "columns": [
        {"title": "Company Name", "type": "text", "id": "company_name"},
        {"title": "Contact Email", "type": "email", "id": "contact_email"},
        {"title": "Project Title", "type": "text", "id": "project_title"},
        {"title": "Description", "type": "long_text", "id": "description"},
        {"title": "Development Stage", "type": "status", "id": "dev_stage"},
        {"title": "Budget Range", "type": "dropdown", "id": "budget"},
        {"title": "Timeline", "type": "timeline", "id": "timeline"},
        {"title": "Technical Requirements", "type": "long_text", "id": "tech_requirements"},
        {"title": "Files", "type": "file", "id": "files"},
        {"title": "Review Status", "type": "status", "id": "review_status"},
        {"title": "Reviewer", "type": "people", "id": "reviewer"},
        {"title": "Submitted At", "type": "date", "id": "submitted_at"},
    ],
    "groups": [
        {"title": "New Submissions", "color": "#FDAB3D"},
        {"title": "Under Review", "color": "#0086C0"},
        {"title": "Approved", "color": "#00C875"},
        {"title": "Rejected", "color": "#E2445C"},
    ],
}

PIPELINE_PHASES = [
    {"name": "Discovery", "color": "#00C875"},
    {"name": "Design & Engineering", "color": "#0086C0"},
    {"name": "Prototyping", "color": "#A25DDC"},
    {"name": "Testing & QA", "color": "#E2445C"},
    {"name": "Production", "color": "#037F4C"},
    {"name": "Completed", "color": "#00C875"},
]

PIPELINE_BOARD = {
    "name": "Project Pipeline",
    "columns": [
        {"title": "Company Name", "type": "text", "id": "company_name"},
        {"title": "Contact Email", "type": "email", "id": "contact_email"},
        {"title": "Phase", "type": "status", "id": "phase"},
        {"title": "Assigned To", "type": "people", "id": "assigned_to"},
        {"title": "Priority", "type": "status", "id": "priority"},
        {"title": "Due Date", "type": "date", "id": "due_date"},
        {"title": "Progress", "type": "numbers", "id": "progress"},
        {"title": "Notes", "type": "long_text", "id": "notes"},
        {"title": "Files", "type": "file", "id": "files"},
    ],
    "groups": [{"title": phase["name"], "color": phase["color"]} for phase in PIPELINE_PHASES],
}


def monday_query(query: str, variables: dict = None) -> dict:
    """Execute a Monday.com GraphQL query."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(MONDAY_API_URL, json=payload, headers=HEADERS)
    response.raise_for_status()

    data = response.json()
    if "errors" in data:
        raise Exception(f"Monday.com API error: {data['errors']}")

    return data


def create_board(name: str, workspace_id: str = None) -> str:
    """Create a new board and return its ID."""
    workspace_clause = f', workspace_id: {workspace_id}' if workspace_id else ''
    query = f'''
    mutation {{
        create_board(
            board_name: "{name}",
            board_kind: private
            {workspace_clause}
        ) {{
            id
        }}
    }}
    '''
    result = monday_query(query)
    board_id = result["data"]["create_board"]["id"]
    print(f"  Created board '{name}' (ID: {board_id})")
    return board_id


def create_column(board_id: str, title: str, column_type: str, col_id: str) -> None:
    """Add a column to a board."""
    query = f'''
    mutation {{
        create_column(
            board_id: {board_id},
            title: "{title}",
            column_type: {column_type},
            id: "{col_id}"
        ) {{
            id
        }}
    }}
    '''
    try:
        monday_query(query)
        print(f"    + Column: {title} ({column_type})")
    except Exception as e:
        print(f"    ! Column '{title}' may already exist: {e}")


def create_group(board_id: str, group_name: str) -> str:
    """Create a group in a board."""
    query = f'''
    mutation {{
        create_group(
            board_id: {board_id},
            group_name: "{group_name}"
        ) {{
            id
        }}
    }}
    '''
    result = monday_query(query)
    group_id = result["data"]["create_group"]["id"]
    print(f"    + Group: {group_name}")
    return group_id


def setup_board(config: dict, workspace_id: str = None) -> str:
    """Set up a complete board with columns and groups."""
    print(f"\nSetting up board: {config['name']}")
    print("-" * 40)

    board_id = create_board(config["name"], workspace_id)

    print("  Adding columns:")
    for col in config["columns"]:
        create_column(board_id, col["title"], col["type"], col["id"])

    print("  Adding groups:")
    for group in config["groups"]:
        create_group(board_id, group["title"])

    return board_id


def main():
    """Set up the complete Monday.com board structure."""
    if not MONDAY_API_TOKEN:
        print("Error: MONDAY_API_TOKEN not set in .env")
        print("Copy .env.example to .env and add your token.")
        return

    workspace_id = os.getenv("DEFAULT_WORKSPACE_ID")

    print("=" * 50)
    print("Monday.com Board Setup")
    print("=" * 50)

    # Create Review Board
    review_board_id = setup_board(REVIEW_BOARD, workspace_id)

    # Create Pipeline Board
    pipeline_board_id = setup_board(PIPELINE_BOARD, workspace_id)

    print("\n" + "=" * 50)
    print("Setup Complete!")
    print("=" * 50)
    print(f"\nReview Board ID:   {review_board_id}")
    print(f"Pipeline Board ID: {pipeline_board_id}")
    print(f"\nAdd these IDs to your .env file and n8n credentials.")


if __name__ == "__main__":
    main()
