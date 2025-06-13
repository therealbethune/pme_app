import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from scipy.optimize import minimize
import logging

from models import Fund, Portfolio, PortfolioFund, CashFlow, NAV
from analysis_engine import PMEAnalysisEngine

logger = logging.getLogger(__name__)

class PortfolioService:
    """Service for portfolio-level analytics and optimization."""
    
    def __init__(self, db: Session):
        self.db = db
        self.analysis_engine = PMEAnalysisEngine()
    
    async def build_portfolio(self, fund_ids: List[int], portfolio_name: str = "New Portfolio") -> Portfolio:
        """Build a new portfolio from fund IDs."""
        try:
            # Create new portfolio
            portfolio = Portfolio(name=portfolio_name)
            self.db.add(portfolio)
            self.db.flush()  # Get portfolio ID
            
            # Add funds to portfolio with equal weights initially
            weight = 1.0 / len(fund_ids) if fund_ids else 0.0
            
            for fund_id in fund_ids:
                fund = self.db.query(Fund).filter(Fund.id == fund_id).first()
                if not fund:
                    logger.warning(f"Fund {fund_id} not found")
                    continue
                    
                portfolio_fund = PortfolioFund(
                    portfolio_id=portfolio.id,
                    fund_id=fund_id,
                    weight=weight
                )
                self.db.add(portfolio_fund)
            
            self.db.commit()
            logger.info(f"Created portfolio '{portfolio_name}' with {len(fund_ids)} funds")
            return portfolio
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error building portfolio: {str(e)}")
            raise
    
    async def calc_portfolio_kpis(self, portfolio_id: int) -> Dict:
        """Calculate comprehensive portfolio KPIs including Markowitz optimal weights."""
        try:
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                raise ValueError(f"Portfolio {portfolio_id} not found")
            
            # Get portfolio funds with current weights
            portfolio_funds = self.db.query(PortfolioFund).filter(
                PortfolioFund.portfolio_id == portfolio_id
            ).all()
            
            if not portfolio_funds:
                return {"error": "No funds in portfolio"}
            
            # Calculate individual fund metrics
            fund_metrics = []
            fund_returns = []
            fund_weights = []
            
            for pf in portfolio_funds:
                fund_data = await self._get_fund_data(pf.fund_id)
                if fund_data:
                    metrics = self.analysis_engine.calculate_metrics(
                        fund_data['cash_flows'], 
                        fund_data['nav_data']
                    )
                    fund_metrics.append(metrics)
                    fund_returns.append(self._calculate_quarterly_returns(fund_data))
                    fund_weights.append(pf.weight)
            
            if not fund_metrics:
                return {"error": "No valid fund data"}
            
            # Portfolio-weighted KPIs
            portfolio_kpis = self._calc_weighted_kpis(fund_metrics, fund_weights)
            
            # Correlation matrix
            correlation_matrix = self._calc_correlation_matrix(fund_returns)
            
            # Markowitz optimization
            optimal_weights = self._calc_optimal_weights(fund_returns, fund_weights)
            
            # Portfolio risk metrics
            risk_metrics = self._calc_portfolio_risk(fund_returns, fund_weights)
            
            # Diversification score
            diversification_score = self._calc_diversification_score(correlation_matrix, fund_weights)
            
            return {
                "portfolio_id": portfolio_id,
                "portfolio_name": portfolio.name,
                "num_funds": len(fund_metrics),
                "kpis": portfolio_kpis,
                "correlation_matrix": correlation_matrix.tolist() if correlation_matrix is not None else None,
                "optimal_weights": optimal_weights,
                "current_weights": fund_weights,
                "risk_metrics": risk_metrics,
                "diversification_score": diversification_score,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio KPIs: {str(e)}")
            raise
    
    def _calc_weighted_kpis(self, fund_metrics: List[Dict], weights: List[float]) -> Dict:
        """Calculate portfolio-weighted KPIs."""
        if not fund_metrics or not weights:
            return {}
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights] if total_weight > 0 else weights
        
        weighted_kpis = {}
        
        # Key metrics to aggregate
        metrics_to_weight = ['Fund IRR', 'TVPI', 'DPI', 'RVPI', 'Alpha', 'Beta']
        
        for metric in metrics_to_weight:
            values = [m.get(metric, 0) for m in fund_metrics]
            if all(isinstance(v, (int, float)) and not np.isnan(v) for v in values):
                weighted_kpis[f'Portfolio {metric}'] = sum(v * w for v, w in zip(values, normalized_weights))
        
        # Total values (sum, not weighted average)
        total_contributions = sum(m.get('Total Contributions', 0) for m in fund_metrics)
        total_distributions = sum(m.get('Total Distributions', 0) for m in fund_metrics)
        final_nav = sum(m.get('Final NAV', 0) for m in fund_metrics)
        
        weighted_kpis.update({
            'Portfolio Total Contributions': total_contributions,
            'Portfolio Total Distributions': total_distributions,
            'Portfolio Final NAV': final_nav,
            'Portfolio TVPI': (total_distributions + final_nav) / total_contributions if total_contributions > 0 else 0
        })
        
        return weighted_kpis
    
    def _calc_correlation_matrix(self, fund_returns: List[List[float]]) -> Optional[np.ndarray]:
        """Calculate correlation matrix of fund returns."""
        if len(fund_returns) < 2:
            return None
        
        try:
            # Convert to DataFrame for easier correlation calculation
            df = pd.DataFrame(fund_returns).T
            correlation_matrix = df.corr().values
            
            # Replace NaN with 0
            correlation_matrix = np.nan_to_num(correlation_matrix)
            
            return correlation_matrix
            
        except Exception as e:
            logger.error(f"Error calculating correlation matrix: {str(e)}")
            return None
    
    def _calc_optimal_weights(self, fund_returns: List[List[float]], current_weights: List[float]) -> Dict:
        """Calculate Markowitz optimal weights."""
        if len(fund_returns) < 2:
            return {"message": "Need at least 2 funds for optimization"}
        
        try:
            # Convert returns to numpy array
            returns_array = np.array(fund_returns)
            
            # Calculate mean returns and covariance matrix
            mean_returns = np.mean(returns_array, axis=1)
            cov_matrix = np.cov(returns_array)
            
            num_assets = len(fund_returns)
            
            # Objective function: minimize portfolio variance
            def objective(weights):
                return np.dot(weights.T, np.dot(cov_matrix, weights))
            
            # Constraints: weights sum to 1
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            
            # Bounds: weights between 0 and 1 (long-only)
            bounds = tuple((0, 1) for _ in range(num_assets))
            
            # Initial guess: equal weights
            initial_weights = np.array([1.0 / num_assets] * num_assets)
            
            # Optimize
            result = minimize(
                objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if result.success:
                optimal_weights = result.x.tolist()
                
                # Calculate expected return and risk for optimal portfolio
                optimal_return = np.dot(optimal_weights, mean_returns)
                optimal_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
                
                return {
                    "optimal_weights": optimal_weights,
                    "current_weights": current_weights,
                    "expected_return": float(optimal_return),
                    "expected_risk": float(optimal_risk),
                    "optimization_success": True
                }
            else:
                return {
                    "message": "Optimization failed",
                    "error": result.message,
                    "optimization_success": False
                }
                
        except Exception as e:
            logger.error(f"Error in Markowitz optimization: {str(e)}")
            return {"error": str(e), "optimization_success": False}
    
    def _calc_portfolio_risk(self, fund_returns: List[List[float]], weights: List[float]) -> Dict:
        """Calculate portfolio risk metrics."""
        if not fund_returns or not weights:
            return {}
        
        try:
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights] if total_weight > 0 else weights
            
            # Calculate portfolio returns
            returns_array = np.array(fund_returns)
            portfolio_returns = np.dot(normalized_weights, returns_array)
            
            # Risk metrics
            volatility = np.std(portfolio_returns) * np.sqrt(4)  # Annualized (quarterly data)
            max_drawdown = self._calculate_max_drawdown(portfolio_returns)
            var_95 = np.percentile(portfolio_returns, 5)  # 5% VaR
            
            # Sharpe ratio (assuming risk-free rate of 2.5%)
            risk_free_rate = 0.025 / 4  # Quarterly
            excess_returns = portfolio_returns - risk_free_rate
            sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) > 0 else 0
            
            return {
                "portfolio_volatility": float(volatility),
                "portfolio_max_drawdown": float(max_drawdown),
                "portfolio_var_95": float(var_95),
                "portfolio_sharpe_ratio": float(sharpe_ratio * np.sqrt(4))  # Annualized
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {str(e)}")
            return {}
    
    def _calc_diversification_score(self, correlation_matrix: Optional[np.ndarray], weights: List[float]) -> float:
        """Calculate diversification score (0-1, higher is better)."""
        if correlation_matrix is None or len(weights) < 2:
            return 0.0
        
        try:
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights] if total_weight > 0 else weights
            weights_array = np.array(normalized_weights)
            
            # Portfolio correlation is weighted average of pairwise correlations
            portfolio_correlation = 0.0
            total_pairs = 0
            
            for i in range(len(weights)):
                for j in range(i + 1, len(weights)):
                    weight_product = weights_array[i] * weights_array[j]
                    portfolio_correlation += correlation_matrix[i, j] * weight_product
                    total_pairs += weight_product
            
            if total_pairs > 0:
                portfolio_correlation /= total_pairs
            
            # Diversification score: 1 - average correlation
            diversification_score = max(0.0, 1.0 - abs(portfolio_correlation))
            
            return float(diversification_score)
            
        except Exception as e:
            logger.error(f"Error calculating diversification score: {str(e)}")
            return 0.0
    
    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Calculate maximum drawdown from returns series."""
        cumulative = np.cumprod(1 + returns)
        rolling_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - rolling_max) / rolling_max
        return float(np.min(drawdown))
    
    def _calculate_quarterly_returns(self, fund_data: Dict) -> List[float]:
        """Calculate quarterly returns for a fund."""
        try:
            nav_data = fund_data.get('nav_data', [])
            if len(nav_data) < 2:
                return [0.0]  # Return zero if insufficient data
            
            # Sort by date
            nav_data = sorted(nav_data, key=lambda x: x['date'])
            
            # Calculate quarterly returns
            returns = []
            for i in range(1, len(nav_data)):
                prev_nav = nav_data[i-1]['nav']
                curr_nav = nav_data[i]['nav']
                if prev_nav > 0:
                    return_pct = (curr_nav - prev_nav) / prev_nav
                    returns.append(return_pct)
            
            return returns if returns else [0.0]
            
        except Exception as e:
            logger.error(f"Error calculating quarterly returns: {str(e)}")
            return [0.0]
    
    async def _get_fund_data(self, fund_id: int) -> Optional[Dict]:
        """Get cash flow and NAV data for a fund."""
        try:
            fund = self.db.query(Fund).filter(Fund.id == fund_id).first()
            if not fund:
                return None
            
            # Get cash flows
            cash_flows = []
            cf_entries = self.db.query(CashFlow).filter(CashFlow.fund_id == fund_id).order_by(CashFlow.date).all()
            for cf in cf_entries:
                cash_flows.append({
                    'date': cf.date,
                    'amount': cf.amount
                })
            
            # Get NAV data
            nav_data = []
            nav_entries = self.db.query(NAV).filter(NAV.fund_id == fund_id).order_by(NAV.date).all()
            for nav in nav_entries:
                nav_data.append({
                    'date': nav.date,
                    'nav': nav.nav_value
                })
            
            return {
                'fund_id': fund_id,
                'fund_name': fund.name,
                'cash_flows': cash_flows,
                'nav_data': nav_data
            }
            
        except Exception as e:
            logger.error(f"Error getting fund data for {fund_id}: {str(e)}")
            return None 