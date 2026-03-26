import os
import pandas as pd
from rich.console import Console
from rich.table import Table
from meraki import DashboardAPI

def main():
    # Initialize the Meraki Dashboard API client
    api_key = os.getenv('MK_CSM_KEY')
    if not api_key:
        print("Environment variable MK_CSM_KEY not set.")
        return

    dashboard = DashboardAPI(api_key, suppress_logging=True)

    try:
        organizations = dashboard.organizations.getOrganizations()
    except Exception as e:
        print(f"Error fetching organizations list: {e}")
        return

    data = []
    strictest_orgs = []
    error_orgs = []
    min_timeout = float('inf')
    total_scanned = 0

    console = Console()
    table = Table(title="Organization Login Security Settings")

    table.add_column("Organization Name", style="cyan", no_wrap=True)
    table.add_column("Organization ID", style="magenta")
    table.add_column("URL", style="blue", overflow="fold")
    table.add_column("Enforce Idle Timeout", style="green")
    table.add_column("Idle Timeout Minutes", style="green")

    for org in organizations:
        total_scanned += 1
        org_id = org['id']
        org_name = org['name']
        org_url = org['url']

        if org_url.endswith('/overview'):
            org_url = org_url[:-len('/overview')] + '/edit?from=organization+settings'

        try:
            # Get login security settings
            login_security = dashboard.organizations.getOrganizationLoginSecurity(org_id)
            
            enforce = login_security.get("enforceIdleTimeout", False)
            timeout = login_security.get("idleTimeoutMinutes")

            # Logic for strictest timeout
            if enforce is True and timeout is not None:
                if timeout < min_timeout:
                    min_timeout = timeout
                    strictest_orgs = [org_name]
                elif timeout == min_timeout:
                    strictest_orgs.append(org_name)

            enforce_str = str(enforce)
            timeout_str = str(timeout) if timeout is not None else "N/A"

        except Exception as e:
            # Track organizations with data-reading issues
            error_orgs.append(f"{org_name} (ID: {org_id})")
            enforce_str = "[red]Error[/red]"
            timeout_str = "[red]Error[/red]"

        table.add_row(org_name, org_id, org_url, enforce_str, timeout_str)

        data.append({
            "Organization Name": org_name,
            "Organization ID": org_id,
            "URL": org_url,
            "Enforce Idle Timeout": enforce_str,
            "Idle Timeout Minutes": timeout_str
        })

    # Output results
    console.print(table)

    # Summary Report
    console.print("\n" + "="*30)
    console.print("[bold yellow]FINAL SUMMARY REPORT[/bold yellow]")
    console.print(f"Total Organizations Scanned: {total_scanned}")
    
    # 1. Strictest Timeout Report
    if strictest_orgs:
        org_list = ", ".join(strictest_orgs)
        console.print(f"[bold green]Lowest Idle Timeout Enforced:[/bold green] {min_timeout} minutes")
        console.print(f"[bold green]Organization(s):[/bold green] {org_list}")
    else:
        console.print("[red]No organization has idle timeout enforced.[/red]")

    # 2. Error Report
    if error_orgs:
        console.print(f"\n[bold red]Issues Reading Data ({len(error_orgs)}):[/bold red]")
        for entry in error_orgs:
            console.print(f" - {entry}")
    else:
        console.print("\n[bold green]All organizations were read successfully.[/bold green]")
    console.print("="*30 + "\n")

    # Excel Export
    df = pd.DataFrame(data)
    excel_file = "organization_login_security.xlsx"
    df.to_excel(excel_file, index=False)
    print(f"Excel file '{excel_file}' has been updated.")

if __name__ == "__main__":
    main()