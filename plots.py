def apply_plot_style(fig, is_dark=True, height=330, reverse_y=False):
    """Applies clean unified theme styling to Plotly figures."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#71717a" if is_dark else "#475569", size=11),
        margin=dict(l=10, r=10, t=25, b=10),
        height=height
    )
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.06)" if is_dark else "rgba(0,0,0,0.06)",
        zerolinecolor="rgba(255,255,255,0.06)" if is_dark else "rgba(0,0,0,0.06)",
        tickfont=dict(size=10)
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.06)" if is_dark else "rgba(0,0,0,0.06)",
        zerolinecolor="rgba(255,255,255,0.06)" if is_dark else "rgba(0,0,0,0.06)",
        tickfont=dict(size=10),
        autorange="reversed" if reverse_y else None
    )
    return fig
