import io
import logging
from datetime import datetime

from database import get_db  # Assume this exists
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from models import Fund, Portfolio, PortfolioFund
from portfolio_service import PortfolioService
from reporting import ReportingService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

# Pydantic models for request/response
from pydantic import BaseModel


class PortfolioCreate(BaseModel):
    name: str
    description: str | None = None
    benchmark_symbol: str = "^GSPC"
    risk_free_rate: float = 0.025
    fund_ids: list[int]


class PortfolioUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    benchmark_symbol: str | None = None
    risk_free_rate: float | None = None


class PortfolioResponse(BaseModel):
    id: int
    name: str
    description: str | None
    benchmark_symbol: str
    risk_free_rate: float
    created_at: datetime
    updated_at: datetime
    num_funds: int

    class Config:
        from_attributes = True


class WeightUpdate(BaseModel):
    fund_id: int
    weight: float


@router.post("/", response_model=PortfolioResponse)
async def create_portfolio(
    portfolio_data: PortfolioCreate, db: Session = Depends(get_db)
) -> PortfolioResponse:
    """Create a new portfolio with selected funds."""
    try:
        portfolio_service = PortfolioService(db)

        # Validate that all fund IDs exist
        for fund_id in portfolio_data.fund_ids:
            fund = db.query(Fund).filter(Fund.id == fund_id).first()
            if not fund:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Fund {fund_id} not found",
                )

        # Create portfolio
        portfolio = await portfolio_service.build_portfolio(
            fund_ids=portfolio_data.fund_ids, portfolio_name=portfolio_data.name
        )

        # Update additional fields
        portfolio.description = portfolio_data.description
        portfolio.benchmark_symbol = portfolio_data.benchmark_symbol
        portfolio.risk_free_rate = portfolio_data.risk_free_rate
        db.commit()

        # Get fund count for response
        num_funds = len(portfolio_data.fund_ids)

        return PortfolioResponse(
            id=portfolio.id,
            name=portfolio.name,
            description=portfolio.description,
            benchmark_symbol=portfolio.benchmark_symbol,
            risk_free_rate=portfolio.risk_free_rate,
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at,
            num_funds=num_funds,
        )

    except Exception as e:
        logger.error(f"Error creating portfolio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/", response_model=list[PortfolioResponse])
async def get_portfolios(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[PortfolioResponse]:
    """Get all portfolios with pagination."""
    try:
        portfolios = (
            db.query(Portfolio)
            .filter(Portfolio.is_active)
            .offset(skip)
            .limit(limit)
            .all()
        )

        result = []
        for portfolio in portfolios:
            num_funds = (
                db.query(PortfolioFund)
                .filter(PortfolioFund.portfolio_id == portfolio.id)
                .count()
            )

            result.append(
                PortfolioResponse(
                    id=portfolio.id,
                    name=portfolio.name,
                    description=portfolio.description,
                    benchmark_symbol=portfolio.benchmark_symbol,
                    risk_free_rate=portfolio.risk_free_rate,
                    created_at=portfolio.created_at,
                    updated_at=portfolio.updated_at,
                    num_funds=num_funds,
                )
            )

        return result

    except Exception as e:
        logger.error(f"Error getting portfolios: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: int, db: Session = Depends(get_db)
) -> PortfolioResponse:
    """Get a specific portfolio."""
    try:
        portfolio = (
            db.query(Portfolio)
            .filter(Portfolio.id == portfolio_id, Portfolio.is_active)
            .first()
        )

        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
            )

        num_funds = (
            db.query(PortfolioFund)
            .filter(PortfolioFund.portfolio_id == portfolio_id)
            .count()
        )

        return PortfolioResponse(
            id=portfolio.id,
            name=portfolio.name,
            description=portfolio.description,
            benchmark_symbol=portfolio.benchmark_symbol,
            risk_free_rate=portfolio.risk_free_rate,
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at,
            num_funds=num_funds,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting portfolio {portfolio_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: int, portfolio_data: PortfolioUpdate, db: Session = Depends(get_db)
) -> PortfolioResponse:
    """Update portfolio details."""
    try:
        portfolio = (
            db.query(Portfolio)
            .filter(Portfolio.id == portfolio_id, Portfolio.is_active)
            .first()
        )

        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
            )

        # Update fields
        update_data = portfolio_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(portfolio, field, value)

        portfolio.updated_at = datetime.utcnow()
        db.commit()

        num_funds = (
            db.query(PortfolioFund)
            .filter(PortfolioFund.portfolio_id == portfolio_id)
            .count()
        )

        return PortfolioResponse(
            id=portfolio.id,
            name=portfolio.name,
            description=portfolio.description,
            benchmark_symbol=portfolio.benchmark_symbol,
            risk_free_rate=portfolio.risk_free_rate,
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at,
            num_funds=num_funds,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating portfolio {portfolio_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: int, db: Session = Depends(get_db)
) -> dict[str, str]:
    """Soft delete a portfolio."""
    try:
        portfolio = (
            db.query(Portfolio)
            .filter(Portfolio.id == portfolio_id, Portfolio.is_active)
            .first()
        )

        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
            )

        portfolio.is_active = False
        portfolio.updated_at = datetime.utcnow()
        db.commit()

        return {"message": "Portfolio deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting portfolio {portfolio_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{portfolio_id}/analytics")
