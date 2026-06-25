"""
charts.py
---------
Chart-building helpers for the AI Business Idea Generator app.

Uses Plotly for interactive, responsive charts that look good in both
light and dark Streamlit themes.
"""

from typing import List
import plotly.graph_objects as go

from idea_generator import BusinessIdea


# Consistent color palette across all charts in the app.
PRIMARY_COLOR = "#6C5CE7"
SECONDARY_COLOR = "#00B894"
ACCENT_COLOR = "#FDCB6E"
TEXT_COLOR = "#2D3436"


def build_startup_cost_chart(ideas: List[BusinessIdea]) -> go.Figure:
    """Build a horizontal bar chart comparing estimated startup costs.

    Each bar shows a range (min-max) per business idea using an
    error-bar style range marker for a clean, professional look.
    """
    names = [f"{idea.rank}. {idea.name}" for idea in ideas]
    mins = [idea.startup_cost_min for idea in ideas]
    maxs = [idea.startup_cost_max for idea in ideas]
    midpoints = [(mn + mx) / 2 for mn, mx in zip(mins, maxs)]
    errors = [(mx - mn) / 2 for mn, mx in zip(mins, maxs)]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=midpoints,
            y=names,
            orientation="h",
            error_x=dict(type="data", array=errors, color=TEXT_COLOR, thickness=1.5),
            marker=dict(color=PRIMARY_COLOR, line=dict(width=0)),
            text=[f"${mn:,.0f} - ${mx:,.0f}" for mn, mx in zip(mins, maxs)],
            textposition="outside",
            hovertemplate="%{y}<br>Estimated cost: %{text}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Estimated Startup Cost by Idea (USD)",
        xaxis_title="Startup Cost (USD)",
        yaxis_title=None,
        yaxis=dict(autorange="reversed"),  # Best idea (rank 1) shown on top
        margin=dict(l=10, r=10, t=50, b=10),
        height=380,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR, size=13),
    )
    return fig


def build_income_chart(ideas: List[BusinessIdea]) -> go.Figure:
    """Build a horizontal bar chart comparing potential monthly income."""
    names = [f"{idea.rank}. {idea.name}" for idea in ideas]
    mins = [idea.monthly_income_min for idea in ideas]
    maxs = [idea.monthly_income_max for idea in ideas]
    midpoints = [(mn + mx) / 2 for mn, mx in zip(mins, maxs)]
    errors = [(mx - mn) / 2 for mn, mx in zip(mins, maxs)]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=midpoints,
            y=names,
            orientation="h",
            error_x=dict(type="data", array=errors, color=TEXT_COLOR, thickness=1.5),
            marker=dict(color=SECONDARY_COLOR, line=dict(width=0)),
            text=[f"${mn:,.0f} - ${mx:,.0f}" for mn, mx in zip(mins, maxs)],
            textposition="outside",
            hovertemplate="%{y}<br>Estimated monthly income: %{text}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Potential Monthly Income by Idea (USD)",
        xaxis_title="Monthly Income (USD)",
        yaxis_title=None,
        yaxis=dict(autorange="reversed"),
        margin=dict(l=10, r=10, t=50, b=10),
        height=380,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR, size=13),
    )
    return fig


def build_score_chart(ideas: List[BusinessIdea]) -> go.Figure:
    """Build a vertical bar chart showing the viability score (1-100)."""
    names = [f"#{idea.rank}" for idea in ideas]
    scores = [idea.score for idea in ideas]
    full_names = [idea.name for idea in ideas]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=names,
            y=scores,
            marker=dict(
                color=scores,
                colorscale=[[0, "#FF7675"], [0.5, ACCENT_COLOR], [1, SECONDARY_COLOR]],
                cmin=0,
                cmax=100,
                line=dict(width=0),
            ),
            text=scores,
            textposition="outside",
            customdata=full_names,
            hovertemplate="%{customdata}<br>Score: %{y}/100<extra></extra>",
        )
    )
    fig.update_layout(
        title="Business Viability Score (1-100)",
        xaxis_title="Idea Rank",
        yaxis_title="Score",
        yaxis=dict(range=[0, 110]),
        margin=dict(l=10, r=10, t=50, b=10),
        height=320,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR, size=13),
    )
    return fig
