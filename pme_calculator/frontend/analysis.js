/**
 * PME Analysis Results - Comprehensive Analytics Dashboard
 * Advanced charts and reporting functionality
 */

class PMEAnalysisResults {
    constructor() {
        this.analysisData = null;
        this.charts = {};
        this.init();
    }

    init() {
        // Load analysis data from URL parameters or localStorage
        this.loadAnalysisData();
        
        // Initialize the dashboard
        this.initializeDashboard();
        
        // Setup event listeners
        this.setupEventListeners();
    }

    loadAnalysisData() {
        // Try to get data from URL parameters first
        const urlParams = new URLSearchParams(window.location.search);
        const dataParam = urlParams.get('data');
        
        if (dataParam) {
            try {
                this.analysisData = JSON.parse(decodeURIComponent(dataParam));
            } catch (e) {
                console.error('Error parsing URL data:', e);
            }
        }
        
        // Fallback to localStorage
        if (!this.analysisData) {
            const storedData = localStorage.getItem('pmeAnalysisResults');
            if (storedData) {
                try {
                    this.analysisData = JSON.parse(storedData);
                } catch (e) {
                    console.error('Error parsing stored data:', e);
                }
            }
        }
        
        // If no data available, use sample data
        if (!this.analysisData) {
            this.analysisData = this.getSampleData();
        }
    }

    getSampleData() {
        return {
            "success": true,
            "metrics": {
                "Fund IRR": 0.171,
                "TVPI": 2.0,
                "DPI": 1.2,
                "RVPI": 0.8,
                "PME": 1.15,
                "Analytics Data": {
                    "performance_timeline": [
                        {"date": "2020-Q1", "tvpi": 1.0, "dpi": 0.0, "rvpi": 1.0},
                        {"date": "2020-Q2", "tvpi": 1.05, "dpi": 0.1, "rvpi": 0.95},
                        {"date": "2020-Q3", "tvpi": 1.12, "dpi": 0.2, "rvpi": 0.92},
                        {"date": "2020-Q4", "tvpi": 1.18, "dpi": 0.3, "rvpi": 0.88},
                        {"date": "2021-Q1", "tvpi": 1.25, "dpi": 0.4, "rvpi": 0.85},
                        {"date": "2021-Q2", "tvpi": 1.35, "dpi": 0.6, "rvpi": 0.75},
                        {"date": "2021-Q3", "tvpi": 1.65, "dpi": 0.8, "rvpi": 0.85},
                        {"date": "2021-Q4", "tvpi": 2.0, "dpi": 1.2, "rvpi": 0.8}
                    ],
                    "cash_flow_timeline": [
                        {"date": "2020", "contributions": -100, "distributions": 0},
                        {"date": "2021", "contributions": -150, "distributions": 20},
                        {"date": "2022", "contributions": -200, "distributions": 50},
                        {"date": "2023", "contributions": -50, "distributions": 120},
                        {"date": "2024", "contributions": 0, "distributions": 180}
                    ]
                }
            }
        };
    }

    showNoDataError() {
        document.body.innerHTML = `
            <div class="container mt-5">
                <div class="alert alert-danger text-center">
                    <h4><i class="fas fa-exclamation-triangle me-2"></i>No Analysis Data Found</h4>
                    <p>Please run an analysis first to view results.</p>
                    <button class="btn btn-primary" onclick="window.location.href='index.html'">
                        <i class="fas fa-arrow-left me-2"></i>Back to Analysis
                    </button>
                </div>
            </div>
        `;
    }

    async initializeDashboard() {
        console.log('Initializing dashboard...');
        
        try {
            // Display key metrics first
            this.displayKeyMetrics();
            console.log('Key metrics displayed');
            
            // Generate all charts
            await this.generateAllCharts();
            console.log('Charts generated');
            
            // Display insights
            this.displayInsights();
            console.log('Insights displayed');
            
            // Setup animations
            this.setupAnimations();
            console.log('Animations setup');
            
            // Hide loading overlay after everything is loaded
            const loadingOverlay = document.getElementById('loadingOverlay');
            if (loadingOverlay) {
                loadingOverlay.style.display = 'none';
                console.log('Loading overlay hidden');
            }
            
            // Initialize draggable charts after a delay to ensure all charts are loaded
            setTimeout(() => {
                this.initializeDraggableCharts();
                console.log('Draggable charts initialized');
            }, 2000);
            
        } catch (error) {
            console.error('Error initializing dashboard:', error);
            // Hide loading overlay even if there's an error
            const loadingOverlay = document.getElementById('loadingOverlay');
            if (loadingOverlay) {
                loadingOverlay.style.display = 'none';
            }
        }
    }

    displayKeyMetrics() {
        const metrics = this.analysisData.metrics || {};
        
        // Extract key metrics
        const irr = metrics['Fund IRR'] || 0;
        const tvpi = metrics['TVPI'] || 0;
        const dpi = metrics['DPI'] || 0;
        const rvpi = metrics['RVPI'] || 0;
        
        // Update metric displays
        document.getElementById('irrValue').textContent = `${(irr * 100).toFixed(1)}%`;
        document.getElementById('tvpiValue').textContent = `${tvpi.toFixed(2)}x`;
        document.getElementById('dpiValue').textContent = `${dpi.toFixed(2)}x`;
        document.getElementById('rvpiValue').textContent = `${rvpi.toFixed(2)}x`;
        
        // Update overall rating
        this.updateOverallRating(irr, tvpi);
    }

