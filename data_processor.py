# data_processor.py
import pandas as pd
import json

class DataProcessor:
    @staticmethod
    def flatten_dict(d: dict, parent_key: str = "", sep: str = "_") -> dict:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(DataProcessor.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                if v and isinstance(v[0], dict):
                    items.append((new_key, json.dumps(v, ensure_ascii=False)))
                else:
                    items.append((new_key, ", ".join(str(x) for x in v) if v else ""))
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        df.columns = (df.columns
                      .str.replace('$', '', regex=False)
                      .str.replace('.', '_', regex=False)
                      .str.replace(' ', '_', regex=False)
                      .str.replace('(', '', regex=False)
                      .str.replace(')', '', regex=False))
        return df

    @staticmethod
    def remove_all_timezones(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        for col in df.columns:
            if df[col].dtype == 'object':
                sample = df[col].dropna().head(1)
                if not sample.empty:
                    sample_val = str(sample.iloc[0])
                    if any(x in sample_val for x in ['T', 'Z', '+', '-']) and ':' in sample_val:
                        try:
                            df[col] = pd.to_datetime(df[col], errors='coerce', utc=True).dt.tz_localize(None)
                        except:
                            pass
            elif 'datetime' in str(df[col].dtype):
                try:
                    if hasattr(df[col].dtype, 'tz') and df[col].dtype.tz is not None:
                        df[col] = df[col].dt.tz_localize(None)
                except:
                    pass
        return df
