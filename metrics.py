# metrics.py
import pandas as pd
from data_processor import DataProcessor

class MetricsCalculator:
    def __init__(self, data_store: dict, config):
        self.data = data_store
        self.config = config
        self.metrics = {}

    def calculate_all_metrics(self):
        print("\n" + "="*60)
        print(" 📊 CALCULATING BUSINESS METRICS")
        print("="*60)

        self.metrics = {
            'summary': self._calculate_summary_metrics(),
            'lead_source': self._calculate_lead_source_distribution(),
            'industry_type': self._calculate_industry_distribution(),
            'meetings': self._calculate_meeting_metrics(),
            'leads': self._calculate_lead_metrics(),
            'calls': self._calculate_call_metrics(),
            'email': self._calculate_email_metrics(),
            'lead_quality': self._calculate_lead_quality_metrics(),
            'quotes': self._calculate_quote_metrics(),
            'deals': self._calculate_deal_metrics(),
        }
        return self.metrics

    def _get_dataframe(self, module: str):
        return self.data.get(module, pd.DataFrame())

    def _filter_by_date(self, df: pd.DataFrame, date_col: str = 'Created_Time'):
        if df.empty or date_col not in df.columns:
            return df
        try:
            df = DataProcessor.remove_all_timezones(df)
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            mask = (df[date_col] >= self.config.MONTH_START) & (df[date_col] <= self.config.MONTH_END)
            return df[mask]
        except:
            return df

    def _calculate_summary_metrics(self):
        return {
            'total_contacts': len(self._get_dataframe('Contacts')),
            'total_accounts': len(self._get_dataframe('Accounts')),
            'total_deals': len(self._get_dataframe('Pipelines')),
            'total_calls': len(self._get_dataframe('Calls')),
            'total_meetings': len(self._get_dataframe('Events')),
            'date_range': f"{self.config.MONTH_START.strftime('%Y-%m-%d')} to {self.config.MONTH_END.strftime('%Y-%m-%d')}"
        }

    def _calculate_lead_source_distribution(self):
        df = self._get_dataframe('Contacts')
        if df.empty:
            return pd.DataFrame(columns=['Lead_Source', 'Count', 'Percentage'])
        lead_col = None
        for col in df.columns:
            if 'lead' in col.lower() and 'source' in col.lower():
                lead_col = col; break
        if not lead_col:
            return pd.DataFrame(columns=['Lead_Source', 'Count', 'Percentage'])
        dist = df[lead_col].value_counts().reset_index()
        dist.columns = ['Lead_Source', 'Count']
        dist['Percentage'] = (dist['Count'] / dist['Count'].sum() * 100).round(2)
        return dist

    def _calculate_industry_distribution(self):
        df = self._get_dataframe('Accounts')
        if df.empty:
            return pd.DataFrame(columns=['Industry', 'Count', 'Percentage'])
        industry_col = next((c for c in df.columns if 'industry' in c.lower()), None)
        if not industry_col:
            return pd.DataFrame(columns=['Industry', 'Count', 'Percentage'])
        dist = df[industry_col].value_counts().reset_index()
        dist.columns = ['Industry', 'Count']
        dist['Percentage'] = (dist['Count'] / dist['Count'].sum() * 100).round(2)
        return dist

    def _calculate_meeting_metrics(self):
        df = self._filter_by_date(self._get_dataframe('Events'))
        if df.empty:
            return {'total_meetings': 0, 'meetings_this_month': 0, 'avg_meetings_per_day': 0}
        total = len(df)
        days = (self.config.MONTH_END - self.config.MONTH_START).days + 1
        avg = total / days if days > 0 else 0
        return {'total_meetings': total, 'meetings_this_month': total, 'avg_meetings_per_day': round(avg, 2)}

    def _calculate_lead_metrics(self):
        df = self._filter_by_date(self._get_dataframe('Contacts'))
        return {'total_leads_generated': len(df), 'new_leads_this_month': len(df)}

    def _calculate_call_metrics(self):
        df = self._filter_by_date(self._get_dataframe('Calls'))
        if df.empty:
            return {'total_calls': 0, 'calls_this_month': 0, 'avg_calls_per_day': 0}
        total = len(df)
        days = (self.config.MONTH_END - self.config.MONTH_START).days + 1
        avg = total / days if days > 0 else 0
        return {'total_calls': total, 'calls_this_month': total, 'avg_calls_per_day': round(avg, 2)}

    def _calculate_email_metrics(self):
        tasks_df = self._filter_by_date(self._get_dataframe('Tasks'))
        email_tasks = 0
        if not tasks_df.empty:
            for col in tasks_df.columns:
                if 'subject' in col.lower() or 'type' in col.lower():
                    email_tasks = tasks_df[tasks_df[col].astype(str).str.lower().str.contains('email|mail', na=False, regex=True)].shape[0]
                    break
        return {'email_related_tasks': email_tasks, 'note': 'Email tracking requires Campaign module or Email integration'}

    def _calculate_lead_quality_metrics(self):
        df = self._filter_by_date(self._get_dataframe('Contacts'))
        if df.empty:
            return {'total_leads': 0, 'junk_leads': 0, 'prospect_leads': 0, 'qualified_leads': 0}
        status_col = next((c for c in df.columns if any(k in c.lower() for k in ['status','stage','rating'])), None)
        if not status_col:
            return {'total_leads': len(df), 'junk_leads': 0, 'prospect_leads': 0, 'qualified_leads': len(df), 'note': 'No status/stage column'}
        status_counts = df[status_col].value_counts().to_dict()
        junk = sum(c for s, c in status_counts.items() if any(k in str(s).lower() for k in ['junk','disqualified','lost','invalid','dead']))
        prospect = sum(c for s, c in status_counts.items() if any(k in str(s).lower() for k in ['prospect','future','nurture','cold','warm']))
        qualified = len(df) - junk - prospect
        return {'total_leads': len(df), 'junk_leads': junk, 'prospect_leads': prospect, 'qualified_leads': qualified, 'status_breakdown': status_counts}

    def _calculate_quote_metrics(self):
        df = self._filter_by_date(self._get_dataframe('Pipelines'))
        if df.empty:
            return {'total_quotes': 0, 'total_quote_value': 0, 'average_quote_value': 0}
        stage_col = next((c for c in df.columns if 'stage' in c.lower() or 'status' in c.lower()), None)
        quotes_df = df[df[stage_col].astype(str).str.lower().str.contains('quote|proposal|quotation', na=False, regex=True)] if stage_col else df
        amount_col = next((c for c in df.columns if 'amount' in c.lower() or 'value' in c.lower()), None)
        total_value = pd.to_numeric(quotes_df[amount_col], errors='coerce').fillna(0).sum() if amount_col else 0
        return {'total_quotes': len(quotes_df), 'total_quote_value': float(total_value), 'average_quote_value': float(total_value / len(quotes_df)) if len(quotes_df) > 0 else 0}

    def _calculate_deal_metrics(self):
        df = self._filter_by_date(self._get_dataframe('Pipelines'))
        if df.empty:
            return {'total_deals': 0, 'deals_won': 0, 'deals_lost': 0, 'total_won_value': 0, 'win_rate': 0}
        stage_col = next((c for c in df.columns if 'stage' in c.lower() or 'status' in c.lower()), None)
        won = df[df[stage_col].astype(str).str.lower().str.contains('won|closed won|success', na=False, regex=True)] if stage_col else pd.DataFrame()
        lost = df[df[stage_col].astype(str).str.lower().str.contains('lost|closed lost|dead', na=False, regex=True)] if stage_col else pd.DataFrame()
        amount_col = next((c for c in won.columns if 'amount' in c.lower() or 'value' in c.lower()), None)
        total_value = pd.to_numeric(won[amount_col], errors='coerce').fillna(0).sum() if amount_col else 0
        total_closed = len(won) + len(lost)
        win_rate = (len(won) / total_closed * 100) if total_closed > 0 else 0
        return {'total_deals': len(df), 'deals_won': len(won), 'deals_lost': len(lost), 'total_won_value': float(total_value), 'win_rate': round(win_rate, 2)}