async def get_portfolio_analytics(
    portfolio_id: int, db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Get comprehensive portfolio analytics."""
    try:
        # Run heavy computation in thread pool
        analytics = await run_in_threadpool(
            _calculate_portfolio_analytics_sync, portfolio_id, db
        )

        return analytics

    except Exception as e:
        logger.error(f"Error getting portfolio analytics {portfolio_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


def _calculate_portfolio_analytics_sync(
    portfolio_id: int, db: Session
) -> dict[str, Any]:
    """Synchronous portfolio analytics calculation for thread pool execution."""
    portfolio_service = PortfolioService(db)
    return portfolio_service.calc_portfolio_kpis(portfolio_id)


@router.put("/{portfolio_id}/weights")
async def update_portfolio_weights(
    portfolio_id: int, weights: list[WeightUpdate], db: Session = Depends(get_db)
) -> dict[str, str]:
    """Update portfolio fund weights."""
    try:
        # Validate portfolio exists
        portfolio = (
            db.query(Portfolio)
            .filter(Portfolio.id == portfolio_id, Portfolio.is_active)
            .first()
        )

        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
            )

        # Validate weights sum to 1
        total_weight = sum(w.weight for w in weights)
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Weights must sum to 1.0, got {total_weight}",
            )

        # Update weights
        for weight_update in weights:
            portfolio_fund = (
                db.query(PortfolioFund)
                .filter(
                    PortfolioFund.portfolio_id == portfolio_id,
                    PortfolioFund.fund_id == weight_update.fund_id,
                )
                .first()
            )

            if not portfolio_fund:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Fund {weight_update.fund_id} not in portfolio",
                )

            portfolio_fund.weight = weight_update.weight

        portfolio.updated_at = datetime.utcnow()
        db.commit()

        return {"message": "Portfolio weights updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating portfolio weights {portfolio_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/{portfolio_id}/funds/{fund_id}")
async def add_fund_to_portfolio(
    portfolio_id: int, fund_id: int, weight: float = 0.0, db: Session = Depends(get_db)
) -> dict[str, str]:
    """Add a fund to portfolio."""
    try:
        # Validate portfolio and fund exist
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        fund = db.query(Fund).filter(Fund.id == fund_id).first()
        if not fund:
            raise HTTPException(status_code=404, detail="Fund not found")

        # Check if fund already in portfolio
        existing = (
            db.query(PortfolioFund)
            .filter(
                PortfolioFund.portfolio_id == portfolio_id,
                PortfolioFund.fund_id == fund_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(status_code=400, detail="Fund already in portfolio")

        # Add fund to portfolio
        portfolio_fund = PortfolioFund(
            portfolio_id=portfolio_id, fund_id=fund_id, weight=weight
        )
        db.add(portfolio_fund)
        db.commit()

        return {"message": "Fund added to portfolio successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding fund to portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{portfolio_id}/funds/{fund_id}")
async def remove_fund_from_portfolio(
    portfolio_id: int, fund_id: int, db: Session = Depends(get_db)
) -> dict[str, str]:
    """Remove a fund from portfolio."""
    try:
        portfolio_fund = (
            db.query(PortfolioFund)
            .filter(
                PortfolioFund.portfolio_id == portfolio_id,
                PortfolioFund.fund_id == fund_id,
            )
            .first()
        )

        if not portfolio_fund:
            raise HTTPException(status_code=404, detail="Fund not in portfolio")

        db.delete(portfolio_fund)
        db.commit()

        return {"message": "Fund removed from portfolio successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing fund from portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{portfolio_id}/report/pdf")
async def download_pdf_report(
    portfolio_id: int, db: Session = Depends(get_db)
) -> bytes:
    """Download PDF report for portfolio."""
    try:
        # Run heavy computation in thread pool
        pdf_bytes = await run_in_threadpool(_generate_pdf_report_sync, portfolio_id, db)

        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        filename = f"{portfolio.name.replace(' ', '_')}_report.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_pdf_report_sync(portfolio_id: int, db: Session) -> bytes:
    """Synchronous PDF report generation for thread pool execution."""
    reporting_service = ReportingService(db)
    return reporting_service.generate_pdf(portfolio_id)


@router.get("/{portfolio_id}/report/excel")
async def download_excel_report(
    portfolio_id: int, db: Session = Depends(get_db)
) -> bytes:
    """Download Excel report for portfolio."""
    try:
        # Run heavy computation in thread pool
        excel_bytes = await run_in_threadpool(
            _generate_excel_report_sync, portfolio_id, db
        )

        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        filename = f"{portfolio.name.replace(' ', '_')}_report.xlsx"

        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error(f"Error generating Excel report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_excel_report_sync(portfolio_id: int, db: Session) -> bytes:
    """Synchronous Excel report generation for thread pool execution."""
    reporting_service = ReportingService(db)
    return reporting_service.generate_excel(portfolio_id)