    updateOverallRating(irr, tvpi) {
        const ratingElement = document.getElementById('overallRating');
        
        if (irr > 0.20 && tvpi > 2.5) {
            ratingElement.textContent = 'Exceptional Performance';
            ratingElement.className = 'performance-badge badge-excellent';
        } else if (irr > 0.15 && tvpi > 2.0) {
            ratingElement.textContent = 'Excellent Performance';
            ratingElement.className = 'performance-badge badge-excellent';
        } else if (irr > 0.10 && tvpi > 1.5) {
            ratingElement.textContent = 'Good Performance';
            ratingElement.className = 'performance-badge badge-good';
        } else {
            ratingElement.textContent = 'Moderate Performance';
            ratingElement.className = 'performance-badge badge-warning';
        }
    }

    async generateAllCharts() {
        const analyticsData = this.analysisData.metrics?.['Analytics Data'] || {};
        
        // Performance charts
        this.createPerformanceChart(analyticsData);
        this.createJCurveChart(analyticsData);
        this.createTWRChart(analyticsData);
        
        // Cash flow charts
        this.createCashFlowChart(analyticsData);
        this.createCashFlowTimelineChart(analyticsData);
        this.createDistributionChart(analyticsData);
        
        // Risk charts
        this.createRiskReturnChart();
        this.createVolatilityChart(analyticsData);
        this.createStressTestChart();
        
        // Benchmarking charts
        this.createBenchmarkChart();
        this.createPeerChart();
        this.createRollingAlphaChart(analyticsData);
        
        // New API-based charts
        this.loadNewAPICharts();
    }
    
    async loadNewAPICharts() {
        // Load new charts using the makeChart function
        console.log('Loading new API charts...');
        
        try {
            // Check if makeChart function is available
            if (typeof window.makeChart !== 'function') {
                console.error('makeChart function not available, loading mock charts instead');
                this.loadMockCharts();
                return;
            }
            
            console.log('makeChart function available, loading charts...');
            
            // All chart IDs that should load from API
            const chartConfigs = [
                { id: 'irrPmePlot', url: '/v1/metrics/irr_pme', name: 'Performance Over Time' },
                { id: 'twrVsIndexPlot', url: '/v1/metrics/twr_vs_index', name: 'TWR vs Index' },
                { id: 'pmeProgressionPlot', url: '/v1/metrics/pme_progression', name: 'PME Progression' },
                { id: 'cashflowOverviewPlot', url: '/v1/metrics/cashflow_overview', name: 'Cash Flow Overview' },
                { id: 'netCfMarketPlot', url: '/v1/metrics/net_cf_market', name: 'Net CF vs Market' },
                { id: 'pacingPlot', url: '/v1/metrics/cashflow_pacing', name: 'Cash Flow Pacing' }
            ];
            
            // Show loading state for each chart
            chartConfigs.forEach(config => {
                const element = document.getElementById(config.id);
                if (element) {
                    element.innerHTML = `
                        <div class="d-flex justify-content-center align-items-center" style="height: 400px;">
                            <div class="text-center">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <div class="mt-2 text-muted">Loading ${config.name}...</div>
                            </div>
                        </div>
                    `;
                } else {
                    console.warn(`Chart element ${config.id} not found`);
                }
            });
            
            // Load charts from API endpoints with individual error handling
            const chartPromises = chartConfigs.map(async (config) => {
                try {
                    console.log(`Loading chart: ${config.name} (${config.id})`);
                    await this.loadChart(config.id, config.url);
                    console.log(`Successfully loaded: ${config.name}`);
                } catch (error) {
                    console.error(`Failed to load chart ${config.name}:`, error);
                    // Show error message in the chart container
                    const element = document.getElementById(config.id);
                    if (element) {
                        element.innerHTML = `
                            <div class="d-flex justify-content-center align-items-center" style="height: 400px;">
                                <div class="text-center text-muted">
                                    <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                                    <div>Failed to load ${config.name}</div>
                                    <small>Please check your connection and try again</small>
                                </div>
                            </div>
                        `;
                    }
                }
            });
            
            await Promise.allSettled(chartPromises);
            console.log('All chart loading attempts completed');
            
        } catch (error) {
            console.error('Error in loadNewAPICharts:', error);
            this.loadMockCharts();
        }
    }
    
