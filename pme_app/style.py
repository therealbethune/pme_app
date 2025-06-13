from ttkbootstrap import Style

# Glasfunds Color Palette for Web Application
# This module provides color constants for consistent styling across the web interface

GLASFUNDS_COLORS = {
    # Primary colors
    'primary_blue': '#005F8C',
    'primary_teal': '#0FA689', 
    'primary_orange': '#FF7E42',
    'primary_purple': '#7A4FFF',
    
    # Gray scale
    'gray_100': '#F7F9FA',
    'gray_200': '#DDE3E6', 
    'gray_300': '#D9DCE0',
    'gray_700': '#4B5563',
    
    # Status colors
    'success': '#0FA689',
    'warning': '#FF7E42',
    'error': '#DC2626',
    'info': '#005F8C',
    
    # Background colors
    'background_light': '#F7F9FA',
    'background_white': '#FFFFFF',
    'card_background': '#FFFFFF',
    'border_color': '#DDE3E6'
}

# Metric-specific colors for consistency
METRIC_COLORS = {
    'IRR': GLASFUNDS_COLORS['primary_blue'],
    'TVPI': GLASFUNDS_COLORS['primary_teal'],
    'DPI': GLASFUNDS_COLORS['primary_orange'],
    'RVPI': GLASFUNDS_COLORS['primary_purple'],
    'Direct': GLASFUNDS_COLORS['primary_blue']
}

def get_glasfunds_color(color_name):
    """Get a Glasfunds color by name."""
    return GLASFUNDS_COLORS.get(color_name, GLASFUNDS_COLORS['gray_700'])

def get_metric_color(metric_name):
    """Get the appropriate color for a specific metric."""
    return METRIC_COLORS.get(metric_name, GLASFUNDS_COLORS['primary_blue'])

def glasfunds_style(dark=False):
    """
    Apply Glasfunds brand palette and typography to the app.
    Returns a ttkbootstrap.Style instance.
    """
    theme = 'darkly' if dark else 'flatly'
    s = Style(theme=theme)
    s.configure('.', font=('Inter', 11))
    # Base backgrounds and text
    s.configure('.', background='#F7F9FA', foreground='#4B5563')  # gf-gray-100, gf-gray-700
    # Card style
    s.configure('Card.TFrame', padding=14, relief='flat',
                background='white', borderwidth=1,
                bordercolor='#DDE3E6', borderradius=6)
    # KPI colours
    for k, c in {'IRR':'#005F8C', 'TVPI':'#0FA689',
                 'DPI':'#FF7E42', 'RVPI':'#7A4FFF',
                 'Direct':'#005F8C'}.items():
        s.configure(f'{k}.TLabel', foreground=c, font=('Inter', 22, 'bold'))
    # Nav bar
    s.configure('Nav.TFrame', background='#005F8C')
    s.configure('Nav.TLabel', background='#005F8C', foreground='white', font=('Inter',13,'bold'))
    s.configure('Nav.TButton', background='#005F8C', foreground='white', font=('Inter',13,'bold'))
    # Stepper
    s.configure('Stepper.TLabel', background='#F7F9FA', foreground='#005F8C', font=('Inter', 11, 'bold'))
    s.configure('StepperLineActive.TFrame', background='#005F8C')
    s.configure('StepperLineInactive.TFrame', background='#D9DCE0')
    # Body text
    s.configure('Body.TLabel', background='white', foreground='#4B5563', font=('Inter', 12))
    return s
