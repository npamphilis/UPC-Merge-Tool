# UPC Merge Tool (Fixed)

This tool merges a cleaned UPC list with a Partner Dashboard product file and returns an ingestion-ready output.

## Features
- Multi-tab Excel file support
- Header detection
- Barcode cleaning (no trailing zero bugs)
- Size and count parsing from description
- Category breakdown from any `>`-formatted column

## How to Use
Import the `clean_and_merge_upcs` function and call:

```python
from upc_merge_tool_barcode_fixed import clean_and_merge_upcs

merged = clean_and_merge_upcs("your_upc_file.xlsx", "partner_dashboard_file.xlsx")
merged.to_excel("merged_output.xlsx", index=False)
```
