from ttkbootstrap import Style


def glasfunds_style(dark=False):
    """
    Apply Glasfunds brand palette and typography to the app.
    Returns a ttkbootstrap.Style instance.
    """
    theme = "darkly" if dark else "flatly"
    s = Style(theme=theme)
    s.configure(".", font=("Inter", 11))
    # Base backgrounds and text
    s.configure(
        ".", background="#F7F9FA", foreground="#4B5563"
    )  # gf-gray-100, gf-gray-700
    # Card style
    s.configure(
        "Card.TFrame",
        padding=14,
        relief="flat",
        background="white",
        borderwidth=1,
        bordercolor="#DDE3E6",
        borderradius=6,
    )
    # KPI colours
    for k, c in {
        "IRR": "#005F8C",
        "TVPI": "#0FA689",
        "DPI": "#FF7E42",
        "RVPI": "#7A4FFF",
        "Direct": "#005F8C",
    }.items():
        s.configure(f"{k}.TLabel", foreground=c, font=("Inter", 22, "bold"))
    # Nav bar
    s.configure("Nav.TFrame", background="#005F8C")
    s.configure(
        "Nav.TLabel",
        background="#005F8C",
        foreground="white",
        font=("Inter", 13, "bold"),
    )
    s.configure(
        "Nav.TButton",
        background="#005F8C",
        foreground="white",
        font=("Inter", 13, "bold"),
    )
    # Stepper
    s.configure(
        "Stepper.TLabel",
        background="#F7F9FA",
        foreground="#005F8C",
        font=("Inter", 11, "bold"),
    )
    s.configure("StepperLineActive.TFrame", background="#005F8C")
    s.configure("StepperLineInactive.TFrame", background="#D9DCE0")
    # Body text
    s.configure(
        "Body.TLabel", background="white", foreground="#4B5563", font=("Inter", 12)
    )
    return s