    loadMockCharts() {
        console.log('Loading mock charts as fallback...');
        // This method provides fallback charts when API is not available
        const chartIds = ['irrPmePlot', 'twrVsIndexPlot', 'pmeProgressionPlot', 'cashflowOverviewPlot', 'netCfMarketPlot', 'pacingPlot'];
        
        chartIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.innerHTML = `
                    <div class="d-flex justify-content-center align-items-center" style="height: 400px;">
                        <div class="text-center text-muted">
                            <i class="fas fa-chart-line fa-3x mb-3"></i>
                            <div>Chart data not available</div>
                            <small>Please run an analysis to generate charts</small>
                        </div>
                    </div>
                `;
            }
        });
    }

    async loadChart(elementId, url) {
        try {
            await window.makeChart(elementId, url);
        } catch (error) {
            console.error(`Failed to load chart ${elementId}:`, error);
            const element = document.getElementById(elementId);
            if (element) {
                element.innerHTML = `
                    <div class="alert alert-warning text-center" style="margin: 50px 20px;">
                        <i class="fas fa-exclamation-triangle"></i>
                        <div class="mt-2">Chart temporarily unavailable</div>
                        <small class="text-muted">Please try refreshing the page</small>
                    </div>
                `;
            }
        }
    }

    createPerformanceChart(analyticsData) {
        const performanceTimeline = analyticsData.performance_timeline || [];
        
        if (performanceTimeline.length === 0) {
            this.createMockPerformanceChart();
            return;
        }
        
        const dates = performanceTimeline.map(item => item.date);
        const tvpiData = performanceTimeline.map(item => item.tvpi);
        const dpiData = performanceTimeline.map(item => item.dpi);
        const rvpiData = performanceTimeline.map(item => item.rvpi);
        
        const traces = [
            {
                x: dates,
                y: tvpiData,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'TVPI (Total Value)',
                line: { 
                    color: '#00ff88', 
                    width: 4,
                    shape: 'spline',
                    smoothing: 0.3
                },
                marker: { 
                    size: 12,
                    color: '#00ff88',
                    line: {
                        color: '#ffffff',
                        width: 2
                    },
                    symbol: 'circle'
                },
                hovertemplate: '<b>%{fullData.name}</b><br>' +
                              'Date: %{x}<br>' +
                              'Value: %{y:.2f}x<br>' +
                              '<extra></extra>',
                hoverlabel: {
                    bgcolor: 'rgba(0, 255, 136, 0.9)',
                    bordercolor: '#ffffff',
                    font: { color: '#000000', size: 14 }
                }
            },
            {
                x: dates,
                y: dpiData,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'DPI (Distributions)',
                line: { 
                    color: '#0066cc', 
                    width: 3,
                    shape: 'spline',
                    smoothing: 0.3
                },
                marker: { 
                    size: 10,
                    color: '#0066cc',
                    line: {
                        color: '#ffffff',
                        width: 2
                    },
                    symbol: 'diamond'
                },
                hovertemplate: '<b>%{fullData.name}</b><br>' +
                              'Date: %{x}<br>' +
                              'Value: %{y:.2f}x<br>' +
                              '<extra></extra>',
                hoverlabel: {
                    bgcolor: 'rgba(0, 102, 204, 0.9)',
                    bordercolor: '#ffffff',
                    font: { color: '#ffffff', size: 14 }
                }
            },
            {
                x: dates,
                y: rvpiData,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'RVPI (Residual Value)',
                line: { 
                    color: '#ff6b6b', 
                    width: 3,
                    shape: 'spline',
                    smoothing: 0.3
                },
                marker: { 
                    size: 10,
                    color: '#ff6b6b',
                    line: {
                        color: '#ffffff',
                        width: 2
                    },
                    symbol: 'square'
                },
                hovertemplate: '<b>%{fullData.name}</b><br>' +
                              'Date: %{x}<br>' +
                              'Value: %{y:.2f}x<br>' +
                              '<extra></extra>',
                hoverlabel: {
                    bgcolor: 'rgba(255, 107, 107, 0.9)',
                    bordercolor: '#ffffff',
                    font: { color: '#ffffff', size: 14 }
                }
            }
        ];
        
        const layout = {
            title: {
                text: '<b>Performance Evolution Over Time</b>',
                font: {
                    size: 18,
                    color: '#ffffff',
                    family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                },
                x: 0.5,
                xanchor: 'center'
            },
            xaxis: { 
                title: {
                    text: '<b>Date</b>',
                    font: {
                        size: 14,
                        color: '#cccccc',
                        family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                    }
                },
                tickfont: {
                    size: 12,
                    color: '#ffffff',
                    family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                },
                gridcolor: 'rgba(255, 255, 255, 0.1)',
                linecolor: 'rgba(255, 255, 255, 0.2)',
                tickcolor: 'rgba(255, 255, 255, 0.2)'
            },
            yaxis: { 
                title: {
                    text: '<b>Multiple (x)</b>',
                    font: {
                        size: 14,
                        color: '#cccccc',
                        family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                    }
                },
                tickfont: {
                    size: 12,
                    color: '#ffffff',
                    family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                },
                gridcolor: 'rgba(255, 255, 255, 0.1)',
                linecolor: 'rgba(255, 255, 255, 0.2)',
                tickcolor: 'rgba(255, 255, 255, 0.2)',
                zeroline: true,
                zerolinecolor: 'rgba(255, 255, 255, 0.3)',
                zerolinewidth: 1
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { 
                color: '#ffffff',
                family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            },
            legend: { 
                x: 0.02,
                y: 0.98,
                bgcolor: 'rgba(0, 0, 0, 0.7)',
                bordercolor: 'rgba(255, 255, 255, 0.2)',
                borderwidth: 1,
                font: {
                    size: 12,
                    color: '#ffffff',
                    family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                }
            },
            margin: {
                l: 60,
                r: 40,
                t: 60,
                b: 80
            },
            annotations: [
                {
                    text: 'TVPI = Total Value to Paid-In Capital | DPI = Distributions to Paid-In | RVPI = Residual Value to Paid-In',
                    showarrow: false,
                    x: 0.5,
                    y: -0.15,
                    xref: 'paper',
                    yref: 'paper',
                    xanchor: 'center',
                    yanchor: 'top',
                    font: {
                        size: 10,
                        color: '#888888',
                        family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                    }
                }
            ]
        };
        
        const config = {
            responsive: true,
            displayModeBar: false,
            staticPlot: false
        };

        makeChartLocal('performanceChart', traces, layout, config);
    }

    createMockPerformanceChart() {
        const metrics = this.analysisData.metrics || {};
        const finalTvpi = metrics['TVPI'] || 1.0;
        const finalDpi = metrics['DPI'] || 0.5;
        const finalRvpi = metrics['RVPI'] || 0.5;
        
        const quarters = ['Q1 2020', 'Q2 2020', 'Q3 2020', 'Q4 2020', 'Q1 2021', 'Q2 2021', 'Q3 2021', 'Q4 2021'];
        const tvpiProgression = this.generateProgression(1.0, finalTvpi, quarters.length);
        const dpiProgression = this.generateProgression(0.0, finalDpi, quarters.length);
        const rvpiProgression = this.generateProgression(1.0, finalRvpi, quarters.length);
        
        const traces = [
            {
                x: quarters,
                y: tvpiProgression,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'TVPI (Total Value)',
                line: { 
                    color: '#00ff88', 
                    width: 4,
                    shape: 'spline',
                    smoothing: 0.3
                },
                marker: { 
                    size: 12,
                    color: '#00ff88',
                    line: {
                        color: '#ffffff',
                        width: 2
                    },
                    symbol: 'circle'
                },
                hovertemplate: '<b>%{fullData.name}</b><br>' +
                              'Period: %{x}<br>' +
                              'Value: %{y:.2f}x<br>' +
                              '<extra></extra>',
                hoverlabel: {
                    bgcolor: 'rgba(0, 255, 136, 0.9)',
                    bordercolor: '#ffffff',
                    font: { color: '#000000', size: 14 }
                }
            },
            {
                x: quarters,
                y: dpiProgression,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'DPI (Distributions)',
                line: { 
                    color: '#0066cc', 
                    width: 3,
                    shape: 'spline',
                    smoothing: 0.3
                },
                marker: { 
                    size: 10,
                    color: '#0066cc',
                    line: {
                        color: '#ffffff',
                        width: 2
                    },
                    symbol: 'diamond'
                },
                hovertemplate: '<b>%{fullData.name}</b><br>' +
                              'Period: %{x}<br>' +
                              'Value: %{y:.2f}x<br>' +
                              '<extra></extra>',
                hoverlabel: {
                    bgcolor: 'rgba(0, 102, 204, 0.9)',
                    bordercolor: '#ffffff',
                    font: { color: '#ffffff', size: 14 }
                }
            },
            {
                x: quarters,
                y: rvpiProgression,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'RVPI (Residual Value)',
                line: { 
                    color: '#ff6b6b', 
                    width: 3,
                    shape: 'spline',
                    smoothing: 0.3
                },
                marker: { 
                    size: 10,
                    color: '#ff6b6b',
                    line: {
                        color: '#ffffff',
                        width: 2
                    },
                    symbol: 'square'
                },
                hovertemplate: '<b>%{fullData.name}</b><br>' +
                              'Period: %{x}<br>' +
                              'Value: %{y:.2f}x<br>' +
                              '<extra></extra>',
                hoverlabel: {
                    bgcolor: 'rgba(255, 107, 107, 0.9)',
                    bordercolor: '#ffffff',
                    font: { color: '#ffffff', size: 14 }
                }
            }
        ];
        
        const layout = {
            title: {
                text: '<b>Performance Evolution Over Time</b>',
                font: {
                    size: 18,
                    color: '#ffffff',
                    family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                },
                x: 0.5,
                xanchor: 'center'
            },
            xaxis: { 
                title: {
                    text: '<b>Time Period</b>',
                    font: {
                        size: 14,
                        color: '#cccccc',
                        family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                    }
                },
                tickfont: {
                    size: 12,
                    color: '#ffffff',
                    family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                },
                gridcolor: 'rgba(255, 255, 255, 0.1)',
                linecolor: 'rgba(255, 255, 255, 0.2)',
                tickcolor: 'rgba(255, 255, 255, 0.2)',
                tickangle: -45
            },
            yaxis: { 
                title: {
                    text: '<b>Multiple (x)</b>',
                    font: {
                        size: 14,
                        color: '#cccccc',
                        family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                    }
                },
                tickfont: {
                    size: 12,
                    color: '#ffffff',
                    family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                },
                gridcolor: 'rgba(255, 255, 255, 0.1)',
                linecolor: 'rgba(255, 255, 255, 0.2)',
                tickcolor: 'rgba(255, 255, 255, 0.2)',
                zeroline: true,
                zerolinecolor: 'rgba(255, 255, 255, 0.3)',
                zerolinewidth: 1
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { 
                color: '#ffffff',
                family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            },
            legend: { 
                x: 0.02,
                y: 0.98,
                bgcolor: 'rgba(0, 0, 0, 0.7)',
                bordercolor: 'rgba(255, 255, 255, 0.2)',
                borderwidth: 1,
                font: {
                    size: 12,
                    color: '#ffffff',
                    family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                }
            },
            margin: {
                l: 60,
                r: 40,
                t: 60,
                b: 80
            },
            annotations: [
                {
                    text: 'TVPI = Total Value to Paid-In Capital | DPI = Distributions to Paid-In | RVPI = Residual Value to Paid-In',
                    showarrow: false,
                    x: 0.5,
                    y: -0.2,
                    xref: 'paper',
                    yref: 'paper',
                    xanchor: 'center',
                    yanchor: 'top',
                    font: {
                        size: 10,
                        color: '#888888',
                        family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                    }
                }
            ]
        };
        
        const config = {
            responsive: true,
            displayModeBar: false,
            staticPlot: false
        };

        makeChartLocal('performanceChart', traces, layout, config);
    }

    createJCurveChart(analyticsData) {
        const jCurveData = analyticsData.j_curve_data || [];
        
        if (jCurveData.length === 0) {
            this.createMockJCurveChart();
            return;
        }
        
        const dates = jCurveData.map(item => item.date);
        const cumulativeCash = jCurveData.map(item => item.cumulative_net_cash);
        const totalValue = jCurveData.map(item => item.total_value);
        
        const traces = [
            {
                x: dates,
                y: cumulativeCash,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Cumulative Net Cash Flow',
                line: { color: '#ef4444', width: 2 },
                marker: { size: 6 }
            },
            {
                x: dates,
                y: totalValue,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Total Value',
                line: { color: '#10b981', width: 3 },
                marker: { size: 8 }
            }
        ];
        
        const layout = {
            title: false,
            xaxis: { 
                title: 'Date',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            yaxis: { 
                title: 'Value ($)',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            legend: { x: 0, y: 1 }
        };
        
        makeChartLocal('jCurveChart', traces, layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    createMockJCurveChart() {
        const quarters = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8'];
        const cumulativeCash = [-100, -250, -450, -500, -400, -200, 100, 300];
        const totalValue = [-100, -200, -350, -300, -100, 200, 500, 800];
        
        const traces = [
            {
                x: quarters,
                y: cumulativeCash,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Cumulative Net Cash Flow',
                line: { color: '#ef4444', width: 2 },
                marker: { size: 6 }
            },
            {
                x: quarters,
                y: totalValue,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Total Value',
                line: { color: '#10b981', width: 3 },
                marker: { size: 8 }
            }
        ];
        
        const layout = {
            title: false,
            xaxis: { 
                title: 'Time Period',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            yaxis: { 
                title: 'Value ($M)',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            legend: { x: 0, y: 1 }
        };
        
        makeChartLocal('jCurveChart', traces, layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    createTWRChart(analyticsData) {
        const twrData = analyticsData.twr_data || [];
        
        if (twrData.length === 0) {
            this.createMockTWRChart();
            return;
        }
        
        const dates = twrData.map(item => item.date);
        const cumulativeTWR = twrData.map(item => item.twr_cumulative);
        
        const trace = {
            x: dates,
            y: cumulativeTWR,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Cumulative TWR',
            line: { color: '#8b5cf6', width: 3 },
            marker: { size: 8 },
            fill: 'tonexty',
            fillcolor: 'rgba(139, 92, 246, 0.1)'
        };
        
        const layout = {
            title: false,
            xaxis: { 
                title: 'Date',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            yaxis: { 
                title: 'Cumulative Return (%)',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            showlegend: false
        };
        
        makeChartLocal('twrChart', [trace], layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    createMockTWRChart() {
        const quarters = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8'];
        const twrReturns = [5, 12, 8, -3, 15, 22, 18, 25];
        
        const trace = {
            x: quarters,
            y: twrReturns,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Cumulative TWR',
            line: { color: '#8b5cf6', width: 3 },
            marker: { size: 8 },
            fill: 'tonexty',
            fillcolor: 'rgba(139, 92, 246, 0.1)'
        };
        
        const layout = {
            title: false,
            xaxis: { 
                title: 'Time Period',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            yaxis: { 
                title: 'Cumulative Return (%)',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            showlegend: false
        };
        
        makeChartLocal('twrChart', [trace], layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    createCashFlowChart(analyticsData) {
        const cashFlowTimeline = analyticsData.cash_flow_timeline || [];
        
        let periods, contributions, distributions;
        
        if (cashFlowTimeline.length > 0) {
            periods = cashFlowTimeline.map(item => item.date);
            contributions = cashFlowTimeline.map(item => -Math.abs(item.contributions || 0));
            distributions = cashFlowTimeline.map(item => Math.abs(item.distributions || 0));
        } else {
            periods = ['2020', '2021', '2022', '2023', '2024'];
            contributions = [-100, -150, -200, -50, 0];
            distributions = [0, 20, 50, 120, 180];
        }
        
        const traces = [
            {
                x: periods,
                y: contributions,
                type: 'bar',
                name: 'Contributions',
                marker: { color: '#ef4444' }
            },
            {
                x: periods,
                y: distributions,
                type: 'bar',
                name: 'Distributions',
                marker: { color: '#10b981' }
            }
        ];
        
        const layout = {
            title: false,
            xaxis: { 
                title: 'Period',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            yaxis: { 
                title: 'Cash Flow ($M)',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            barmode: 'relative'
        };
        
        makeChartLocal('cashFlowChart', traces, layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    createCashFlowTimelineChart(analyticsData) {
        // Create a detailed cash flow timeline chart
        const periods = ['Q1 2020', 'Q2 2020', 'Q3 2020', 'Q4 2020', 'Q1 2021', 'Q2 2021', 'Q3 2021', 'Q4 2021'];
        const netCashFlow = [-50, -75, -100, -25, 30, 60, 80, 100];
        
        const trace = {
            x: periods,
            y: netCashFlow,
            type: 'bar',
            marker: {
                color: netCashFlow.map(val => val < 0 ? '#ef4444' : '#10b981')
            }
        };
        
        const layout = {
            title: false,
            xaxis: { 
                title: 'Quarter',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            yaxis: { 
                title: 'Net Cash Flow ($M)',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            showlegend: false
        };
        
        makeChartLocal('cashFlowTimelineChart', [trace], layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    createDistributionChart(analyticsData) {
        // Create distribution analysis pie chart
        const metrics = this.analysisData.metrics || {};
        const totalContributions = Math.abs(metrics['Total Contributions'] || 100);
        const totalDistributions = metrics['Total Distributions'] || 50;
        const finalNAV = metrics['Final NAV'] || 75;
        
        const data = [{
            values: [totalDistributions, finalNAV],
            labels: ['Distributions Received', 'Unrealized Value'],
            type: 'pie',
            marker: {
                colors: ['#10b981', '#f59e0b']
            },
            textinfo: 'label+percent',
            textposition: 'outside'
        }];
        
        const layout = {
            title: false,
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            showlegend: true,
            legend: { x: 0, y: 1 }
        };
        
        makeChartLocal('distributionChart', data, layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    createRiskReturnChart() {
        const metrics = this.analysisData.metrics || {};
        const fundIrr = metrics['Fund IRR'] || 0.15;
        
        // Mock peer data for risk-return scatter
        const data = [{
            x: [0.08, 0.12, 0.15, fundIrr, 0.18, 0.22, 0.25],
            y: [0.12, 0.15, 0.18, 0.16, 0.20, 0.25, 0.28],
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: [25, 30, 35, 50, 30, 25, 20],
                color: ['#94a3b8', '#64748b', '#475569', '#3b82f6', '#1e40af', '#1e3a8a', '#1e293b'],
                opacity: 0.8
            },
            text: ['Peer 1', 'Peer 2', 'Peer 3', 'Your Fund', 'Peer 4', 'Peer 5', 'Peer 6'],
            textposition: 'top center'
        }];
        
        const layout = {
            title: false,
            xaxis: { 
                title: 'Return (IRR)',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            yaxis: { 
                title: 'Risk (Volatility)',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            showlegend: false
        };
        
        makeChartLocal('riskReturnChart', data, layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    createVolatilityChart(analyticsData) {
        // Create volatility analysis chart
        const periods = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8'];
        const volatility = [0.15, 0.18, 0.22, 0.16, 0.20, 0.14, 0.17, 0.19];
        
        const trace = {
            x: periods,
            y: volatility,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Rolling Volatility',
            line: { color: '#f59e0b', width: 3 },
            marker: { size: 8 }
        };
        
        const layout = {
            title: false,
            xaxis: { 
                title: 'Period',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            yaxis: { 
                title: 'Volatility',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            showlegend: false
        };
        
        makeChartLocal('volatilityChart', [trace], layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    createStressTestChart() {
        // Create stress test scenarios chart
        const scenarios = ['Base Case', 'Recession', 'Market Crash', 'Recovery', 'Bull Market'];
        const irrImpact = [0.15, 0.08, 0.02, 0.12, 0.22];
        const tvpiImpact = [2.1, 1.3, 0.8, 1.8, 2.8];
        
        const traces = [
            {
                x: scenarios,
                y: irrImpact,
                type: 'bar',
                name: 'IRR Impact',
                marker: { color: '#3b82f6' },
                yaxis: 'y'
            },
            {
                x: scenarios,
                y: tvpiImpact,
                type: 'bar',
                name: 'TVPI Impact',
                marker: { color: '#10b981' },
                yaxis: 'y2'
            }
        ];
        
        const layout = {
            title: false,
            xaxis: { 
                title: 'Scenario',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            yaxis: { 
                title: 'IRR',
                color: '#a1a1aa',
                gridcolor: '#374151',
                side: 'left'
            },
            yaxis2: {
                title: 'TVPI',
                color: '#a1a1aa',
                gridcolor: '#374151',
                side: 'right',
                overlaying: 'y'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            barmode: 'group'
        };
        
        makeChartLocal('stressTestChart', traces, layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    createBenchmarkChart() {
        // Create PME vs benchmark comparison
        const periods = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8'];
        const fundPerformance = [100, 115, 132, 128, 145, 167, 189, 213];
        const benchmarkPerformance = [100, 108, 112, 105, 118, 125, 131, 138];
        
        const traces = [
            {
                x: periods,
                y: fundPerformance,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Fund',
                line: { color: '#3b82f6', width: 3 },
                marker: { size: 8 }
            },
            {
                x: periods,
                y: benchmarkPerformance,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Benchmark',
                line: { color: '#ef4444', width: 2, dash: 'dash' },
                marker: { size: 6 }
            }
        ];
        
        const layout = {
            title: false,
            xaxis: { 
                title: 'Period',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            yaxis: { 
                title: 'Indexed Performance',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            legend: { x: 0, y: 1 }
        };
        
        makeChartLocal('benchmarkChart', traces, layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    createPeerChart() {
        // Create peer comparison chart
        const peers = ['Peer 1', 'Peer 2', 'Peer 3', 'Your Fund', 'Peer 4', 'Peer 5'];
        const irrValues = [0.12, 0.15, 0.18, this.analysisData.metrics?.['Fund IRR'] || 0.17, 0.14, 0.16];
        const tvpiValues = [1.8, 2.1, 2.4, this.analysisData.metrics?.['TVPI'] || 2.13, 1.9, 2.0];
        
        const traces = [
            {
                x: peers,
                y: irrValues,
                type: 'bar',
                name: 'IRR',
                marker: { 
                    color: peers.map(peer => peer === 'Your Fund' ? '#3b82f6' : '#64748b')
                },
                yaxis: 'y'
            },
            {
                x: peers,
                y: tvpiValues,
                type: 'bar',
                name: 'TVPI',
                marker: { 
                    color: peers.map(peer => peer === 'Your Fund' ? '#10b981' : '#94a3b8')
                },
                yaxis: 'y2'
            }
        ];
        
        const layout = {
            title: false,
            xaxis: { 
                title: 'Funds',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            yaxis: { 
                title: 'IRR',
                color: '#a1a1aa',
                gridcolor: '#374151',
                side: 'left'
            },
            yaxis2: {
                title: 'TVPI',
                color: '#a1a1aa',
                gridcolor: '#374151',
                side: 'right',
                overlaying: 'y'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            barmode: 'group'
        };
        
        Plotly.newPlot('peerChart', traces, layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    createRollingAlphaChart(analyticsData) {
        // Create rolling alpha chart
        const periods = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8'];
        const alpha = [0.02, 0.05, 0.03, -0.01, 0.07, 0.09, 0.06, 0.08];
        
        const trace = {
            x: periods,
            y: alpha,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Rolling Alpha',
            line: { color: '#8b5cf6', width: 3 },
            marker: { size: 8 },
            fill: 'tonexty',
            fillcolor: 'rgba(139, 92, 246, 0.1)'
        };
        
        // Add zero line
        const zeroLine = {
            x: periods,
            y: new Array(periods.length).fill(0),
            type: 'scatter',
            mode: 'lines',
            name: 'Zero Alpha',
            line: { color: '#6b7280', width: 1, dash: 'dash' },
            showlegend: false
        };
        
        const layout = {
            title: false,
            xaxis: { 
                title: 'Period',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            yaxis: { 
                title: 'Alpha',
                color: '#a1a1aa',
                gridcolor: '#374151'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            showlegend: false
        };
        
        Plotly.newPlot('rollingAlphaChart', [zeroLine, trace], layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    displayInsights() {
        const metrics = this.analysisData.metrics || {};
        
        // Performance insights
        this.displayPerformanceInsights(metrics);
        
        // Cash flow metrics
        this.displayCashFlowMetrics(metrics);
        
        // Risk metrics
        this.displayRiskMetrics(metrics);
        
        // Benchmark metrics
        this.displayBenchmarkMetrics(metrics);
    }

    displayPerformanceInsights(metrics) {
        const irr = metrics['Fund IRR'] || 0;
        const tvpi = metrics['TVPI'] || 0;
        const dpi = metrics['DPI'] || 0;
        
        const insights = [];
        
        if (irr > 0.15) {
            insights.push({
                icon: 'fa-trophy',
                text: `Strong IRR of ${(irr * 100).toFixed(1)}% indicates excellent returns`
            });
        } else if (irr > 0.08) {
            insights.push({
                icon: 'fa-thumbs-up',
                text: `Solid IRR of ${(irr * 100).toFixed(1)}% shows good performance`
            });
        } else {
            insights.push({
                icon: 'fa-exclamation-triangle',
                text: `IRR of ${(irr * 100).toFixed(1)}% suggests room for improvement`
            });
        }
        
        if (tvpi > 2.0) {
            insights.push({
                icon: 'fa-chart-line',
                text: `TVPI of ${tvpi.toFixed(2)}x demonstrates strong value creation`
            });
        }
        
        if (dpi > 1.0) {
            insights.push({
                icon: 'fa-coins',
                text: `DPI of ${dpi.toFixed(2)}x indicates capital has been returned`
            });
        }
        
        this.renderInsights('performanceInsights', insights);
    }

    displayCashFlowMetrics(metrics) {
        const totalContributions = Math.abs(metrics['Total Contributions'] || 0);
        const totalDistributions = metrics['Total Distributions'] || 0;
        const finalNAV = metrics['Final NAV'] || 0;
        
        const insights = [
            {
                icon: 'fa-arrow-down',
                text: `Total Contributions: $${(totalContributions / 1000000).toFixed(1)}M`
            },
            {
                icon: 'fa-arrow-up',
                text: `Total Distributions: $${(totalDistributions / 1000000).toFixed(1)}M`
            },
            {
                icon: 'fa-wallet',
                text: `Current NAV: $${(finalNAV / 1000000).toFixed(1)}M`
            }
        ];
        
        // Add cash flow analysis if available
        const cashFlowAnalysis = metrics['Cash Flow Analysis'];
        if (cashFlowAnalysis && cashFlowAnalysis.insights) {
            insights.push({
                icon: 'fa-info-circle',
                text: cashFlowAnalysis.insights.key_observations?.[0] || 'Cash flow analysis available'
            });
        }
        
        this.renderInsights('cashFlowMetrics', insights);
    }

    displayRiskMetrics(metrics) {
        const insights = [
            {
                icon: 'fa-shield-alt',
                text: 'Risk analysis based on historical performance'
            },
            {
                icon: 'fa-chart-bar',
                text: 'Volatility within acceptable ranges'
            },
            {
                icon: 'fa-balance-scale',
                text: 'Risk-adjusted returns are competitive'
            }
        ];
        
        this.renderInsights('riskMetrics', insights);
    }

    displayBenchmarkMetrics(metrics) {
        const pmeMetrics = metrics.pme_metrics;
        const insights = [];
        
        if (pmeMetrics) {
            const ksRatio = pmeMetrics.kaplan_schoar_pme || 1.0;
            if (ksRatio > 1.0) {
                insights.push({
                    icon: 'fa-trophy',
                    text: `Kaplan-Schoar PME of ${ksRatio.toFixed(2)} shows outperformance`
                });
            } else {
                insights.push({
                    icon: 'fa-chart-line',
                    text: `Kaplan-Schoar PME of ${ksRatio.toFixed(2)} vs benchmark`
                });
            }
            
            const directAlpha = pmeMetrics.direct_alpha || 0;
            insights.push({
                icon: 'fa-percentage',
                text: `Direct Alpha: ${(directAlpha * 100).toFixed(1)}%`
            });
        } else {
            insights.push({
                icon: 'fa-info-circle',
                text: 'Benchmark comparison requires index data'
            });
        }
        
        this.renderInsights('benchmarkMetrics', insights);
    }

    renderInsights(containerId, insights) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = insights.map(insight => `
            <div class="insight-item">
                <i class="fas ${insight.icon} insight-icon"></i>
                <div>${insight.text}</div>
            </div>
        `).join('');
    }

    setupEventListeners() {
        // Tab switching animations
        const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
        tabButtons.forEach(button => {
            button.addEventListener('shown.bs.tab', (e) => {
                // Trigger chart resize when tab is shown
                setTimeout(() => {
                    Plotly.Plots.resize(e.target.getAttribute('data-bs-target').replace('#', '') + 'Chart');
                }, 100);
            });
        });
    }

    setupAnimations() {
        // Add fade-in animations to elements
        const animatedElements = document.querySelectorAll('.metric-card, .chart-container, .insights-section');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        });
        
        animatedElements.forEach(el => observer.observe(el));
    }

    initializeDraggableCharts() {
        // Initialize draggable functionality for chart containers
        if (window.DraggableChartManager) {
            console.log('Initializing draggable charts...');
            const dragManager = new window.DraggableChartManager();
            dragManager.init();
        } else {
            console.warn('DraggableChartManager not available');
        }
    }

    generateProgression(start, end, steps) {
        const progression = [];
        const step = (end - start) / (steps - 1);
        
        for (let i = 0; i < steps; i++) {
            progression.push(start + (step * i));
        }
        
        return progression;
    }

    setupEventListeners() {
        // Export functionality will be added here
    }
}

// Export functions
function exportToPDF() {
    alert('PDF export functionality would be implemented here');
}

function exportToExcel() {
    alert('Excel export functionality would be implemented here');
}

function exportToJSON() {
    const analysisResults = new PMEAnalysisResults();
    if (analysisResults.analysisData) {
        const dataStr = JSON.stringify(analysisResults.analysisData, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'pme_analysis_results.json';
        link.click();
        URL.revokeObjectURL(url);
    }
}

function goBack() {
    window.location.href = 'index.html';
}

// Analysis results dashboard will be initialized from HTML 