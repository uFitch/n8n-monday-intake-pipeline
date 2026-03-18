# Field Mapping Reference

## Form → Monday.com Column Mapping

| Form Field | Monday.com Column | Type |
|------------|-------------------|------|
| company_name | company_name | Text |
| contact_email | contact_email | Email |
| project_title | project_title | Text |
| project_description | description | Long Text |
| development_stage | dev_stage | Status |
| budget_range | budget | Dropdown |
| timeline | timeline | Timeline |
| technical_requirements | tech_requirements | Long Text |
| file_uploads | files | File |

## Required Fields

- company_name
- contact_email
- project_title
- description
- dev_stage

## Adding a New Field

1. Add field in your form tool
2. Update scripts/field_mapping.py with new mapping
3. Add column in Monday.com
4. Update n8n workflow if custom processing needed