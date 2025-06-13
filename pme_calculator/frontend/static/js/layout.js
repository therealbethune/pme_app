/**
 * Layout management with GridStack and Plotly resize handling
 */

// Initialize GridStack with enhanced configuration
const grid = GridStack.init({
    column: 16,  // Increased from 12 for better granularity
    float: true, // Allow floating layout
    cellHeight: 'auto',
    margin: 10,
    resizable: {
        handles: 'e, se, s, sw, w'
    },
    draggable: {
        handle: '.card-header'
    }
});

// Global resize handler for Plotly charts
window.addEventListener('resize', () => {
    document.querySelectorAll('.plotly').forEach(gd => {
        if (window.Plotly && window.Plotly.Plots) {
            window.Plotly.Plots.resize(gd);
        }
    });
});

// GridStack item resize handler for Plotly charts
grid.on('resizestop', (event, element) => {
    const plotlyDiv = element.querySelector('.plotly');
    if (plotlyDiv && window.Plotly && window.Plotly.Plots) {
        // Small delay to ensure DOM has updated
        setTimeout(() => {
            window.Plotly.Plots.resize(plotlyDiv);
        }, 100);
    }
});

// Export for use in other modules
window.layoutGrid = grid; 