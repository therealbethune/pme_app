from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()


class Fund(Base):
    __tablename__ = "funds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    fund_type: Mapped[str] = mapped_column(String(100), nullable=True)  # PE, VC, etc.
    vintage_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_size: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    cash_flows: Mapped[list["CashFlow"]] = relationship(
        "CashFlow", back_populates="fund", cascade="all, delete-orphan"
    )
    nav_entries: Mapped[list["NAV"]] = relationship(
        "NAV", back_populates="fund", cascade="all, delete-orphan"
    )
    portfolio_funds: Mapped[list["PortfolioFund"]] = relationship(
        "PortfolioFund", back_populates="fund"
    )

    __table_args__ = (Index("idx_fund_name_vintage", "name", "vintage_year"),)


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    benchmark_symbol: Mapped[str] = mapped_column(
        String(20), default="^GSPC"
    )  # S&P 500
    risk_free_rate: Mapped[float] = mapped_column(Float, default=0.025)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    portfolio_funds: Mapped[list["PortfolioFund"]] = relationship(
        "PortfolioFund", back_populates="portfolio", cascade="all, delete-orphan"
    )


class PortfolioFund(Base):
    __tablename__ = "portfolio_funds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    portfolio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("portfolios.id"), nullable=False
    )
    fund_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("funds.id"), nullable=False
    )
    weight: Mapped[float] = mapped_column(Float, default=1.0)  # Portfolio weight
    date_added: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio", back_populates="portfolio_funds"
    )
    fund: Mapped["Fund"] = relationship("Fund", back_populates="portfolio_funds")

    __table_args__ = (Index("idx_portfolio_fund", "portfolio_id", "fund_id"),)


class CashFlow(Base):
    __tablename__ = "cash_flows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fund_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("funds.id"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # Positive = contribution, Negative = distribution
    cash_flow_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # contribution, distribution, management_fee
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    fund: Mapped["Fund"] = relationship("Fund", back_populates="cash_flows")

    __table_args__ = (
        Index("idx_cashflow_fund_date", "fund_id", "date"),
        Index("idx_cashflow_date_type", "date", "cash_flow_type"),
    )


class NAV(Base):
    __tablename__ = "nav_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fund_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("funds.id"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    nav_value: Mapped[float] = mapped_column(Float, nullable=False)
    called_capital: Mapped[float | None] = mapped_column(Float, nullable=True)
    distributed_capital: Mapped[float | None] = mapped_column(Float, nullable=True)
    remaining_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    fund: Mapped["Fund"] = relationship("Fund", back_populates="nav_entries")

    __table_args__ = (Index("idx_nav_fund_date", "fund_id", "date"),)


class BenchmarkPrice(Base):
    __tablename__ = "benchmark_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    adjusted_close: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_benchmark_symbol_date", "symbol", "date"),)


class UploadHistory(Base):
    __tablename__ = "upload_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # fund, index, nav
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    rows_processed: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(
        String(20), default="success"
    )  # success, error, partial
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    fund_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("funds.id"), nullable=True
    )

    __table_args__ = (Index("idx_upload_date_type", "upload_date", "file_type"),)
