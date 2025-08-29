import json
from typing import Dict

from sqlalchemy import select

from app.db import session_scope, get_engine
from app.models.sql_models import Base, User, UserPreference
from app.config import settings
import bcrypt


class SQLUserService:
    def __init__(self):
        # Ensure tables exist
        engine = get_engine()
        Base.metadata.create_all(bind=engine)

    def register_user(self, username: str, password: str):
        if not username or not password:
            return False, "Username and password cannot be empty."

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        with session_scope() as s:
            exists = s.execute(select(User).where(User.email == username)).scalar_one_or_none()
            if exists:
                return False, "Username already exists."
            s.add(User(email=username, password_hash=password_hash))
        return True, "User registered successfully."

    def verify_user(self, username: str, password: str) -> bool:
        with session_scope() as s:
            user = s.execute(select(User).where(User.email == username)).scalar_one_or_none()
            if not user:
                return False
            if not user.password_hash:
                return False
            try:
                return bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8"))
            except Exception:
                return False

    def load_user_preferences(self, username: str) -> Dict:
        with session_scope() as s:
            user = s.execute(select(User).where(User.email == username)).scalar_one_or_none()
            if not user:
                return {}
            prefs = s.execute(select(UserPreference).where(UserPreference.user_id == user.id)).scalars().all()
            result: Dict[str, str] = {p.key: p.value for p in prefs}
            # Convert JSON-like strings back to native types where possible
            converted: Dict[str, object] = {}
            for k, v in result.items():
                try:
                    converted[k] = json.loads(v)
                except Exception:
                    converted[k] = v
            return converted

    def save_user_preferences(self, username: str, preferences: Dict) -> None:
        with session_scope() as s:
            user = s.execute(select(User).where(User.email == username)).scalar_one_or_none()
            if not user:
                return
            # Upsert key/value as strings (JSON dump)
            for k, v in preferences.items():
                value_str = json.dumps(v)
                pref = s.execute(
                    select(UserPreference).where(UserPreference.user_id == user.id, UserPreference.key == k)
                ).scalar_one_or_none()
                if pref:
                    pref.value = value_str
                else:
                    s.add(UserPreference(user_id=user.id, key=k, value=value_str))

    def get_user_id(self, username: str) -> int:
        with session_scope() as s:
            user = s.execute(select(User).where(User.email == username)).scalar_one_or_none()
            return user.id if user else 0


