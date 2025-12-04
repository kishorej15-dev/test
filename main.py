# main.py
import os
from config import Config
from db import DB
from token_manager import TokenManager
from client import ZohoBiginClient
from data_processor import DataProcessor
from metrics import MetricsCalculator
from exporter import MetricsExporter
from datetime import datetime

def main():
    print("Starting Zoho Bigin Analytics (modular)...")

    cfg = Config()

    if not cfg.SQL_ODBC:
        print("ERROR: SQL_ODBC not set in env. Example:")
        print('  export SQL_SERVER_ODBC="DRIVER={ODBC Driver 18 for SQL Server};SERVER=server;DATABASE=db;UID=user;PWD=pass;TrustServerCertificate=yes"')
        return

    db = DB(cfg.SQL_ODBC)

    token_row = db.get_token_row("zoho_bigin")
    if token_row is None:
        print("No token row found for service 'zoho_bigin' in zoho_tokens table.")
        print("Please insert a row with your refresh_token. Example SQL was provided in docs.")
        return

    tm = TokenManager(cfg, db, service_name="zoho_bigin")
    client = ZohoBiginClient(tm, cfg.BASE_URL, cfg)

    data_store = {}
    success_count = 0
    for module in cfg.MODULES_TO_FETCH:
        try:
            records = client.fetch_module_data(module)
            if records:
                flattened = [DataProcessor.flatten_dict(r) for r in records]
                import pandas as pd
                df = pd.DataFrame(flattened)
                df = DataProcessor.clean_column_names(df)
                df = DataProcessor.remove_all_timezones(df)
                data_store[module] = df
                success_count += 1
        except Exception as e:
            print(f"Error fetching {module}: {e}")

    print(f"Fetched {success_count}/{len(cfg.MODULES_TO_FETCH)} modules")

    if success_count == 0:
        print("No data fetched; exiting.")
        return

    calc = MetricsCalculator(data_store, cfg)
    metrics = calc.calculate_all_metrics()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"Zoho_Analytics_{ts}.xlsx"
    ok = MetricsExporter.create_excel(data_store, metrics, fname)
    if ok:
        print(f"Report created: {fname}")
    else:
        print("Failed to create report.")

if __name__ == "__main__":
    main()
