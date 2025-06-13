import { useState } from "react";

interface PortfolioMetrics {
  "Total NAV": number;
  "Annualized Return": number;
  "Volatility": number;
  "Sharpe (rf=0)": number;
  "Funds": number;
  "Max Drawdown": number;
  "Calmar Ratio": number;
  files_processed?: number;
  file_names?: string[];
}

export default function PortfolioMetrics() {
  const [metrics, setMetrics] = useState<PortfolioMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<any>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;

    setLoading(true);
    setError(null);
    setMetrics(null);
    setPreviewData(null);

    try {
      const formData = new FormData();
      Array.from(e.target.files).forEach(file => {
        formData.append("files", file);
      });

      // First, preview the data
      const previewResponse = await fetch("/portfolio/preview", {
        method: "POST",
        body: formData,
      });

      if (!previewResponse.ok) {
        throw new Error(`Preview failed: ${previewResponse.statusText}`);
      }

      const preview = await previewResponse.json();
      setPreviewData(preview);

      // Then calculate metrics
      const metricsResponse = await fetch("/portfolio/metrics", {
        method: "POST",
        body: formData,
      });

      if (!metricsResponse.ok) {
        throw new Error(`Metrics calculation failed: ${metricsResponse.statusText}`);
      }

      const metricsData = await metricsResponse.json();
      setMetrics(metricsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatNumber = (value: number, decimals: number = 3) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  };

  const getPerformanceColor = (value: number, isPositiveGood: boolean = true) => {
    if (value === 0) return "text-gray-500";
    const isPositive = value > 0;
    return (isPositive === isPositiveGood) ? "text-green-600" : "text-red-600";
  };

  return (
    <div className="p-4 space-y-6">
      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          📊 Portfolio Analytics
        </h2>
        
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <input
              type="file"
              multiple
              accept=".csv"
              onChange={handleUpload}
              disabled={loading}
              className="flex-1 p-2 border border-gray-300 rounded"
            />
            <button
              disabled={loading}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
            >
              {loading ? "Processing..." : "Upload Files"}
            </button>
          </div>

          <div className="text-sm text-gray-600">
            Upload multiple CSV files containing fund data with Date and NAV columns.
          </div>

          {error && (
            <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Preview Section */}
      {previewData && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Data Preview</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 bg-gray-200 rounded text-sm">
                {previewData.files_processed} files processed
              </span>
            </div>
            
            <div className="grid gap-4">
              {Object.entries(previewData.preview).map(([filename, data]: [string, any]) => (
                <div key={filename} className="border rounded-lg p-4">
                  <h4 className="font-medium mb-2">{filename}</h4>
                  {data.error ? (
                    <div className="text-red-600 text-sm">{data.error}</div>
                  ) : (
                    <div className="text-sm text-gray-600">
                      {data.rows} rows, {data.columns?.length} columns: {data.columns?.join(", ")}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Metrics Section */}
      {metrics && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Portfolio Value */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-2">Portfolio Value</h3>
            <div className="text-2xl font-bold text-blue-600">
              {formatCurrency(metrics["Total NAV"])}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Across {metrics.Funds} fund{metrics.Funds !== 1 ? 's' : ''}
            </div>
          </div>

          {/* Annualized Return */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-2">Annualized Return</h3>
            <div className={`text-2xl font-bold ${getPerformanceColor(metrics["Annualized Return"])}`}>
              {formatPercentage(metrics["Annualized Return"])}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Geometric mean return
            </div>
          </div>

          {/* Volatility */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-2">Volatility</h3>
            <div className="text-2xl font-bold">
              {formatPercentage(metrics.Volatility)}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Annualized standard deviation
            </div>
          </div>

          {/* Sharpe Ratio */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-2">Sharpe Ratio</h3>
            <div className={`text-2xl font-bold ${getPerformanceColor(metrics["Sharpe (rf=0)"])}`}>
              {formatNumber(metrics["Sharpe (rf=0)"])}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Return per unit of risk
            </div>
          </div>

          {/* Max Drawdown */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-2">Max Drawdown</h3>
            <div className={`text-2xl font-bold ${getPerformanceColor(metrics["Max Drawdown"], false)}`}>
              {formatPercentage(metrics["Max Drawdown"])}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Peak-to-trough decline
            </div>
          </div>

          {/* Calmar Ratio */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-2">Calmar Ratio</h3>
            <div className={`text-2xl font-bold ${getPerformanceColor(metrics["Calmar Ratio"])}`}>
              {formatNumber(metrics["Calmar Ratio"])}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Return / |Max Drawdown|
            </div>
          </div>
        </div>
      )}

      {/* Performance Summary */}
      {metrics && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Performance Summary</h3>
          <div className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <h4 className="font-medium mb-2">Risk Assessment</h4>
                <div className="text-sm text-gray-600">
                  {metrics["Sharpe (rf=0)"] > 1.0 ? "Excellent" :
                   metrics["Sharpe (rf=0)"] > 0.5 ? "Good" :
                   metrics["Sharpe (rf=0)"] > 0 ? "Moderate" : "Poor"} risk-adjusted returns
                </div>
              </div>
              
              <div>
                <h4 className="font-medium mb-2">Portfolio Composition</h4>
                <div className="text-sm text-gray-600">
                  {metrics.files_processed} file{metrics.files_processed !== 1 ? 's' : ''} processed
                  {metrics.file_names && (
                    <div className="mt-1 flex flex-wrap gap-1">
                      {metrics.file_names.map((name, idx) => (
                        <span key={idx} className="px-2 py-1 bg-gray-100 rounded text-xs">
                          {name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="pt-4 border-t">
              <button className="w-full px-4 py-2 border border-gray-300 rounded hover:bg-gray-50">
                📄 Generate Detailed Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 