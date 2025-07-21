# Standard Library Imports
from typing import Any, Dict

# Third-Party Imports
import plotly.graph_objects as go


def create_plotly_chart_dict(freq_data: Dict[str, int], data_name: str, chart_type: str, chart_title: str) -> Dict[str, Any]:
    """
    Creates a JSON-serializable dictionary of a Plotly chart for frequency data.

    Args:
        freq_data: A dictionary with item names as keys and their frequencies as values.
        data_name: The name of the data being plotted (e.g., "Topic", "Category").
        chart_type: The type of chart to generate ('bar', 'donut', or 'line').
        chart_title: The title of the chart.

    Returns:
        A dictionary representing the Plotly figure, ready for JSON serialization.
    """
    # Sort data for bar charts, but preserve original order for line charts
    if chart_type == 'bar':
        sorted_items = sorted(freq_data.items(), key=lambda x: x[1])
    else:
        sorted_items = freq_data.items()
        
    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]

    if chart_type == 'bar':
        fig = go.Figure(data=[go.Bar(x=values, y=labels, orientation='h')])
        fig.update_layout(
            title_text=chart_title,
            xaxis_title="Frequency",
            yaxis=dict(tickmode='array', tickvals=labels, ticktext=labels),
            margin=dict(l=150), # Add left margin to prevent labels from being cut off
            height=max(400, len(labels) * 25) # Dynamically adjust height
        )
    elif chart_type == 'donut':
        legend_title = "Categories" if data_name == "Category" else data_name + 's'
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4)])
        fig.update_layout(
            title_text=chart_title,
            legend_title_text=legend_title
        )
    elif chart_type == 'timeseries_bar':
        # Define a blue color scale
        blue_colorscale = [
            [0, 'rgb(204, 204, 255)'],  # Lightest blue
            [0.2, 'rgb(153, 153, 255)'],
            [0.4, 'rgb(102, 102, 255)'],
            [0.6, 'rgb(51, 51, 255)'],
            [0.8, 'rgb(100, 100, 200)'],    # Softer pure blue
            [1, 'rgb(50, 50, 150)']     # Darkest blue (softer)
        ]

        fig = go.Figure(data=[go.Bar(
            x=labels,
            y=values,
            marker=dict(
                color=values,  # Color based on the 'values' (number of videos watched)
                colorscale=blue_colorscale,
                showscale=True
            )
        )])
        fig.update_layout(
            title_text=chart_title,
            xaxis_title="Month",
            yaxis_title="Number of Videos Watched",
            width=None,
            height=None,
            xaxis_rangeslider_visible=True
        )
    elif chart_type == 'daily_needle_chart':
        fig = go.Figure(data=[go.Scatter(x=labels, y=values, mode='lines', line=dict(width=1, color='#FF9999'))])
        fig.update_layout(
            title_text=chart_title,
            xaxis_title="Date",
            yaxis_title="Number of Videos Watched",
            width=None,
            height=None,
            showlegend=False
        )
    elif chart_type == 'line':
        fig = go.Figure(data=go.Scatter(x=labels, y=values, mode='lines+markers'))
        fig.update_layout(
            title_text=chart_title,
            xaxis_title="Date",
            yaxis_title="Number of Videos Watched"
        )
    else:
        fig = go.Figure() # Return an empty figure if chart_type is invalid

    return fig.to_dict()
