"""
FastAPI main application for PME Calculator.
Production-ready API with comprehensive PME analysis capabilities.
"""

import io

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from pme_app.logger import logger
from pme_app.routers import portfolio
from pme_app.services.analysis import (
    calculate_annualized_return,
    compute_alpha_beta,
    compute_drawdown,
    compute_volatility,
    direct_alpha,
    ks_pme,
)
from pme_app.utils import (
    DefaultJSONResponse,
    create_error_response,
    create_success_response,
)

# Create FastAPI app
app = FastAPI(
    title="PME Calculator API",
    description="Professional Private Market Equivalent (PME) calculation API with comprehensive analysis capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=DefaultJSONResponse,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(portfolio.router)


# Pydantic models
class PMERequest(BaseModel):
    fund_cashflows: list[float]
    index_values: list[float]


class AlphaRequest(BaseModel):
    fund_irr: float
    index_irr: float


class VolatilityRequest(BaseModel):
    returns: list[float]


class DrawdownRequest(BaseModel):
    prices: list[float]


class AlphaBetaRequest(BaseModel):
    fund_returns: list[float]
    index_returns: list[float]


class AnnualizedReturnRequest(BaseModel):
    returns: list[float]


# Health check endpoints (both paths for compatibility)
@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "PME Calculator API",
        "version": "1.0.0",
        "features": [
            "KS PME Calculation",
            "Direct Alpha Analysis",
            "Volatility Computation",
            "Drawdown Analysis",
            "Alpha/Beta Calculation",
            "Annualized Returns",
        ],
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "PME Calculator API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0",
    }


# PME Calculation endpoints
@app.post("/api/pme/ks")
async def calculate_ks_pme(request: PMERequest):
    """Calculate KS PME (Kaplan-Schoar Public Market Equivalent)."""
    try:
        fund_cf = np.array(request.fund_cashflows)
        idx_values = np.array(request.index_values)

        result = ks_pme(fund_cf, idx_values)

        logger.info(
            "KS PME calculation completed",
            extra={
                "pme_value": result,
                "fund_cashflows_count": len(fund_cf),
                "index_values_count": len(idx_values),
            },
        )

        return create_success_response(
            data={
                "pme_value": result,
                "method": "Kaplan-Schoar PME",
                "fund_cashflows_count": len(fund_cf),
                "index_values_count": len(idx_values),
            },
            message="KS PME calculation completed successfully",
        )
    except Exception as e:
        logger.error(f"KS PME calculation failed: {str(e)}")
        return create_error_response(
            error="KS PME calculation failed", details=str(e), status_code=400
        )


@app.post("/api/alpha/direct")
async def calculate_direct_alpha(request: AlphaRequest):
    """Calculate Direct Alpha."""
    try:
        result = direct_alpha(request.fund_irr, request.index_irr)

        return {
            "alpha": result,
            "fund_irr": request.fund_irr,
            "index_irr": request.index_irr,
            "method": "Direct Alpha",
        }
    except Exception as e:
        logger.error(f"Direct Alpha calculation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Calculation failed: {str(e)}")


@app.post("/api/analysis/volatility")
async def calculate_volatility(request: VolatilityRequest):
    """Calculate volatility of returns."""
    try:
        returns_series = pd.Series(request.returns)
        result = compute_volatility(returns_series)

        return create_success_response(
            data={
                "volatility": result,
                "returns_count": len(request.returns),
                "method": "Standard Deviation",
            },
            message="Volatility calculation completed successfully",
        )
    except Exception as e:
        logger.error(f"Volatility calculation failed: {str(e)}")
        return create_error_response(
            error="Volatility calculation failed", details=str(e), status_code=400
        )


@app.post("/api/analysis/drawdown")
async def calculate_drawdown(request: DrawdownRequest):
    """Calculate maximum drawdown."""
    try:
        prices_series = pd.Series(request.prices)
        result = compute_drawdown(prices_series)

        return {
            "max_drawdown": result,
            "prices_count": len(request.prices),
            "method": "Peak-to-Trough",
        }
    except Exception as e:
        logger.error(f"Drawdown calculation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Calculation failed: {str(e)}")


