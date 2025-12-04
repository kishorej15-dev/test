# exporter.py
import pandas as pd
from datetime import datetime
from data_processor import DataProcessor

class MetricsExporter:
    @staticmethod
    def create_excel(raw_data: dict, metrics: dict, filename: str) -> bool:
        print(f"\nCreating Excel: {filename}")
        try:
            with pd.ExcelWriter(filename, engine="openpyxl") as writer:
                MetricsExporter._create_dashboard(writer, metrics)
                for name, df in raw_data.items():
                    if df is None or df.empty:
                        continue
                    safe_name = name[:31]
                    df_clean = DataProcessor.remove_all_timezones(df)
                    df_clean.to_excel(writer, sheet_name=safe_name, index=False)
                    print(f"  ✓ {safe_name}: {len(df)} rows")
            print("Excel created.")
            return True
        except Exception as e:
            print(f"Excel creation failed: {e}")
            return False

    @staticmethod
    def _create_dashboard(writer, metrics: dict):
        data = []
        data.append(["ZOHO BIGIN ANALYTICS DASHBOARD", "", ""])
        data.append(["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ""])
        data.append(["Period:", metrics["summary"].get("date_range", "N/A"), ""])
        data.append(["", "", ""])
        data.append(["SUMMARY OVERVIEW", "", ""])
        data.append(["Total Contacts", metrics["summary"]["total_contacts"], ""])
        data.append(["Total Accounts", metrics["summary"]["total_accounts"], ""])
        data.append(["Total Deals", metrics["summary"]["total_deals"], ""])
        data.append(["Total Calls", metrics["summary"]["total_calls"], ""])
        data.append(["Total Meetings", metrics["summary"]["total_meetings"], ""])
        data.append(["", "", ""])
        data.append(["LEAD SOURCE DISTRIBUTION", "", ""])
        ls = metrics["lead_source"]
        if isinstance(ls, pd.DataFrame) and not ls.empty:
            for _, row in ls.iterrows():
                data.append([row["Lead_Source"], row["Count"], f"{row['Percentage']}%"])
        else:
            data.append(["No data available", "", ""])
        data.append(["", "", ""])
        data.append(["INDUSTRY DISTRIBUTION", "", ""])
        it = metrics["industry_type"]
        if isinstance(it, pd.DataFrame) and not it.empty:
            for _, row in it.iterrows():
                data.append([row["Industry"], row["Count"], f"{row['Percentage']}%"])
        else:
            data.append(["No data available", "", ""])
        data.append(["", "", ""])
        data.append(["MEETING METRICS", "", ""])
        data.append(["Total Meetings", metrics["meetings"]["total_meetings"], ""])
        data.append(["Avg per Day", metrics["meetings"]["avg_meetings_per_day"], ""])
        data.append(["", "", ""])
        data.append(["CALL ACTIVITY", "", ""])
        data.append(["Total Calls", metrics["calls"]["total_calls"], ""])
        data.append(["Avg per Day", metrics["calls"]["avg_calls_per_day"], ""])
        data.append(["", "", ""])
        data.append(["LEAD QUALITY SEGMENTATION", "", ""])
        data.append(["Total Leads", metrics["lead_quality"]["total_leads"], ""])
        data.append(["Junk", metrics["lead_quality"]["junk_leads"], ""])
        data.append(["Prospect", metrics["lead_quality"]["prospect_leads"], ""])
        data.append(["Qualified", metrics["lead_quality"]["qualified_leads"], ""])
        data.append(["", "", ""])
        data.append(["QUOTE METRICS", "", ""])
        data.append(["Total Quotes", metrics["quotes"]["total_quotes"], ""])
        data.append(["Total Value", metrics["quotes"]["total_quote_value"], ""])
        data.append(["Avg Value", metrics["quotes"]["average_quote_value"], ""])
        data.append(["", "", ""])
        data.append(["DEAL METRICS", "", ""])
        data.append(["Total Deals", metrics["deals"]["total_deals"], ""])
        data.append(["Deals Won", metrics["deals"]["deals_won"], ""])
        data.append(["Win Rate", metrics["deals"]["win_rate"], ""])
        df = pd.DataFrame(data, columns=["Metric", "Value", "Details"])
        df.to_excel(writer, sheet_name="Dashboard", index=False)
        ws = writer.sheets["Dashboard"]
        ws.column_dimensions["A"].width = 40
        ws.column_dimensions["B"].width = 20
        ws.column_dimensions["C"].width = 20
        print("  ✓ Dashboard sheet created")
