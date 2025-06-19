import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  PieChart, 
  Activity,
  DollarSign,
  Percent,
  Target,
  Calendar,
  Download,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Info
} from 'lucide-react';
import { PlotlyChart } from '../components/PlotlyChart';
import { analysisService } from '../services/analysisService';
import { fileStore } from '../services/fileStore';

interface AnalysisMetrics {
  'Fund IRR'?: number;
  'TVPI'?: number;
  'DPI'?: number;
  'RVPI'?: number;
  'Total Contributions'?: number;
  'Total Distributions'?: number;
  'Final NAV'?: number;
  'PME+'?: number;
  'Direct Alpha'?: number;
  'Modified IRR'?: number;
  'Cash-on-Cash Multiple'?: number;
}

interface AnalysisData {
  success: boolean;
  metrics?: AnalysisMetrics;
  charts?: any;
  summary?: any;
  request_id?: string;
  error?: string;
}

const Analysis: React.FC = () => {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [twrChartData, setTwrChartData] = useState<any>(null);

  useEffect(() => {
    loadAnalysisData();
    loadTWRChart();
  }, []);

  const loadAnalysisData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Try to get existing analysis results first
      const fileState = fileStore.getState();
      let results;
      
      if (fileState.analysisResults) {
        results = fileState.analysisResults;
      } else {
        // Run simple analysis if no results exist
        results = await analysisService.runSimpleAnalysis();
      }
      
      if (results.success) {
        setAnalysisData(results);
      } else {
        setError(results.detail || results.error || 'Analysis failed');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const loadTWRChart = async () => {
    try {
      const chartData = await analysisService.getTWRvsIndex();
      setTwrChartData(chartData);
    } catch (err) {
      console.warn('Failed to load TWR chart:', err);
    }
  };

  const handleRefresh = () => {
    loadAnalysisData();
    loadTWRChart();
  };

  const formatCurrency = (value: number | undefined): string => {
    if (value === undefined || value === null) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value: number | undefined): string => {
    if (value === undefined || value === null) return 'N/A';
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatMultiple = (value: number | undefined): string => {
    if (value === undefined || value === null) return 'N/A';
    return `${value.toFixed(2)}x`;
  };

  const getMetricCards = () => {
    if (!analysisData?.metrics) return [];

    const metrics = analysisData.metrics;
    
    return [
      {
        title: 'Fund IRR',
        value: formatPercentage(metrics['Fund IRR']),
        icon: TrendingUp,
        color: 'text-green-400',
        bgColor: 'bg-green-900/20',
        borderColor: 'border-green-800',
        description: 'Internal Rate of Return'
      },
      {
        title: 'TVPI',
        value: formatMultiple(metrics['TVPI']),
        icon: BarChart3,
        color: 'text-blue-400',
        bgColor: 'bg-blue-900/20',
        borderColor: 'border-blue-800',
        description: 'Total Value to Paid-In'
      },
      {
        title: 'DPI',
        value: formatMultiple(metrics['DPI']),
        icon: DollarSign,
        color: 'text-purple-400',
        bgColor: 'bg-purple-900/20',
        borderColor: 'border-purple-800',
        description: 'Distributions to Paid-In'
      },
      {
        title: 'RVPI',
        value: formatMultiple(metrics['RVPI']),
        icon: PieChart,
        color: 'text-yellow-400',
        bgColor: 'bg-yellow-900/20',
        borderColor: 'border-yellow-800',
        description: 'Residual Value to Paid-In'
      },
      {
        title: 'Total Contributions',
        value: formatCurrency(metrics['Total Contributions']),
        icon: Target,
        color: 'text-cyan-400',
        bgColor: 'bg-cyan-900/20',
        borderColor: 'border-cyan-800',
        description: 'Total Capital Called'
      },
      {
        title: 'Total Distributions',
        value: formatCurrency(metrics['Total Distributions']),
        icon: Activity,
        color: 'text-orange-400',
        bgColor: 'bg-orange-900/20',
        borderColor: 'border-orange-800',
        description: 'Total Cash Returned'
      }
    ];
  };

  if (isLoading) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 text-primary animate-spin mx-auto mb-4" />
            <p className="text-gray-400">Loading analysis data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="bg-red-900/20 border border-red-800 rounded-xl p-6 text-center">
          <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">Analysis Error</h3>
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={handleRefresh}
            className="btn-primary"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry Analysis
          </button>
        </div>
      </div>
    );
  }

  const metricCards = getMetricCards();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="p-6 max-w-7xl mx-auto"
    >
      {/* Header */}
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            PME Analysis Dashboard
          </h1>
          <p className="text-gray-400">
            Comprehensive performance metrics and benchmarking analysis
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleRefresh}
            className="btn-ghost"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
          <button className="btn-primary">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </button>
        </div>
      </div>

      {/* Success Indicator */}
      {analysisData?.success && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 bg-green-900/20 border border-green-800 rounded-xl p-4 flex items-center"
        >
          <CheckCircle className="w-5 h-5 text-green-400 mr-3" />
          <div>
            <p className="text-green-400 font-medium">Analysis Complete</p>
            {analysisData.request_id && (
              <p className="text-gray-400 text-sm">Request ID: {analysisData.request_id}</p>
            )}
          </div>
        </motion.div>
      )}

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {metricCards.map((metric, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            whileHover={{ y: -4, boxShadow: "0 8px 28px rgba(0,0,0,0.3)" }}
            className={`metric-card ${metric.bgColor} ${metric.borderColor}`}
          >
            <div className="flex items-center justify-between mb-4">
              <metric.icon className={`w-8 h-8 ${metric.color}`} />
              <Info className="w-4 h-4 text-gray-500" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-1">
              {metric.title}
            </h3>
            <p className="text-2xl font-bold text-white mb-2">
              {metric.value}
            </p>
            <p className="text-xs text-gray-400">
              {metric.description}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* TWR vs Index Chart */}
        {twrChartData && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="chart-container"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-primary" />
              Time-Weighted Return Comparison
            </h3>
            <PlotlyChart
              data={twrChartData.data}
              layout={twrChartData.layout}
              className="h-80"
            />
          </motion.div>
        )}

        {/* Performance Summary */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="chart-container"
        >
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-primary" />
            Performance Summary
          </h3>
          {analysisData?.summary ? (
            <div className="space-y-4">
              <div className="bg-gray-900/50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Fund Performance</h4>
                <p className="text-white">{analysisData.summary.fund_performance || 'Strong performance metrics'}</p>
              </div>
              <div className="bg-gray-900/50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-300 mb-2">vs Benchmark</h4>
                <p className="text-white">{analysisData.summary.vs_benchmark || 'Competitive positioning'}</p>
              </div>
              <div className="bg-gray-900/50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Risk Profile</h4>
                <p className="text-white">{analysisData.summary.risk_profile || 'Balanced risk exposure'}</p>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Performance summary will appear here</p>
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Additional Analysis Tools */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
        className="chart-container"
      >
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <Calendar className="w-5 h-5 mr-2 text-primary" />
          Analysis Tools
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="btn-secondary text-left p-4 h-auto">
            <Target className="w-6 h-6 text-primary mb-2" />
            <h4 className="font-medium text-white mb-1">Scenario Analysis</h4>
            <p className="text-sm text-gray-400">Test different market conditions</p>
          </button>
          <button className="btn-secondary text-left p-4 h-auto">
            <Percent className="w-6 h-6 text-primary mb-2" />
            <h4 className="font-medium text-white mb-1">Sensitivity Analysis</h4>
            <p className="text-sm text-gray-400">Analyze key variable impacts</p>
          </button>
          <button className="btn-secondary text-left p-4 h-auto">
            <Activity className="w-6 h-6 text-primary mb-2" />
            <h4 className="font-medium text-white mb-1">Monte Carlo</h4>
            <p className="text-sm text-gray-400">Probabilistic modeling</p>
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default Analysis; 