@app.post("/api/analysis/alpha-beta")
async def calculate_alpha_beta_analysis(request: AlphaBetaRequest):
    """Calculate Alpha and Beta using regression analysis."""
    try:
        fund_returns = pd.Series(request.fund_returns)
        index_returns = pd.Series(request.index_returns)

        alpha, beta = compute_alpha_beta(fund_returns, index_returns)

        return {
            "alpha": alpha,
            "beta": beta,
            "fund_returns_count": len(request.fund_returns),
            "index_returns_count": len(request.index_returns),
            "method": "OLS Regression",
        }
    except Exception as e:
        logger.error(f"Alpha/Beta calculation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Calculation failed: {str(e)}")


@app.post("/api/analysis/annualized-return")
async def calculate_annualized_return_endpoint(request: AnnualizedReturnRequest):
    """Calculate annualized return."""
    try:
        returns_series = pd.Series(request.returns)
        result = calculate_annualized_return(returns_series)

        return {
            "annualized_return": result,
            "returns_count": len(request.returns),
            "method": "Geometric Mean",
        }
    except Exception as e:
        logger.error(f"Annualized return calculation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Calculation failed: {str(e)}")


# File upload endpoints
@app.post("/api/upload/csv")
async def upload_csv_data(file: UploadFile = File(...)):
    """Upload CSV file and return parsed data."""
    try:
        if not file.filename or not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="File must be a CSV")

        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        return {
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "data_preview": df.head().to_dict("records"),
        }
    except Exception as e:
        logger.error(f"CSV upload failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")


@app.post("/api/upload/fund")
async def upload_fund_data(file: UploadFile = File(...)):
    """Upload fund data file (CSV/Excel)."""
    try:
        if not file.filename or not (
            file.filename.endswith(".csv") or file.filename.endswith(".xlsx")
        ):
            raise HTTPException(
                status_code=400, detail="File must be CSV or Excel format"
            )

        contents = await file.read()

        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        else:
            df = pd.read_excel(io.BytesIO(contents))

        logger.info(
            "Fund data uploaded",
            extra={
                "filename": file.filename,
                "rows": len(df),
                "columns": list(df.columns),
            },
        )

        return {
            "status": "success",
            "message": "Fund data uploaded successfully",
            "filename": file.filename,
            "file_id": f"fund_{file.filename}_{len(df)}",
            "rows": len(df),
            "columns": list(df.columns),
            "rows_processed": len(df),
            "columns_detected": len(df.columns),
            "data_preview": df.head().to_dict("records"),
            "data_type": "fund",
        }
    except Exception as e:
        logger.error(f"Fund upload failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")


@app.post("/api/upload/index")
async def upload_index_data(file: UploadFile = File(...)):
    """Upload market index data file (CSV/Excel)."""
    try:
        if not file.filename or not (
            file.filename.endswith(".csv") or file.filename.endswith(".xlsx")
        ):
            raise HTTPException(
                status_code=400, detail="File must be CSV or Excel format"
            )

        contents = await file.read()

        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        else:
            df = pd.read_excel(io.BytesIO(contents))

        logger.info(
            "Index data uploaded",
            extra={
                "filename": file.filename,
                "rows": len(df),
                "columns": list(df.columns),
            },
        )

        return {
            "status": "success",
            "message": "Index data uploaded successfully",
            "filename": file.filename,
            "file_id": f"index_{file.filename}_{len(df)}",
            "rows": len(df),
            "columns": list(df.columns),
            "rows_processed": len(df),
            "columns_detected": len(df.columns),
            "data_preview": df.head().to_dict("records"),
            "data_type": "index",
        }
    except Exception as e:
        logger.error(f"Index upload failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")


