# db.py
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from datetime import datetime

class DB:
    """Simple DB wrapper for token CRUD using SQLAlchemy"""
    def __init__(self, odbc_connection_string: str):
        if not odbc_connection_string:
            raise ValueError("ODBC connection string is required. Set SQL_SERVER_ODBC env var.")
        quoted = quote_plus(odbc_connection_string)
        self.engine = create_engine(f"mssql+pyodbc:///?odbc_connect={quoted}", fast_executemany=True)

    def get_token_row(self, service: str):
        sql = text("SELECT service, access_token, refresh_token, expires_at FROM zoho_tokens WHERE service = :svc")
        with self.engine.connect() as conn:
            r = conn.execute(sql, {"svc": service}).fetchone()
            if not r:
                return None
            return {"service": r[0], "access_token": r[1], "refresh_token": r[2], "expires_at": r[3]}

    def upsert_token(self, service: str, access_token: str, refresh_token: str = None, expires_at=None):
        now = datetime.utcnow()
        with self.engine.begin() as conn:
            existing = conn.execute(text("SELECT 1 FROM zoho_tokens WHERE service = :svc"), {"svc": service}).scalar()
            if existing:
                conn.execute(
                    text("""UPDATE zoho_tokens
                            SET access_token = :access_token,
                                refresh_token = COALESCE(:refresh_token, refresh_token),
                                expires_at = :expires_at,
                                updated_at = SYSUTCDATETIME()
                            WHERE service = :svc"""),
                    {"access_token": access_token, "refresh_token": refresh_token, "expires_at": expires_at, "svc": service}
                )
            else:
                conn.execute(
                    text("""INSERT INTO zoho_tokens(service, access_token, refresh_token, expires_at)
                            VALUES(:svc, :access_token, :refresh_token, :expires_at)"""),
                    {"svc": service, "access_token": access_token, "refresh_token": refresh_token, "expires_at": expires_at}
                )
