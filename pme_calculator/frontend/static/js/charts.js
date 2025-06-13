// Import dark theme template
import { PLOTLY_TEMPLATE } from './theme.js';

// Plotly Helper Wrapper
window.makeChart = async function(elId, fetchURL, plotOptions) {
    try {
        // Use environment-aware API base URL
        const API_BASE = window.API_BASE || `${location.protocol}//${location.hostname}:8000`;
        const fullUrl = fetchURL.startsWith('http') ? fetchURL : `${API_BASE}${fetchURL}`;
        
        console.log(`Loading chart ${elId} from ${fullUrl}`);
        
        const res = await fetch(fullUrl, {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!res.ok) {
            throw new Error(`Failed to fetch chart data: ${res.status}`);
        }
        
        const {data, layout} = await res.json();
        
        // Apply consistent professional theme
        layout.template = getProfessionalChartTemplate();
        layout.margin = {l:60,r:20,t:40,b:40};
        layout.paper_bgcolor = 'rgba(0,0,0,0)';  // Clear background
        layout.plot_bgcolor = 'rgba(0,0,0,0)';   // Clear plot area
        
        const cfg = {
            responsive: true, 
            displaylogo: false, 
            modeBarButtonsToAdd: ['downloadCsv','hoverClosest'],
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d', 'autoScale2d']
        };
        
        // Enhanced hover tooltips
        data.forEach(trace => {
            if (trace.y && Array.isArray(trace.y)) {
                trace.customdata = trace.y;
                trace.hovertemplate = '%{y:$,.1f}<br>(Δ %{customdata:.2%})<extra></extra>';
            }
        });
        
        Plotly.newPlot(elId, data, layout, { ...cfg, template: PLOTLY_TEMPLATE });
        
        // Add ResizeObserver for responsive chart resizing
        const gd = document.getElementById(elId);
        if (gd && gd.parentElement) {
            new ResizeObserver(() => {
                if (window.Plotly && window.Plotly.Plots) {
                    window.Plotly.Plots.resize(gd);
                }
            }).observe(gd.parentElement);
        }
        
        console.log(`Chart ${elId} loaded successfully`);
        
    } catch (error) {
        console.error(`Error loading chart ${elId}:`, error);
        const element = document.getElementById(elId);
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

// Alternative function for local data (current app.js usage)
window.makeChartLocal = function(elId, data, layout, config = {}) {
    // Apply professional theme template to layout
    const professionalTemplate = getProfessionalChartTemplate();
    Object.assign(layout, professionalTemplate.layout);
    
    // Ensure clear backgrounds
    layout.paper_bgcolor = 'rgba(0,0,0,0)';
    layout.plot_bgcolor = 'rgba(0,0,0,0)';
    layout.margin = layout.margin || {l:60,r:20,t:40,b:40};
    
    // Apply professional styling to traces
    if (data && Array.isArray(data)) {
        data.forEach(trace => {
            applyProfessionalTraceStyle(trace);
        });
    }
    
    // Default config with professional settings
    const cfg = Object.assign({
        responsive: true, 
        displaylogo: false, 
        modeBarButtonsToAdd: ['downloadCsv','hoverClosest'],
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d', 'autoScale2d'],
        displayModeBar: true,
        toImageButtonOptions: {
            format: 'png',
            filename: elId + '_chart',
            height: 600,
            width: 1000,
            scale: 2
        }
    }, config);
    
    // Enhanced hover tooltips
    data.forEach(trace => {
        if (trace.y && Array.isArray(trace.y)) {
            trace.customdata = trace.y;
            trace.hovertemplate = '%{y:$,.1f}<br>(Δ %{customdata:.2%})<extra></extra>';
        }
    });
    
    Plotly.newPlot(elId, data, layout, { ...cfg, template: PLOTLY_TEMPLATE });
    
    // Add ResizeObserver for responsive chart resizing
    const gd = document.getElementById(elId);
    if (gd && gd.parentElement) {
        new ResizeObserver(() => {
            if (window.Plotly && window.Plotly.Plots) {
                window.Plotly.Plots.resize(gd);
            }
        }).observe(gd.parentElement);
    }
}

// Professional Chart Template - matches Cash Flow Pacing Analysis style
function getProfessionalChartTemplate() {
    return {
        layout: {
            font: {
                family: '"Inter", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                size: 12,
                color: '#e0e6ed'
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            colorway: [
                '#0066cc',  // Primary blue
                '#00ff88',  // Success green
                '#ff6b6b',  // Error red
                '#4ecdc4',  // Teal
                '#45b7d1',  // Light blue
                '#96ceb4',  // Mint
                '#feca57',  // Yellow
                '#ff9ff3',  // Pink
                '#54a0ff',  // Blue
                '#5f27cd'   // Purple
            ],
            xaxis: {
                gridcolor: 'rgba(255,255,255,0.1)',
                linecolor: 'rgba(255,255,255,0.2)',
                tickcolor: 'rgba(255,255,255,0.2)',
                tickfont: { color: '#b0b7c3', size: 11 },
                titlefont: { color: '#e0e6ed', size: 13, family: '"Inter", sans-serif' },
                zeroline: false,
                showgrid: true,
                gridwidth: 1
            },
            yaxis: {
                gridcolor: 'rgba(255,255,255,0.1)',
                linecolor: 'rgba(255,255,255,0.2)',
                tickcolor: 'rgba(255,255,255,0.2)',
                tickfont: { color: '#b0b7c3', size: 11 },
                titlefont: { color: '#e0e6ed', size: 13, family: '"Inter", sans-serif' },
                zeroline: false,
                showgrid: true,
                gridwidth: 1
            },
            legend: {
                font: { color: '#e0e6ed', size: 11 },
                bgcolor: 'rgba(255,255,255,0.05)',
                bordercolor: 'rgba(255,255,255,0.1)',
                borderwidth: 1,
                orientation: 'h',
                x: 0,
                y: -0.2
            },
            title: {
                font: { 
                    color: '#e0e6ed', 
                    size: 16, 
                    family: '"Inter", sans-serif' 
                },
                x: 0.02,
                xanchor: 'left'
            },
            hoverlabel: {
                bgcolor: 'rgba(17, 17, 17, 0.95)',
                bordercolor: 'rgba(0, 102, 204, 0.5)',
                font: { color: '#e0e6ed', size: 12 }
            },
            annotations: [],
            shapes: []
        }
    };
}

// Apply professional styling to individual traces
function applyProfessionalTraceStyle(trace) {
    // Line styling
    if (trace.type === 'scatter' && trace.mode && trace.mode.includes('lines')) {
        trace.line = trace.line || {};
        trace.line.width = trace.line.width || 3;
        
        // Add smooth curves for line charts
        if (!trace.line.shape) {
            trace.line.shape = 'spline';
        }
    }
    
    // Bar styling
    if (trace.type === 'bar') {
        trace.marker = trace.marker || {};
        trace.marker.line = trace.marker.line || {};
        trace.marker.line.width = 0.5;
        trace.marker.line.color = 'rgba(255,255,255,0.1)';
        
        // Add gradient effect for bars
        if (!trace.marker.color || typeof trace.marker.color === 'string') {
            trace.marker.opacity = 0.8;
        }
    }
    
    // Scatter plot styling
    if (trace.type === 'scatter' && trace.mode && trace.mode.includes('markers')) {
        trace.marker = trace.marker || {};
        trace.marker.size = trace.marker.size || 8;
        trace.marker.line = trace.marker.line || {};
        trace.marker.line.width = 2;
        trace.marker.line.color = 'rgba(255,255,255,0.3)';
    }
    
    // Pie chart styling
    if (trace.type === 'pie') {
        trace.textinfo = trace.textinfo || 'label+percent';
        trace.textposition = 'auto';
        trace.textfont = { color: '#ffffff', size: 12 };
        trace.marker = trace.marker || {};
        trace.marker.line = { color: 'rgba(255,255,255,0.2)', width: 2 };
        trace.hole = trace.hole || 0.3; // Donut style
    }
    
    // Heatmap styling
    if (trace.type === 'heatmap') {
        trace.colorscale = trace.colorscale || [
            [0, '#0066cc'],
            [0.5, '#00ff88'],
            [1, '#ff6b6b']
        ];
    }
    
    return trace;
}

// CSV Download functionality that respects zoom/filter
async function downloadCsv(gd) {
    const xaxis = gd.layout.xaxis.range || [gd._fullData[0].x[0], gd._fullData[0].x.at(-1)];
    const rows = [];
    gd.data.forEach(t => {
        t.x.forEach((x, i) => {
            if (x >= xaxis[0] && x <= xaxis[1]) {
                rows.push({date: x, label: t.name, value: t.y[i]});
            }
        });
    });
    const csv = 'date,label,value\n' + rows.map(r => `${r.date},${r.label},${r.value}`).join('\n');
    const blob = new Blob([csv], {type: 'text/csv'});
    const a = Object.assign(document.createElement('a'), {
        href: URL.createObjectURL(blob),
        download: 'chart.csv'
    });
    a.click();
    URL.revokeObjectURL(a.href);
}

// Keep existing Plotly CSV download for compatibility
window.Plotly.downloadCsv = downloadCsv; 

// Enhanced chart creation function with professional styling
window.createProfessionalChart = function(elId, data, layout, config = {}) {
    // Apply professional template
    const professionalLayout = Object.assign({}, getProfessionalChartTemplate().layout, layout);
    
    // Ensure clear backgrounds
    professionalLayout.paper_bgcolor = 'rgba(0,0,0,0)';
    professionalLayout.plot_bgcolor = 'rgba(0,0,0,0)';
    
    // Apply professional styling to all traces
    const styledData = data.map(trace => {
        const styledTrace = Object.assign({}, trace);
        applyProfessionalTraceStyle(styledTrace);
        return styledTrace;
    });
    
    // Enhanced hover tooltips
    styledData.forEach(trace => {
        if (trace.y && Array.isArray(trace.y)) {
            trace.customdata = trace.y;
            trace.hovertemplate = '%{y:$,.1f}<br>(Δ %{customdata:.2%})<extra></extra>';
        }
    });
    
    // Professional config
    const professionalConfig = Object.assign({
        responsive: true,
        displaylogo: false,
        modeBarButtonsToAdd: ['downloadCsv', 'hoverClosest'],
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d', 'autoScale2d'],
        displayModeBar: true,
        toImageButtonOptions: {
            format: 'png',
            filename: elId + '_professional_chart',
            height: 600,
            width: 1000,
            scale: 2
        }
    }, config);
    
    Plotly.newPlot(elId, styledData, professionalLayout, { ...professionalConfig, template: PLOTLY_TEMPLATE });
    
    // Add ResizeObserver for responsive chart resizing
    const gd = document.getElementById(elId);
    if (gd && gd.parentElement) {
        new ResizeObserver(() => {
            if (window.Plotly && window.Plotly.Plots) {
                window.Plotly.Plots.resize(gd);
            }
        }).observe(gd.parentElement);
    }
    
    // Make chart draggable after creation
    setTimeout(() => {
        if (window.draggableChartManager) {
            const chartElement = document.getElementById(elId).closest('.chart-container, .chart-card');
            if (chartElement) {
                window.draggableChartManager.makeDraggable(chartElement);
            }
        }
    }, 100);
}

// Draggable Chart Window System
class DraggableChartManager {
    constructor() {
        this.draggedElement = null;
        this.offset = { x: 0, y: 0 };
        this.zIndexCounter = 1000;
        this.init();
    }

    init() {
        this.addDraggableToExistingCharts();
        this.setupGlobalEventListeners();
        this.addResetButton();
    }

    addDraggableToExistingCharts() {
        // Find all chart containers and make them draggable
        const chartContainers = document.querySelectorAll('.chart-container, .chart-card');
        chartContainers.forEach(container => {
            this.makeChartDraggable(container);
        });
    }

    makeChartDraggable(chartContainer) {
        // Skip if already made draggable
        if (chartContainer.classList.contains('draggable-chart')) {
            return;
        }

        chartContainer.classList.add('draggable-chart');
        
        // Add draggable styles
        chartContainer.style.position = 'relative';
        chartContainer.style.cursor = 'move';
        chartContainer.style.transition = 'transform 0.2s ease, box-shadow 0.2s ease';
        
        // Add drag handle to the header
        const header = chartContainer.querySelector('.card-header, .chart-title');
        if (header) {
            header.style.cursor = 'move';
            header.style.userSelect = 'none';
            
            // Add drag icon
            const dragIcon = document.createElement('i');
            dragIcon.className = 'fas fa-grip-vertical drag-handle';
            dragIcon.style.cssText = `
                position: absolute;
                right: 10px;
                top: 50%;
                transform: translateY(-50%);
                color: rgba(255, 255, 255, 0.5);
                cursor: move;
                font-size: 14px;
            `;
            header.style.position = 'relative';
            header.appendChild(dragIcon);
        }

        // Add event listeners
        chartContainer.addEventListener('mousedown', this.handleMouseDown.bind(this));
        chartContainer.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
    }

    handleMouseDown(e) {
        // Only start drag if clicking on header or drag handle
        const header = e.currentTarget.querySelector('.card-header, .chart-title');
        const dragHandle = e.target.closest('.drag-handle');
        const isPlotlyElement = e.target.closest('.plotly');
        
        // Don't drag if clicking on the actual chart (Plotly element)
        if (isPlotlyElement) {
            return;
        }
        
        if (!header || (!header.contains(e.target) && !dragHandle)) {
            return;
        }

        e.preventDefault();
        this.startDrag(e.currentTarget, e.clientX, e.clientY);
    }

    handleTouchStart(e) {
        const header = e.currentTarget.querySelector('.card-header, .chart-title');
        const dragHandle = e.target.closest('.drag-handle');
        const isPlotlyElement = e.target.closest('.plotly');
        
        // Don't drag if clicking on the actual chart (Plotly element)
        if (isPlotlyElement) {
            return;
        }
        
        if (!header || (!header.contains(e.target) && !dragHandle)) {
            return;
        }

        e.preventDefault();
        const touch = e.touches[0];
        this.startDrag(e.currentTarget, touch.clientX, touch.clientY);
    }

    startDrag(element, clientX, clientY) {
        this.draggedElement = element;
        
        // Bring to front
        element.style.zIndex = ++this.zIndexCounter;
        
        // Add dragging class for visual feedback
        element.classList.add('dragging');
        element.style.boxShadow = '0 20px 60px rgba(0, 102, 204, 0.4), 0 0 30px rgba(0, 102, 204, 0.3)';
        element.style.transform = 'scale(1.02)';
        
        // Calculate offset from mouse to element's top-left corner
        const rect = element.getBoundingClientRect();
        this.offset.x = clientX - rect.left;
        this.offset.y = clientY - rect.top;
        
        // Change cursor for entire document
        document.body.style.cursor = 'move';
        document.body.style.userSelect = 'none';
    }

    setupGlobalEventListeners() {
        // Mouse events
        document.addEventListener('mousemove', this.handleMouseMove.bind(this));
        document.addEventListener('mouseup', this.handleMouseUp.bind(this));
        
        // Touch events
        document.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        document.addEventListener('touchend', this.handleTouchEnd.bind(this));
    }

    handleMouseMove(e) {
        if (!this.draggedElement) return;
        
        e.preventDefault();
        this.updatePosition(e.clientX, e.clientY);
    }

    handleTouchMove(e) {
        if (!this.draggedElement) return;
        
        e.preventDefault();
        const touch = e.touches[0];
        this.updatePosition(touch.clientX, touch.clientY);
    }

    updatePosition(clientX, clientY) {
        if (!this.draggedElement) return;
        
        // Calculate new position
        const newX = clientX - this.offset.x;
        const newY = clientY - this.offset.y;
        
        // Get viewport bounds
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const elementRect = this.draggedElement.getBoundingClientRect();
        
        // Constrain to viewport (optional - remove these lines if you want unlimited movement)
        const constrainedX = Math.max(0, Math.min(newX, viewportWidth - elementRect.width));
        const constrainedY = Math.max(0, Math.min(newY, viewportHeight - elementRect.height));
        
        // Apply position with better width handling
        this.draggedElement.style.position = 'fixed';
        this.draggedElement.style.left = constrainedX + 'px';
        this.draggedElement.style.top = constrainedY + 'px';
        
        // Only set width if it's not already constrained by CSS
        if (!this.draggedElement.style.maxWidth) {
            this.draggedElement.style.width = Math.min(elementRect.width, 600) + 'px';
        }
    }

    handleMouseUp(e) {
        this.endDrag();
    }

    handleTouchEnd(e) {
        this.endDrag();
    }

    endDrag() {
        if (!this.draggedElement) return;
        
        // Remove dragging visual feedback
        this.draggedElement.classList.remove('dragging');
        this.draggedElement.style.boxShadow = '';
        this.draggedElement.style.transform = '';
        
        // Reset cursor
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        
        this.draggedElement = null;
    }

    // Method to reset all charts to their original positions
    resetAllCharts() {
        const draggableCharts = document.querySelectorAll('.draggable-chart');
        draggableCharts.forEach(chart => {
            chart.style.position = 'relative';
            chart.style.left = '';
            chart.style.top = '';
            chart.style.width = '';
            chart.style.zIndex = '';
        });
    }

    // Add reset button
    addResetButton() {
        const resetBtn = document.createElement('button');
        resetBtn.className = 'chart-reset-btn';
        resetBtn.innerHTML = '<i class="fas fa-undo"></i> Reset Charts';
        resetBtn.onclick = () => this.resetAllCharts();
        document.body.appendChild(resetBtn);
    }

    // Method to make a specific chart draggable (for dynamically added charts)
    makeDraggable(chartElement) {
        this.makeChartDraggable(chartElement);
    }
}

// Initialize the draggable chart manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.draggableChartManager = new DraggableChartManager();
});

// Also initialize if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        window.draggableChartManager = new DraggableChartManager();
    });
} else {
    window.draggableChartManager = new DraggableChartManager();
}

// Export for use in other scripts
window.DraggableChartManager = DraggableChartManager;

// Global SHIFT + double-click reset for all charts
document.addEventListener('dblclick', e => {
    if (e.shiftKey) {
        // Reset all chart zooms
        document.querySelectorAll('.plotly').forEach(gd => {
            if (window.Plotly && window.Plotly.relayout) {
                window.Plotly.relayout(gd, {
                    'xaxis.autorange': true,
                    'yaxis.autorange': true
                });
            }
        });
        
        // Emit zoom reset event if bus exists
        if (window.bus && window.bus.emit) {
            window.bus.emit('zoom', null);
        }
        
        console.log('🔄 All charts reset via SHIFT + double-click');
    }
}); 