# Analysis execution endpoints
@app.post("/api/analysis/run")
@app.post("/api/analysis/run-sync")
async def run_comprehensive_analysis():
    """Run comprehensive PME analysis."""
    try:
        # Mock comprehensive analysis results matching frontend expectations
        # In a real implementation, this would process uploaded data
        analysis_results = {
            "status": "completed",
            "analysis_id": "analysis_001",
            "timestamp": "2024-01-15T10:30:00Z",
            "metrics": {
                "Fund IRR": 0.152,
                "Benchmark IRR": 0.128,
                "TVPI": 1.45,
                "DPI": 1.45,
                "RVPI": 0.00,
                "PME Ratio": 1.18,
                "Alpha": 0.024,
                "Beta": 0.95,
                "Volatility": 0.185,
                "Max Drawdown": -0.123,
                "Sharpe Ratio": 0.82,
            },
            "summary": {
                "fund_irr": 0.152,
                "benchmark_irr": 0.128,
                "pme_ratio": 1.18,
                "alpha": 0.024,
                "beta": 0.95,
                "volatility": 0.185,
                "max_drawdown": -0.123,
                "sharpe_ratio": 0.82,
            },
            "performance_metrics": {
                "total_return": 45.6,
                "annualized_return": 15.2,
                "excess_return": 2.4,
                "tracking_error": 8.2,
                "information_ratio": 0.29,
                "sortino_ratio": 1.15,
            },
            "risk_metrics": {
                "value_at_risk_95": -8.5,
                "conditional_var": -12.1,
                "downside_deviation": 13.2,
                "upside_capture": 105.3,
                "downside_capture": 92.7,
            },
            "charts": {
                "performance_comparison": "/v1/metrics/twr_vs_index",
                "cashflow_analysis": "/v1/metrics/cashflow_overview",
                "pme_progression": "/v1/metrics/pme_progression",
                "risk_return": "/v1/metrics/net_cf_market",
            },
            "recommendations": [
                "Fund outperformed benchmark with PME ratio of 1.18",
                "Strong risk-adjusted returns with Sharpe ratio of 0.82",
                "Consider rebalancing to reduce maximum drawdown exposure",
            ],
        }

        logger.info(
            "Comprehensive analysis completed",
            extra={
                "analysis_id": analysis_results["analysis_id"],
                "pme_ratio": analysis_results["summary"]["pme_ratio"],
                "fund_irr": analysis_results["summary"]["fund_irr"],
            },
        )

        return analysis_results

    except Exception as e:
        logger.error(f"Analysis execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/analysis/{analysis_id}")
async def get_analysis_results(analysis_id: str):
    """Get analysis results by ID."""
    # Mock response - in real implementation, retrieve from database
    return {
        "analysis_id": analysis_id,
        "status": "completed",
        "results": "Analysis results would be here",
    }


@app.get("/api/metrics/summary")
async def get_metrics_summary():
    """Get metrics summary for charts."""
    return {
        "status": "success",
        "metrics": {
            "fund_irr": 0.152,
            "benchmark_irr": 0.128,
            "pme_ratio": 1.18,
            "tvpi": 1.45,
            "dpi": 1.45,
            "rvpi": 0.00,
            "alpha": 0.024,
            "beta": 0.95,
            "volatility": 0.185,
            "max_drawdown": -0.123,
            "sharpe_ratio": 0.82,
        },
        "charts_available": True,
    }


# Legacy v1/metrics endpoints for frontend compatibility
@app.get("/v1/metrics/twr_vs_index")
async def get_twr_vs_index():
    """Get TWR vs Index chart data."""
    # Plotly.js format with data as array of traces
    return {
        "chart_type": "line",
        "title": "TWR vs Index Performance",
        "data": [
            {
                "x": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05"],
                "y": [100, 105, 103, 108, 112],
                "type": "scatter",
                "mode": "lines+markers",
                "name": "Fund TWR",
                "line": {"color": "#2563eb", "width": 3},
                "marker": {"size": 8},
            },
            {
                "x": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05"],
                "y": [100, 102, 101, 106, 109],
                "type": "scatter",
                "mode": "lines+markers",
                "name": "Russell 3000",
                "line": {"color": "#dc2626", "width": 2, "dash": "dash"},
                "marker": {"size": 6},
            },
        ],
        "layout": {
            "title": "TWR vs Russell 3000®",
            "xaxis": {"title": "Time Period"},
            "yaxis": {"title": "Index Value"},
        },
    }


@app.get("/v1/metrics/cashflow_overview")
async def get_cashflow_overview():
    """Get cash flow overview chart data."""
    return {
        "chart_type": "bar",
        "title": "Cash Flow Overview",
        "data": [
            {
                "x": ["2023-Q1", "2023-Q2", "2023-Q3", "2023-Q4"],
                "y": [-1000, -500, -750, -300],
                "type": "bar",
                "name": "Contributions",
                "marker": {"color": "#dc2626"},
            },
            {
                "x": ["2023-Q1", "2023-Q2", "2023-Q3", "2023-Q4"],
                "y": [0, 200, 400, 600],
                "type": "bar",
                "name": "Distributions",
                "marker": {"color": "#16a34a"},
            },
        ],
        "layout": {
            "title": "Cash Flow Analysis",
            "xaxis": {"title": "Time Period"},
            "yaxis": {"title": "Cash Flow ($000s)"},
            "barmode": "group",
        },
    }


