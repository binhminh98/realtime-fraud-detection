"""
Module to specify styles.
"""

app_style = {
    "backgroundColor": "#121526",
    "minHeight": "100vh",
    "padding": "20px",
}

card_style = {
    "backgroundColor": "#202640",
    "color": "#ffffff",
    "padding": "15px",
    "borderRadius": "10px",
    "boxShadow": "0 4px 12px rgba(0,0,0,0.3)",
    # "height": "100%",
}

text_style = {
    "fontFamily": "Nunito",
    "color": "#ebe6ff",
    "letterSpacing": "0.04em",
    "marginBottom": "1rem",
    "textShadow": "0 1px 2px rgba(0,0,0,0.5)",
}

title_in_figure_style = {
    "family": "Nunito",
    "color": "#ebe6ff",
    "size": 18,
}

text_in_figure_style = {
    "family": "Nunito",
    "color": "#ebe6ff",
    "size": 14,
}

chart_layout = dict(
    plot_bgcolor="#181c30",
    paper_bgcolor="#181c30",
    font=text_in_figure_style,
    title_font=title_in_figure_style,
    title_x=0.5,
    xaxis=dict(
        showgrid=False,
        rangemode="tozero",
    ),
    yaxis=dict(
        showgrid=True,
        rangemode="tozero",
        gridcolor="rgba(200, 200, 200, 0.1)",
        zerolinecolor="rgba(200, 200, 200, 0.15)",
        linecolor="rgba(255,255,255,0.5)",
        tickfont=dict(color="white"),
    ),
)
