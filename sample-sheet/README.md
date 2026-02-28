# Sample Google Sheet Input

Import these CSVs into a Google Sheet to create your dashboard input.

## Steps

1. Create a new Google Sheet: [sheets.new](https://sheets.new)
2. Create a sheet tab named **Stocks** (or rename Sheet1)
3. Paste or import `Stocks.csv` - ensure headers are in row 1, data from row 2
4. Create a second sheet tab named **YouTube**
5. Paste or import `YouTube.csv`

## Format

### Stocks sheet
- **Symbol**: Stock ticker (e.g., AAPL, MSFT)
- **Name**: Company name
- **Avg Price**: Your average buy price
- **Qty**: Number of shares held

### YouTube sheet
- **Channel Name**: Display name (e.g., @FinancialEducation)
- **Channel ID or Handle**: Either the full channel ID (UC...) or @handle. Get the ID from the channel's About page URL.

## Spreadsheet ID

Copy the ID from your sheet URL:
```
https://docs.google.com/spreadsheets/d/THIS_IS_YOUR_ID/edit
```

## Sharing

Share the sheet with your **Google Service Account** email (from credentials.json) with **Viewer** access so the app can read the data.
