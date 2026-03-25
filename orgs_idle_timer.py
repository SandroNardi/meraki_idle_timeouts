import os
import pandas as pd
from rich.console import Console
from rich.table import Table
from meraki import DashboardAPI

def main():
    # Initialize the Meraki Dashboard API client using the API key from environment variable MK_CSM_KEY
    api_key = os.getenv('MK_CSM_KEY')
    if not api_key:
        print("Environment variable MK_CSM_API not set.")
        return

    dashboard = DashboardAPI(api_key, suppress_logging=True)

    # Get all organizations accessible by the API key
    organizations = dashboard.organizations.getOrganizations()

    # Prepare data list for table and Excel
    data = []

    # Console table setup using rich
    console = Console()
    table = Table(title="Organization Login Security Settings")

    table.add_column("Organization Name", style="cyan", no_wrap=True)
    table.add_column("Organization ID", style="magenta")
    table.add_column("URL", style="blue", overflow="fold")
    table.add_column("Enforce Idle Timeout", style="green")
    table.add_column("Idle Timeout Minutes", style="green")

    for org in organizations:
        org_id = org['id']
        org_name = org['name']
        org_url = org['url']

        # Substitute trailing '/overview' with '/edit?from=organization+settings' in the URL
        if org_url.endswith('/overview'):
            org_url = org_url[:-len('/overview')] + '/edit?from=organization+settings'

        # Get login security settings for the organization
        login_security = dashboard.organizations.getOrganizationLoginSecurity(org_id)

        enforce_idle_timeout = str(login_security.get("enforceIdleTimeout", "N/A"))
        idle_timeout_minutes = str(login_security.get("idleTimeoutMinutes", "N/A"))

        # Add row to rich table
        table.add_row(org_name, org_id, org_url, enforce_idle_timeout, idle_timeout_minutes)

        # Append to data list for Excel
        data.append({
            "Organization Name": org_name,
            "Organization ID": org_id,
            "URL": org_url,
            "Enforce Idle Timeout": enforce_idle_timeout,
            "Idle Timeout Minutes": idle_timeout_minutes
        })

    # Print the table to console
    console.print(table)

    # Create a DataFrame and write to Excel, overwrite if exists
    df = pd.DataFrame(data)
    excel_file = "organization_login_security.xlsx"
    df.to_excel(excel_file, index=False)
    print(f"Excel file '{excel_file}' has been created/overwritten with the organization login security data.")

if __name__ == "__main__":
    main()