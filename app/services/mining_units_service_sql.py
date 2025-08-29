from typing import Dict

from sqlalchemy import select

from app.db import session_scope, get_engine
from app.models.sql_models import Base, MiningUnit


class SQLMiningUnitsService:
    def __init__(self):
        engine = get_engine()
        Base.metadata.create_all(bind=engine)

    def load_units_map(self) -> Dict[str, int]:
        with session_scope() as s:
            rows = s.execute(select(MiningUnit)).scalars().all()
            return {r.resource_key: int(r.units) for r in rows}

    def save_units_map(self, mapping: Dict[str, int]) -> None:
        with session_scope() as s:
            for key, units in mapping.items():
                row = s.execute(select(MiningUnit).where(MiningUnit.resource_key == key)).scalar_one_or_none()
                if row:
                    row.units = int(units)
                else:
                    s.add(MiningUnit(resource_key=key, units=int(units)))


