export const PLOTLY_TEMPLATE = {
    layout: {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#cbd5e1' },
        xaxis: { 
            gridcolor: '#334155', 
            zerolinecolor: '#334155',
            tickcolor: '#cbd5e1',
            linecolor: '#334155'
        },
        yaxis: { 
            gridcolor: '#334155', 
            zerolinecolor: '#334155',
            tickcolor: '#cbd5e1',
            linecolor: '#334155'
        }
    }
};

// Initialize theme from localStorage or default to light
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.dataset.bsTheme = savedTheme;
    }
    
    const next = {light:'dark', dark:'light'};
    const themeToggle = document.querySelector('#themeToggle');
    if (themeToggle) {
        themeToggle.onclick = () => {
            document.body.dataset.bsTheme = next[document.body.dataset.bsTheme];
            localStorage.setItem('theme', document.body.dataset.bsTheme);
            if (typeof Plotly !== 'undefined') {
                Plotly.reactAll();                              // force recolor
            }
        };
    }
});

// Make PLOTLY_TEMPLATE available globally
window.PLOTLY_TEMPLATE = PLOTLY_TEMPLATE; 