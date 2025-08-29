from typing import Dict, Optional, List
from datetime import datetime
import re

from sqlalchemy import select

from app.db import session_scope, get_engine
from app.models.sql_models import Base, Price, PriceHistory
import pandas as pd


class SQLPriceService:
    def __init__(self):
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        self._cache: Dict[str, float] = {}
        self.load_prices()

    @staticmethod
    def _normalize_resource(name: str) -> str:
        if name is None:
            return ""
        # Trim and collapse multiple spaces, keep original casing
        return " ".join(str(name).strip().split())

    def load_prices(self) -> None:
        with session_scope() as s:
            rows = s.execute(select(Price)).scalars().all()
            self._cache = {r.resource: float(r.price) for r in rows}

    def save_prices(self) -> None:
        with session_scope() as s:
            for resource, price in self._cache.items():
                norm = self._normalize_resource(resource)
                row = s.execute(select(Price).where(Price.resource == norm)).scalar_one_or_none()
                if row:
                    row.price = float(price)
                else:
                    s.add(Price(resource=norm, price=float(price)))

    def get_price(self, resource_name: str) -> float:
        return self._cache.get(self._normalize_resource(resource_name), 0.0)

    def get_all_prices(self) -> Dict[str, float]:
        return dict(self._cache)

    def update_price(self, resource_name: str, price: float) -> None:
        self._cache[self._normalize_resource(resource_name)] = float(price)

    def update_multiple_prices(self, price_dict: Dict[str, float]) -> None:
        for k, v in price_dict.items():
            norm = self._normalize_resource(k)
            if not norm:
                continue
            self._cache[norm] = float(v)

    # --- History ---
    def import_prices_dataframe(self, df, user_id: Optional[int] = None, price_date: Optional[datetime] = None) -> None:
        """Import CSV dataframe (columns: resource,buy,sell,average[,date]). Saves to PriceHistory and updates cache optionally.
        """
        if df is None or df.empty:
            return
        with session_scope() as s:
            for _, row in df.iterrows():
                resource = self._normalize_resource(row.get('resource'))
                if not resource:
                    continue
                buy = row.get('buy') if 'buy' in df.columns else None
                sell = row.get('sell') if 'sell' in df.columns else None
                avg = row.get('average') if 'average' in df.columns else None
                d = row.get('date') if 'date' in df.columns else price_date
                try:
                    d = pd.to_datetime(d) if d is not None else datetime.utcnow()
                except Exception:
                    d = datetime.utcnow()
                s.add(PriceHistory(user_id=user_id, resource=resource, price_buy=buy, price_sell=sell, price_avg=avg, date=d))

    def get_distinct_history_dates(self, user_id: Optional[int] = None) -> List[datetime]:
        with session_scope() as s:
            q = select(PriceHistory.date).distinct().order_by(PriceHistory.date)
            if user_id:
                q = q.where(PriceHistory.user_id == user_id)
            return [r[0] for r in s.execute(q).all()]

    def load_prices_from_history_date(self, when: datetime, user_id: Optional[int] = None) -> Dict[str, float]:
        with session_scope() as s:
            q = select(PriceHistory).where(PriceHistory.date == when)
            if user_id:
                q = q.where(PriceHistory.user_id == user_id)
            rows = s.execute(q).scalars().all()
            return {self._normalize_resource(r.resource): float(r.price_avg or r.price_buy or 0.0) for r in rows}

    # For compatibility with file-based service API
    def get_price_history(self, username: str):
        """Return pandas DataFrame of price history for given username (or all if not found)."""
        try:
            from app.services.user_service_sql import SQLUserService
            uid = SQLUserService().get_user_id(username)
        except Exception:
            uid = None
        with session_scope() as s:
            q = select(PriceHistory)
            if uid:
                q = q.where(PriceHistory.user_id == uid)
            rows = s.execute(q).scalars().all()
            if not rows:
                return pd.DataFrame()
            data = [
                {
                    'resource': r.resource,
                    'buy': r.price_buy,
                    'sell': r.price_sell,
                    'average': r.price_avg,
                    'date': pd.to_datetime(r.date)
                }
                for r in rows
            ]
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            return df.sort_values(by='date')