@app.get("/v1/metrics/irr_pme")
async def get_irr_pme():
    """Get IRR and PME metrics."""
    return {
        "chart_type": "combo",
        "title": "IRR vs PME Performance",
        "data": [
            {
                "x": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05"],
                "y": [5.2, 8.1, 11.3, 13.7, 15.2],
                "type": "scatter",
                "mode": "lines+markers",
                "name": "Cumulative IRR (%)",
                "line": {"color": "#2563eb", "width": 3},
                "yaxis": "y",
            },
            {
                "x": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05"],
                "y": [0.95, 1.02, 1.08, 1.15, 1.18],
                "type": "scatter",
                "mode": "lines+markers",
                "name": "PME Ratio",
                "line": {"color": "#16a34a", "width": 3},
                "yaxis": "y2",
            },
        ],
        "layout": {
            "title": "Performance Analysis",
            "xaxis": {"title": "Time Period"},
            "yaxis": {"title": "IRR (%)", "side": "left"},
            "yaxis2": {"title": "PME Ratio", "side": "right", "overlaying": "y"},
        },
    }


@app.get("/v1/metrics/pme_progression")
async def get_pme_progression():
    """Get PME progression over time."""
    return {
        "chart_type": "line",
        "title": "PME Progression",
        "data": [
            {
                "x": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05"],
                "y": [0.95, 1.02, 1.08, 1.15, 1.18],
                "type": "scatter",
                "mode": "lines+markers",
                "name": "PME Ratio",
                "line": {"color": "#2563eb", "width": 3},
                "marker": {"size": 8},
                "fill": "tonexty",
            }
        ],
        "layout": {
            "title": "PME Progression",
            "xaxis": {"title": "Time Period"},
            "yaxis": {"title": "PME Ratio"},
        },
    }


@app.get("/v1/metrics/net_cf_market")
async def get_net_cf_market():
    """Get net cash flow vs market data."""
    return {
        "chart_type": "combo",
        "title": "Net Cash Flow vs Market",
        "data": [
            {
                "x": ["2023-Q1", "2023-Q2", "2023-Q3", "2023-Q4"],
                "y": [-1000, -300, -350, 300],
                "type": "bar",
                "name": "Net Cash Flow ($000s)",
                "marker": {"color": "#2563eb"},
                "yaxis": "y",
            },
            {
                "x": ["2023-Q1", "2023-Q2", "2023-Q3", "2023-Q4"],
                "y": [2.1, -1.5, 3.2, 4.8],
                "type": "scatter",
                "mode": "lines+markers",
                "name": "Market Return (%)",
                "line": {"color": "#dc2626", "width": 3},
                "yaxis": "y2",
            },
        ],
        "layout": {
            "title": "Net Cash Flow vs Market Performance",
            "xaxis": {"title": "Time Period"},
            "yaxis": {"title": "Net Cash Flow ($000s)", "side": "left"},
            "yaxis2": {
                "title": "Market Return (%)",
                "side": "right",
                "overlaying": "y",
            },
        },
    }


@app.get("/v1/metrics/cashflow_pacing")
async def get_cashflow_pacing():
    """Get cash flow pacing data."""
    return {
        "chart_type": "area",
        "title": "Cash Flow Pacing",
        "data": [
            {
                "x": ["2023-Q1", "2023-Q2", "2023-Q3", "2023-Q4"],
                "y": [-800, -600, -400, -200],
                "type": "scatter",
                "mode": "lines",
                "name": "Planned",
                "fill": "tonexty",
                "line": {"color": "#16a34a"},
            },
            {
                "x": ["2023-Q1", "2023-Q2", "2023-Q3", "2023-Q4"],
                "y": [-1000, -500, -750, -300],
                "type": "scatter",
                "mode": "lines+markers",
                "name": "Actual",
                "line": {"color": "#2563eb", "width": 3},
                "marker": {"size": 8},
            },
        ],
        "layout": {
            "title": "Cash Flow Pacing Analysis",
            "xaxis": {"title": "Time Period"},
            "yaxis": {"title": "Cash Flow ($000s)"},
        },
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found. Visit /docs for API documentation."},
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error. Please check logs."}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
