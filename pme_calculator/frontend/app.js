// PME Calculator Pro - Enhanced Application
class PMECalculatorPro {
    constructor() {
        this.fundFileId = null;
        this.benchmarkFileId = null;
        this.analysisResults = null;
        this.charts = {};
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeAnimations();
        
        // Check server health after a short delay to allow server startup
        setTimeout(() => {
            this.checkServerHealth();
        }, 1000);

        // Initialize charts if chart section exists
        this.initializeChartsOnLoad();
    }

    async initializeChartsOnLoad() {
        // Check if we're on a page with charts
        const chartsSection = document.getElementById('chartsSection');
        if (chartsSection) {
            // Load charts immediately to show sample data
            await this.loadAllCharts();
        }
    }

    initializeAnimations() {
        // Add fade-in animations to elements as they come into view
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                }
            });
        }, observerOptions);

        // Observe all cards and sections
        document.querySelectorAll('.card, .feature-card, .metric-card').forEach(el => {
            observer.observe(el);
        });
    }

    setupEventListeners() {
        // File upload zones
        this.setupUploadZone('fundUploadZone', 'fundFileInput', 'fund');
        this.setupUploadZone('benchmarkUploadZone', 'benchmarkFileInput', 'benchmark');

        // Analysis button
        document.getElementById('runAnalysisBtn').addEventListener('click', () => {
            this.runAnalysis();
        });

        // Export and new analysis buttons
        document.getElementById('exportResultsBtn')?.addEventListener('click', () => {
            this.exportResults();
        });

        document.getElementById('newAnalysisBtn')?.addEventListener('click', () => {
            this.resetAnalysis();
        });
    }

    setupUploadZone(zoneId, inputId, type) {
        const zone = document.getElementById(zoneId);
        const input = document.getElementById(inputId);

        // Click to upload
        zone.addEventListener('click', () => input.click());

        // File input change
        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0], type);
            }
        });

        // Drag and drop
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('dragover');
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('dragover');
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('dragover');
            
            if (e.dataTransfer.files.length > 0) {
                this.handleFileUpload(e.dataTransfer.files[0], type);
            }
        });
    }

    async checkServerHealth() {
        try {
            const API_BASE = window.API_BASE || `${location.protocol}//${location.hostname}:8000`;
            const response = await fetch(`${API_BASE}/api/health`, {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const health = await response.json();
                this.showStatus('Server connected successfully', 'success');
                console.log('✅ Backend health check passed:', health);
            } else {
                this.showStatus('Server connection issues', 'warning');
                console.warn('⚠️ Backend health check failed:', response.status);
            }
        } catch (error) {
            console.error('❌ Backend connection error:', error);
            this.showStatus('Unable to connect to server - make sure backend is running', 'error');
        }
    }

    async handleFileUpload(file, type) {
        const statusId = `${type}UploadStatus`;
        const statusElement = document.getElementById(statusId);
        
        // Show upload progress
        statusElement.innerHTML = `
            <div class="alert alert-info">
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                    <span>Uploading ${file.name}...</span>
                </div>
            </div>
        `;

        try {
            const formData = new FormData();
            formData.append('file', file);

            const API_BASE = window.API_BASE || `${location.protocol}//${location.hostname}:8000`;
            const endpoint = type === 'fund' ? `${API_BASE}/api/upload/fund` : `${API_BASE}/api/upload/index`;
            const response = await fetch(endpoint, {
                method: 'POST',
                mode: 'cors',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                if (type === 'fund') {
                    this.fundFileId = result.file_id;
                } else {
                    this.benchmarkFileId = result.file_id;
                }

                statusElement.innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle me-2"></i>
                        <strong>Success!</strong> ${file.name} uploaded successfully
                        <div class="mt-2">
                            <small class="text-muted">
                                Rows: ${result.rows_processed || 'N/A'} | 
                                Columns: ${result.columns_detected || 'N/A'}
                            </small>
                        </div>
                    </div>
                `;

                this.updateAnalysisButton();
                this.addUploadAnimation(statusElement);
            } else {
                throw new Error(result.detail || 'Upload failed');
            }
        } catch (error) {
            statusElement.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Error:</strong> ${error.message}
                </div>
            `;
        }
    }

    addUploadAnimation(element) {
        element.classList.add('animate__animated', 'animate__bounceIn');
        setTimeout(() => {
            element.classList.remove('animate__animated', 'animate__bounceIn');
        }, 1000);
    }

    updateAnalysisButton() {
        const button = document.getElementById('runAnalysisBtn');
        if (this.fundFileId) {
            button.classList.remove('disabled');
            button.innerHTML = '<i class="fas fa-play"></i> Run Comprehensive Analysis';
        }
    }

    async runAnalysis() {
        console.log('🔬 Starting runAnalysis()');
        console.log('📊 Fund File ID:', this.fundFileId);
        console.log('📈 Benchmark File ID:', this.benchmarkFileId);
        
        if (!this.fundFileId) {
            console.error('❌ No fund file ID available');
            this.showStatus('Please upload fund data first', 'error');
            return;
        }

        this.showLoadingOverlay(true);

        try {
            // Build query parameters
            const params = new URLSearchParams({
                fund_file_id: this.fundFileId
            });

            if (this.benchmarkFileId) {
                params.append('index_file_id', this.benchmarkFileId);
            }

            // Use environment-aware API base URL
            const API_BASE = window.API_BASE || `${location.protocol}//${location.hostname}:8000`;
            const fullUrl = `${API_BASE}/api/analysis/run-sync?${params}`;
            
            console.log('🌐 API Base URL:', API_BASE);
            console.log('🔗 Full Request URL:', fullUrl);
            console.log('📋 Request Parameters:', params.toString());
            
            const requestOptions = {
                method: 'POST',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                }
            };
            
            console.log('⚙️  Request Options:', requestOptions);
            console.log('📡 Making fetch request...');
            
            const response = await fetch(fullUrl, requestOptions);
            
            console.log('📨 Response received');
            console.log('📊 Response Status:', response.status);
            console.log('📋 Response Headers:', Object.fromEntries(response.headers.entries()));
            console.log('✅ Response OK:', response.ok);

            const result = await response.json();
            console.log('📄 Response Data:', result);

            if (response.ok) {
                console.log('✅ Analysis successful, processing results...');
                // Extract the inner result object for proper data structure
                const analysisData = result.result || result;
                console.log('📊 Analysis Data Structure:', Object.keys(analysisData));
                
                if (analysisData.metrics) {
                    console.log('📈 Available Metrics:', Object.keys(analysisData.metrics));
                    console.log('💰 Fund IRR:', analysisData.metrics['Fund IRR']);
                    console.log('📊 TVPI:', analysisData.metrics['TVPI']);
                }
                
                this.analysisResults = analysisData;
                this.displayResults(analysisData);
                this.showStatus('Analysis completed successfully!', 'success');
                
                // Add option to view detailed analysis
                this.showDetailedAnalysisOption(analysisData);
            } else {
                console.error('❌ Analysis failed with status:', response.status);
                console.error('📄 Error details:', result);
                throw new Error(result.detail || 'Analysis failed');
            }
        } catch (error) {
            console.error('💥 Analysis error caught:', error);
            console.error('🔍 Error type:', error.constructor.name);
            console.error('📝 Error message:', error.message);
            console.error('📚 Error stack:', error.stack);
            
            // More specific error messages
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                this.showStatus('Analysis failed: Network connection error. Please check if the server is running.', 'error');
            } else if (error.name === 'SyntaxError') {
                this.showStatus('Analysis failed: Invalid response from server. Please try again.', 'error');
            } else {
                this.showStatus(`Analysis failed: ${error.message}`, 'error');
            }
        } finally {
            this.showLoadingOverlay(false);
        }
    }

    displayResults(results) {
        // Show results section
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });

        // Display components
        this.displayMetrics(results);
        this.displaySummary(results);
        
        // Generate charts
        if (results && Object.keys(results).length > 0) {
            this.generateCharts(results);
        }
        
        // Update KPI cards periodically
        this.updateKPICards();
    }

    displayMetrics(results) {
        const metricsRow = document.getElementById('metricsRow');
        
        // Extract metrics from the nested structure returned by backend
        const metricsData = results.metrics || {};
        const metrics = [
            { label: 'IRR', value: metricsData['Fund IRR'], format: 'percentage', icon: 'fa-percentage' },
            { label: 'TVPI', value: metricsData['TVPI'], format: 'multiple', icon: 'fa-times' },
            { label: 'DPI', value: metricsData['DPI'], format: 'multiple', icon: 'fa-coins' },
            { label: 'RVPI', value: metricsData['RVPI'], format: 'multiple', icon: 'fa-chart-line' }
        ];

        metricsRow.innerHTML = metrics.map(metric => `
            <div class="col-md-3 mb-3">
                <div class="metric-card">
                    <div class="metric-value">
                        <i class="fas ${metric.icon} me-2"></i>
                        ${this.formatMetricValue(metric.value, metric.format)}
                    </div>
                    <div class="metric-label">${metric.label}</div>
                </div>
            </div>
        `).join('');

        // Add animation to metrics
        setTimeout(() => {
            document.querySelectorAll('.metric-card').forEach((card, index) => {
                setTimeout(() => {
                    card.classList.add('animate__animated', 'animate__zoomIn');
                }, index * 100);
            });
        }, 100);
    }

    displaySummary(results) {
        const summaryContent = document.getElementById('summaryContent');
        
        const insights = this.generateInsights(results);
        
        summaryContent.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="insights-highlight-section">
                        <h5 class="insights-section-title">
                            <i class="fas fa-chart-line me-2"></i>Performance Highlights
                        </h5>
                        <div class="insights-list">
                            ${insights.performance.map(insight => `
                                <div class="insight-highlight-item">
                                    <i class="fas fa-check-circle insight-highlight-icon success"></i>
                                    <span class="insight-highlight-text">${insight}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="insights-highlight-section">
                        <h5 class="insights-section-title">
                            <i class="fas fa-lightbulb me-2"></i>Key Observations
                        </h5>
                        <div class="insights-list">
                            ${insights.observations.map(insight => `
                                <div class="insight-highlight-item">
                                    <i class="fas fa-info-circle insight-highlight-icon info"></i>
                                    <span class="insight-highlight-text">${insight}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    generateInsights(results) {
        const insights = {
            performance: [],
            observations: []
        };

        // Extract metrics from the nested structure
        const metricsData = results.metrics || {};
        const irr = metricsData['Fund IRR'] || 0;
        const tvpi = metricsData['TVPI'] || 0;
        const dpi = metricsData['DPI'] || 0;
        const rvpi = metricsData['RVPI'] || 0;

        // Performance insights
        if (irr > 0.15) {
            insights.performance.push(`Strong IRR of ${(irr * 100).toFixed(1)}% indicates excellent returns`);
        } else if (irr > 0.08) {
            insights.performance.push(`Solid IRR of ${(irr * 100).toFixed(1)}% shows good performance`);
        } else {
            insights.performance.push(`IRR of ${(irr * 100).toFixed(1)}% suggests room for improvement`);
        }

        if (tvpi > 2.0) {
            insights.performance.push(`TVPI of ${tvpi.toFixed(2)}x demonstrates strong value creation`);
        } else if (tvpi > 1.5) {
            insights.performance.push(`TVPI of ${tvpi.toFixed(2)}x shows positive value generation`);
        }

        // Observations
        if (dpi > 1.0) {
            insights.observations.push(`DPI of ${dpi.toFixed(2)}x indicates capital has been returned`);
        } else {
            insights.observations.push(`DPI of ${dpi.toFixed(2)}x suggests fund is still in investment phase`);
        }

        if (rvpi > 1.0) {
            insights.observations.push(`RVPI of ${rvpi.toFixed(2)}x shows significant unrealized value`);
        }

        return insights;
    }

    async generateCharts(results) {
        const chartsSection = document.getElementById('chartsSection');
        
        // Clear existing charts and create professional chart containers
        chartsSection.innerHTML = `
            <!-- Professional Chart Grid -->
            <div class="row g-4">
                <div class="col-lg-6">
                    <div class="chart-container premium">
                        <h5 class="chart-title">
                            <i class="fas fa-chart-line"></i>
                            TWR vs Russell 3000®
                        </h5>
                        <div class="chart-subtitle">Time-weighted returns compared to benchmark</div>
                        <div class="card-body">
                            <div id="twrIndexPlot" style="height: 400px;"></div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="chart-container premium">
                        <h5 class="chart-title">
                            <i class="fas fa-chart-area"></i>
                            Performance Analysis
                        </h5>
                        <div class="chart-subtitle">Fund performance vs benchmark over time</div>
                        <div class="card-body">
                            <div id="performanceChart" style="height: 400px;"></div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="chart-container premium">
                        <h5 class="chart-title">
                            <i class="fas fa-chart-bar"></i>
                            Cash Flow Analysis
                        </h5>
                        <div class="chart-subtitle">Contributions and distributions timeline</div>
                        <div class="card-body">
                            <div id="cashFlowChart" style="height: 400px;"></div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="chart-container premium">
                        <h5 class="chart-title">
                            <i class="fas fa-chart-pie"></i>
                            Key Metrics
                        </h5>
                        <div class="chart-subtitle">Performance metrics overview</div>
                        <div class="card-body">
                            <div id="metricsChart" style="height: 400px;"></div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-12">
                    <div class="chart-container premium">
                        <h5 class="chart-title">
                            <i class="fas fa-chart-scatter"></i>
                            Risk vs Return Analysis
                        </h5>
                        <div class="chart-subtitle">Portfolio positioning relative to peers</div>
                        <div class="card-body">
                            <div id="riskReturnChart" style="height: 400px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Initialize charts with proper error handling and loading states
        // Add small delay to ensure DOM elements are fully rendered
        setTimeout(async () => {
            await this.loadAllCharts();
        }, 100);
    }

    async loadAllCharts() {
        /**
         * Load all charts with optimized sizing and layout
         */
        console.log('🔄 Loading all charts with optimized layout...');
        
        // Chart IDs with their optimal heights
        const chartConfigs = [
            { id: 'twrIndexPlot', url: '/v1/metrics/twr_vs_index', height: '350px' },
            { id: 'cashFlowChart', url: '/v1/metrics/cashflow_overview', height: '300px' },
            { id: 'metricsChart', url: '/v1/metrics/irr_pme', height: '350px' },
            { id: 'performanceChart', url: '/v1/metrics/pme_progression', height: '300px' },
            { id: 'riskReturnChart', url: '/v1/metrics/net_cf_market', height: '300px' }
        ];

        // Set loading states with optimized heights
        chartConfigs.forEach(config => {
            const element = document.getElementById(config.id);
            if (element) {
                // Set container height to prevent layout shifts
                element.style.height = config.height;
                element.innerHTML = `
                    <div class="d-flex justify-content-center align-items-center h-100">
                        <div class="text-center">
                            <div class="spinner-border text-primary" role="status" style="width: 2rem; height: 2rem;">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <div class="mt-2 text-muted small">Loading chart...</div>
                        </div>
                    </div>
                `;
            }
        });

        // Load charts in parallel with optimized sizing
        const chartPromises = chartConfigs.map(config => 
            this.makeChart(config.id, config.url, config.height).catch(error => {
                console.error(`Failed to load chart ${config.id}:`, error);
                return null;
            })
        );

        await Promise.all(chartPromises);

        // Initialize draggable functionality after charts are loaded
        if (window.DraggableChartManager) {
            const dragManager = new window.DraggableChartManager();
            dragManager.init();
        }
        
        console.log('✅ All charts loaded with optimized layout');
    }

    async makeChart(elementId, url, height = '400px') {
        /**
         * Generic chart maker with optimized sizing and responsive layout
         */
        console.log(`🔄 Making chart: ${elementId} from ${url}`);
        const element = document.getElementById(elementId);
        
        if (!element) {
            console.error(`❌ Element not found: ${elementId}`);
            return;
        }
        
        try {
            // Set container height to prevent layout shifts
            if (element) {
                element.style.height = height;
                element.innerHTML = `
                    <div class="d-flex justify-content-center align-items-center h-100">
                        <div class="text-center">
                            <div class="spinner-border text-primary" role="status" style="width: 2rem; height: 2rem;">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <div class="mt-2 text-muted small">Loading chart...</div>
                        </div>
                    </div>
                `;
            }
            
            // Use environment-aware API base URL
            const API_BASE = window.API_BASE || `${location.protocol}//${location.hostname}:8000`;
            const fullUrl = url.startsWith('http') ? url : `${API_BASE}${url}`;
            
            const response = await fetch(fullUrl, {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch chart data: ${response.status}`);
            }

            const chartData = await response.json();
            
            // **FIX: Always clear loading state before rendering**
            if (element) {
                element.innerHTML = '';
                
                // **FIX: Ensure element is visible and properly sized**
                element.style.display = 'block';
                element.style.width = '100%';
                element.style.height = height;
                element.style.minHeight = height;
                
                // Validate chart data
                if (!chartData.data || !Array.isArray(chartData.data) || chartData.data.length === 0) {
                    throw new Error('Invalid chart data received');
                }
                
                // **USE EXACT SAME CONFIG AS WORKING TEST**
                const optimizedLayout = {
                    ...chartData.layout,
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: {color: '#ffffff'}
                };
                
                // **FIX: Ensure Plotly is available**
                if (typeof Plotly !== 'undefined') {
                    console.log(`📊 Rendering chart ${elementId} with data:`, chartData.data.length, 'traces');
                    console.log(`📊 Chart data sample:`, JSON.stringify(chartData.data[0], null, 2));
                    console.log(`📊 Layout:`, JSON.stringify(optimizedLayout, null, 2));
                    
                    try {
                        await Plotly.newPlot(elementId, chartData.data, optimizedLayout, {
                            responsive: true,
                            displaylogo: false,
                            displayModeBar: false
                        });
                        
                        console.log(`✅ Chart ${elementId} rendered successfully`);
                        
                        // Verify the chart was actually created
                        const plotElement = document.getElementById(elementId);
                        if (plotElement && plotElement.children.length > 0) {
                            console.log(`✅ Chart ${elementId} DOM elements created:`, plotElement.children.length);
                        } else {
                            console.warn(`⚠️ Chart ${elementId} rendered but no DOM elements found`);
                        }
                        
                    } catch (plotlyError) {
                        console.error(`❌ Plotly rendering error for ${elementId}:`, plotlyError);
                        throw plotlyError;
                    }
                    
                } else {
                    console.error('❌ Plotly library not available');
                    throw new Error('Plotly library not available');
                }
            }
            
        } catch (error) {
            console.error(`❌ Error creating chart ${elementId}:`, error);
            if (element) {
                element.style.height = height;
                element.innerHTML = `
                    <div class="alert alert-warning text-center h-100 d-flex align-items-center justify-content-center" style="margin: 0;">
                        <div>
                            <i class="fas fa-exclamation-triangle"></i>
                            <div class="mt-2">Chart temporarily unavailable</div>
                            <small class="text-muted">${error.message || 'Please try refreshing the page'}</small>
                        </div>
                    </div>
                `;
            }
        }
    }

    createPerformanceChart(results) {
        // Extract real performance data from backend
        const analyticsData = results.metrics?.['Analytics Data'] || {};
        const performanceTimeline = analyticsData.performance_timeline || [];
        
        let fundData, benchmarkData;
        
        if (performanceTimeline.length > 0) {
            // Use real data from backend
            fundData = {
                x: performanceTimeline.map(item => item.date),
                y: performanceTimeline.map(item => item.tvpi),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Fund Performance (TVPI)',
                line: { color: '#2563eb', width: 3 },
                marker: { size: 8 }
            };
            
            // Mock benchmark data (would need real benchmark data from backend)
            benchmarkData = {
                x: performanceTimeline.map(item => item.date),
                y: performanceTimeline.map((item, index) => 1.0 + (index * 0.05)), // Mock 5% growth per period
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Benchmark',
                line: { color: '#dc2626', width: 2, dash: 'dash' },
                marker: { size: 6 }
            };
        } else {
            // Fallback to mock data
            const metricsData = results.metrics || {};
            const finalTvpi = metricsData['TVPI'] || 1.0;
            
            fundData = {
                x: ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8'],
                y: [1.0, 1.15, 1.32, 1.28, 1.45, 1.67, 1.89, finalTvpi],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Fund Performance',
                line: { color: '#2563eb', width: 3 },
                marker: { size: 8 }
            };

            benchmarkData = {
                x: ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8'],
                y: [1.0, 1.08, 1.12, 1.05, 1.18, 1.25, 1.31, 1.38],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Benchmark',
                line: { color: '#dc2626', width: 2, dash: 'dash' },
                marker: { size: 6 }
            };
        }

        const layout = {
            title: 'Fund Performance vs Benchmark',
            xaxis: { title: 'Time Period' },
            yaxis: { title: 'Multiple of Invested Capital' }
        };

        // Use professional chart creation
        if (window.createProfessionalChart) {
            window.createProfessionalChart('performanceChart', [fundData, benchmarkData], layout);
        } else {
            makeChartLocal('performanceChart', [fundData, benchmarkData], layout, {
                displayModeBar: false
            });
        }
    }

    createCashFlowChart(results) {
        // Extract real cash flow data from backend
        const analyticsData = results.metrics?.['Analytics Data'] || {};
        const cashFlowTimeline = analyticsData.cash_flow_timeline || [];
        
        let periods, contributions, distributions;
        
        if (cashFlowTimeline.length > 0) {
            // Use real data from backend
            periods = cashFlowTimeline.map(item => item.date);
            contributions = cashFlowTimeline.map(item => item.contributions < 0 ? item.contributions : -Math.abs(item.contributions));
            distributions = cashFlowTimeline.map(item => Math.abs(item.distributions));
        } else {
            // Fallback to mock data
            periods = ['2020', '2021', '2022', '2023', '2024'];
            contributions = [-100, -150, -200, -50, 0];
            distributions = [0, 20, 50, 120, 180];
        }

        const trace1 = {
            x: periods,
            y: contributions,
            type: 'bar',
            name: 'Contributions',
            marker: { color: '#dc2626' }
        };

        const trace2 = {
            x: periods,
            y: distributions,
            type: 'bar',
            name: 'Distributions',
            marker: { color: '#059669' }
        };

        const layout = {
            title: 'Cash Flow Analysis',
            xaxis: { title: 'Year' },
            yaxis: { title: 'Cash Flow ($M)' },
            barmode: 'relative'
        };

        // Use professional chart creation
        if (window.createProfessionalChart) {
            window.createProfessionalChart('cashFlowChart', [trace1, trace2], layout);
        } else {
            makeChartLocal('cashFlowChart', [trace1, trace2], layout, {
                displayModeBar: false
            });
        }
    }

    createMetricsChart(results) {
        // Extract metrics from the nested structure
        const metricsData = results.metrics || {};
        const irr = metricsData['Fund IRR'] || 0;
        const tvpi = metricsData['TVPI'] || 0;
        const dpi = metricsData['DPI'] || 0;
        const rvpi = metricsData['RVPI'] || 0;
        
        // Format values for display
        const formattedValues = [
            irr * 100,  // IRR as percentage
            tvpi,       // TVPI as multiple
            dpi,        // DPI as multiple
            rvpi        // RVPI as multiple
        ];
        
        const data = [{
            type: 'bar',
            x: ['IRR', 'TVPI', 'DPI', 'RVPI'],
            y: formattedValues,
            text: [
                `${(irr * 100).toFixed(1)}%`,
                `${tvpi.toFixed(2)}x`,
                `${dpi.toFixed(2)}x`,
                `${rvpi.toFixed(2)}x`
            ],
            textposition: 'outside',
            textfont: {
                size: 18,
                color: '#ffffff',
                family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
                weight: 700
            },
            marker: {
                color: [
                    irr >= 0.15 ? '#00ff88' : irr >= 0.08 ? '#0066cc' : '#ff6b6b',  // IRR: Green if excellent, blue if good, red if poor
                    tvpi >= 2.0 ? '#00ff88' : tvpi >= 1.5 ? '#0066cc' : '#ff6b6b',   // TVPI: Green if >2x, blue if >1.5x, red if <1.5x
                    dpi >= 1.0 ? '#00ff88' : dpi >= 0.5 ? '#0066cc' : '#ff6b6b',     // DPI: Green if >1x, blue if >0.5x, red if <0.5x
                    rvpi >= 1.0 ? '#00ff88' : rvpi >= 0.5 ? '#0066cc' : '#ff6b6b'    // RVPI: Green if >1x, blue if >0.5x, red if <0.5x
                ],
                line: {
                    color: 'rgba(255, 255, 255, 0.3)',
                    width: 3
                },
                opacity: 0.95
            },
            hovertemplate: 
                '<b>%{x}</b><br>' +
                'Value: %{text}<br>' +
                '<extra></extra>',
            hoverlabel: {
                bgcolor: 'rgba(0, 0, 0, 0.9)',
                bordercolor: '#0066cc',
                font: {
                    color: '#ffffff',
                    size: 16,
                    family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
                    weight: 600
                }
            }
        }];

        const layout = {
            title: {
                text: '<b style="color: #ffffff;">Key Performance Metrics</b>',
                font: {
                    size: 24,
                    color: '#ffffff',
                    family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
                    weight: 700
                },
                x: 0.5,
                xanchor: 'center',
                y: 0.95,
                yanchor: 'top'
            },
            xaxis: { 
                title: {
                    text: '<b style="color: #cccccc;">Metrics</b>',
                    font: {
                        size: 16,
                        color: '#cccccc',
                        family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
                        weight: 600
                    }
                },
                tickfont: {
                    size: 15,
                    color: '#ffffff',
                    family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
                    weight: 600
                },
                gridcolor: 'rgba(255, 255, 255, 0.15)',
                linecolor: 'rgba(255, 255, 255, 0.3)',
                tickcolor: 'rgba(255, 255, 255, 0.3)',
                showgrid: true,
                gridwidth: 1
            },
            yaxis: { 
                title: {
                    text: '<b style="color: #cccccc;">Value</b>',
                    font: {
                        size: 16,
                        color: '#cccccc',
                        family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
                        weight: 600
                    }
                },
                tickfont: {
                    size: 14,
                    color: '#ffffff',
                    family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
                    weight: 500
                },
                gridcolor: 'rgba(255, 255, 255, 0.15)',
                linecolor: 'rgba(255, 255, 255, 0.3)',
                tickcolor: 'rgba(255, 255, 255, 0.3)',
                zeroline: true,
                zerolinecolor: 'rgba(255, 255, 255, 0.4)',
                zerolinewidth: 2,
                showgrid: true,
                gridwidth: 1
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { 
                color: '#ffffff',
                family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            },
            margin: {
                l: 80,
                r: 50,
                t: 80,
                b: 100
            },
            showlegend: false,
            annotations: [
                {
                    text: '<b style="color: #888888;">IRR: Internal Rate of Return | TVPI: Total Value to Paid-In | DPI: Distributions to Paid-In | RVPI: Residual Value to Paid-In</b>',
                    showarrow: false,
                    x: 0.5,
                    y: -0.18,
                    xref: 'paper',
                    yref: 'paper',
                    xanchor: 'center',
                    yanchor: 'top',
                    font: {
                        size: 12,
                        color: '#888888',
                        family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
                        weight: 500
                    }
                }
            ]
        };

        // Simplify layout for professional styling
        const simplifiedLayout = {
            title: 'Key Performance Metrics',
            xaxis: { title: 'Metrics' },
            yaxis: { title: 'Value' }
        };

        // Use professional chart creation
        if (window.createProfessionalChart) {
            window.createProfessionalChart('metricsChart', data, simplifiedLayout);
        } else {
            const config = {
                responsive: true,
                displayModeBar: false,
                staticPlot: false
            };
            makeChartLocal('metricsChart', data, layout, config);
        }
    }

    createRiskReturnChart(results) {
        // Extract real IRR from backend data
        const metricsData = results.metrics || {};
        const fundIrr = metricsData['Fund IRR'] || 0;
        
        // Mock risk-return data with real fund IRR
        const data = [{
            x: [0.12, 0.15, 0.18, fundIrr, 0.22],
            y: [0.08, 0.12, 0.15, 0.14, 0.18],
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: [20, 25, 30, 40, 35],
                color: ['#94a3b8', '#64748b', '#475569', '#2563eb', '#1e40af'],
                opacity: 0.8
            },
            text: ['Peer 1', 'Peer 2', 'Peer 3', 'Your Fund', 'Peer 4'],
            textposition: 'top center'
        }];

        const layout = {
            title: 'Risk vs Return Analysis',
            xaxis: { title: 'Return (IRR)' },
            yaxis: { title: 'Risk (Volatility)' }
        };

        // Use professional chart creation
        if (window.createProfessionalChart) {
            window.createProfessionalChart('riskReturnChart', data, layout);
        } else {
            makeChartLocal('riskReturnChart', data, layout, {
                displayModeBar: false
            });
        }
    }

    formatMetricValue(value, format) {
        if (value === null || value === undefined) return 'N/A';
        
        switch (format) {
            case 'percentage':
                return `${(value * 100).toFixed(1)}%`;
            case 'multiple':
                return `${value.toFixed(2)}x`;
            case 'currency':
                return `$${(value / 1000000).toFixed(1)}M`;
            default:
                return value.toFixed(2);
        }
    }

    showLoadingOverlay(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    showStatus(message, type) {
        // Create a toast notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type} position-fixed`;
        toast.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 10000;
            min-width: 300px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        `;
        
        const icon = type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-triangle' : 'info-circle';
        
        toast.innerHTML = `
            <i class="fas fa-${icon} me-2"></i>
            ${message}
        `;
        
        document.body.appendChild(toast);
        
        // Animate in
        toast.classList.add('animate__animated', 'animate__slideInRight');
        
        // Remove after 5 seconds
        setTimeout(() => {
            toast.classList.add('animate__slideOutRight');
            setTimeout(() => toast.remove(), 500);
        }, 5000);
    }

    exportResults() {
        if (!this.analysisResults) {
            this.showStatus('No results to export', 'warning');
            return;
        }

        // Create export data
        const exportData = {
            analysis_name: document.getElementById('analysisName').value,
            timestamp: new Date().toISOString(),
            fund_name: document.getElementById('fundName').value,
            benchmark_name: document.getElementById('benchmarkName').value,
            results: this.analysisResults
        };

        // Download as JSON
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pme_analysis_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showStatus('Results exported successfully', 'success');
    }

    showDetailedAnalysisOption(results) {
        // Store results for the detailed analysis page
        localStorage.setItem('pmeAnalysisResults', JSON.stringify(results));
        
        // Add a prominent button to view detailed analysis
        const resultsSection = document.getElementById('resultsSection');
        
        // Check if button already exists
        if (!document.getElementById('detailedAnalysisBtn')) {
            const detailedAnalysisButton = document.createElement('div');
            detailedAnalysisButton.className = 'text-center mt-4';
            detailedAnalysisButton.innerHTML = `
                <button id="detailedAnalysisBtn" class="btn btn-primary btn-lg" onclick="window.location.href='analysis.html'">
                    <i class="fas fa-chart-line me-2"></i>
                    View Comprehensive Analysis Report
                </button>
                <p class="text-muted mt-2">
                    <small>Detailed charts, insights, and advanced analytics</small>
                </p>
            `;
            
            resultsSection.appendChild(detailedAnalysisButton);
            
            // Add animation
            setTimeout(() => {
                detailedAnalysisButton.classList.add('animate__animated', 'animate__fadeInUp');
            }, 500);
        }
    }

    resetAnalysis() {
        // Reset file IDs
        this.fundFileId = null;
        this.benchmarkFileId = null;
        this.analysisResults = null;

        // Clear status messages
        document.getElementById('fundUploadStatus').innerHTML = '';
        document.getElementById('benchmarkUploadStatus').innerHTML = '';

        // Reset form inputs
        document.getElementById('fundFileInput').value = '';
        document.getElementById('benchmarkFileInput').value = '';

        // Hide results
        document.getElementById('resultsSection').style.display = 'none';

        // Reset button
        const button = document.getElementById('runAnalysisBtn');
        button.classList.add('disabled');
        button.innerHTML = '<i class="fas fa-play"></i> Run Comprehensive Analysis';

        // Clear stored results
        localStorage.removeItem('pmeAnalysisResults');

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });

        this.showStatus('Analysis reset successfully', 'info');
    }

    async updateKPICards() {
        /**
         * Update the KPI cards with real-time data
         */
        try {
            const API_BASE = window.API_BASE || `${location.protocol}//${location.hostname}:8000`;
            const response = await fetch(`${API_BASE}/api/metrics/summary`, {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success && data.metrics) {
                    this.displayMetrics({ metrics: data.metrics });
                }
            }
        } catch (error) {
            console.error('Failed to update KPI cards:', error);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing PME Calculator Pro...');
    try {
        window.app = new PMECalculatorPro();
        console.log('✅ PME Calculator Pro initialized successfully:', window.app);
        console.log('📊 App methods available:', Object.getOwnPropertyNames(Object.getPrototypeOf(window.app)));
    } catch (error) {
        console.error('❌ Failed to initialize PME Calculator Pro:', error);
        console.error('📚 Error stack:', error.stack);
        
        // Show user-friendly error message
        document.body.innerHTML = `
            <div class="container mt-5">
                <div class="alert alert-danger">
                    <h4><i class="fas fa-exclamation-triangle"></i> Application Error</h4>
                    <p>Failed to initialize the PME Calculator. Please refresh the page and try again.</p>
                    <details>
                        <summary>Technical Details</summary>
                        <pre>${error.message}\n\n${error.stack}</pre>
                    </details>
                </div>
            </div>
        `;
    }
});

// Global error handler for unhandled JavaScript errors
window.addEventListener('error', (event) => {
    console.error('💥 Global JavaScript Error:', event.error);
    console.error('📄 Error details:', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
    });
});

// Global handler for unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('💥 Unhandled Promise Rejection:', event.reason);
    console.error('📄 Promise details:', event);
}); 