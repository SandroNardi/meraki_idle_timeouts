## Meraki Org Idle Timeout Checker

This project helps you find discrepancies in Meraki Dashboard login security settings across different organizations—specifically the `idleTimeoutMinutes` and whether `enforceIdleTimeout` is enabled.

Why it exists: when you administer multiple orgs, the effective idle-timeout behavior you experience can effectively be constrained by the minimum configured idle timeout across those orgs. By pulling the configured values per org, you can quickly spot mismatches.

### What it does

1. Reads the organizations accessible to your Meraki Dashboard API key.
2. For each org, fetches login security settings.
3. Prints a table to the console and writes an Excel file you can compare.

### Prerequisites

- Python 3
- A Meraki Dashboard API key
- `MK_CSM_KEY` environment variable set to your API key

Install dependencies:

```powershell
pip install meraki pandas rich openpyxl
```

### Usage

```powershell
$env:MK_CSM_KEY="YOUR_API_KEY"
python .\orgs_idle_timer.py
```

### Output

- Console table with columns: `Organization Name`, `Organization ID`, `URL`, `Enforce Idle Timeout`, `Idle Timeout Minutes`
- Excel file: `organization_login_security.xlsx`

## License

MIT (see `LICENSE`)

