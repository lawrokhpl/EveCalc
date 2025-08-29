from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    # For local auth fallback only; for Google OAuth store null
    password_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(128), nullable=False)
    value = Column(String(2048), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_user_pref"),)

    user = relationship("User")


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    resource = Column(String(128), unique=True, nullable=False, index=True)
    price = Column(Float, nullable=False, default=0.0)


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    resource = Column(String(128), index=True, nullable=False)
    price_buy = Column(Float, nullable=True)
    price_sell = Column(Float, nullable=True)
    price_avg = Column(Float, nullable=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)


class MiningUnit(Base):
    __tablename__ = "mining_units"

    id = Column(Integer, primary_key=True)
    # resource_id pattern from data frame (planetId_resourceName)
    resource_key = Column(String(128), unique=True, index=True, nullable=False)
    units = Column(Integer, nullable=False, default=0)


