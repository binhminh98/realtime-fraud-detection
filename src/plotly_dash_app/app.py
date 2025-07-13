import os

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from dash import dcc, html
from dash.dependencies import Input, Output, State
from kafka_consumer import KafkaMessageCollector
from sklearn.metrics import classification_report, confusion_matrix
from styles import (
    app_style,
    card_style,
    chart_layout,
    input_field,
    purple_button,
    text_style,
)

# Create Kafka Consumer
collector = KafkaMessageCollector(
    kafka_config={
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        "group.id": "ml_transaction_consumer",
        "auto.offset.reset": "earliest",
    },
    topic="transactions",
    fastapi_url=os.getenv("FASTAPI_URI"),
)

# Dash App Setup
app = dash.Dash(
    __name__,
    title="Fraud Detection Dashboard",
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Nunito:wght@400;600&display=swap",
    ],
)

app.layout = html.Div(
    [
        html.Br(),
        dbc.Row(
            dbc.Col(
                html.H2(
                    "Real-time Fraud Detection Dashboard 💳",
                    style=text_style,
                    className="text-center",
                ),
                width=12,
            ),
            className="mb-4",
            style={"display": "flex", "alignItems": "stretch"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            html.Div(
                                id="total-transaction",
                                style=card_style,
                            ),
                        ),
                        dbc.Row(
                            html.Div(
                                id="predicted-transaction",
                                style=card_style,
                            ),
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    html.Div(
                        dcc.Graph(
                            id="transaction-line-chart",
                        ),
                        style=card_style,
                    ),
                    width=3,
                ),
                dbc.Col(
                    html.Div(
                        dcc.Graph(
                            id="model-performance-bar-chart",
                        ),
                        style=card_style,
                    ),
                    width=3,
                ),
                dbc.Col(
                    html.Div(
                        dcc.Graph(
                            id="model-confusion-matrix",
                        ),
                        style=card_style,
                    ),
                    width=3,
                ),
            ],
            className="mb-4",
            justify="center",
            style={"display": "flex", "alignItems": "stretch"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            html.Div(
                                id="average-inference-latency",
                                style=card_style,
                            ),
                        ),
                        dbc.Row(
                            html.Div(
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.Input(
                                                id="produce-transaction-num-messages",
                                                type="number",
                                                placeholder="Enter an integer",
                                                debounce=True,
                                                step=1,
                                                style=input_field,
                                            ),
                                            width=6,
                                        ),
                                        dbc.Col(
                                            html.Button(
                                                "Produce Transactions",
                                                id="produce-transaction-button",
                                                n_clicks=0,
                                                style=purple_button,
                                            ),
                                            width=6,
                                        ),
                                    ],
                                    id="transactions-producer",
                                ),
                                style=card_style,
                            ),
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    html.Div(
                        dcc.Graph(
                            id="latency-percentile-chart",
                        ),
                        style=card_style,
                    ),
                    width=3,
                ),
                dbc.Col(
                    html.Div(
                        dcc.Graph(id="inferences-per-second-chart"),
                        style=card_style,
                    ),
                    width=3,
                ),
                dbc.Col(
                    html.Div(
                        dcc.Graph(id="latency-histogram"),
                        style=card_style,
                    ),
                    width=3,
                ),
            ],
            className="mb-4",
            justify="center",
            style={"display": "flex", "alignItems": "stretch"},
        ),
        dcc.Interval(
            id="interval-component", interval=5000, n_intervals=0
        ),  # Update every 5 sec
        dbc.Alert(
            id="fraud-alert",
            is_open=False,
            dismissable=True,
            color="danger",
            style={
                "position": "fixed",
                "top": "20px",
                "right": "20px",
                "width": "300px",
                "zIndex": 1050,
                "boxShadow": "0 4px 12px rgba(0,0,0,0.15)",
            },
        ),
        dbc.Alert(
            id="transactions-producer-alert",
            is_open=False,
            dismissable=True,
            style={
                "position": "fixed",
                "top": "20px",
                "left": "20px",
                "width": "300px",
                "zIndex": 1050,
                "boxShadow": "0 4px 12px rgba(0,0,0,0.15)",
            },
        ),
    ],
    style=app_style,
)


@app.callback(
    [
        Output("transactions-producer-alert", "children"),
        Output("transactions-producer-alert", "is_open"),
        Output("transactions-producer-alert", "color"),
    ],
    Input("produce-transaction-button", "n_clicks"),
    State("produce-transaction-num-messages", "value"),
)
def produce_transations(n_clicks, value):
    if n_clicks > 0:
        if value is None:
            return "Please enter a valid number!", True, "danger"

        try:
            int_value = int(value)
            response = requests.post(
                f"{os.getenv('FASTAPI_URI')}/producers/produce_transactions/{int_value}",
            )

            return eval(response.text), True, "success"

        except (ValueError, TypeError):
            return "Invalid input! Please enter an integer.", True, "danger"

    else:
        return [dash.no_update] * 3


@app.callback(
    [
        Output("total-transaction", "children"),
    ],
    [Input("interval-component", "n_intervals")],
)
def update_total_transactions(_):
    _, transaction_ground_truth = collector.get_prediction_results()
    total_transaction = len(transaction_ground_truth)
    normal_transactions = transaction_ground_truth.count(0)
    fraud_transactions = transaction_ground_truth.count(1)

    return [
        html.Div(
            [
                dbc.Row(
                    [
                        html.H4("Total transactions:", style=text_style),
                        html.H4(str(total_transaction), style=text_style),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.H4("Normal", style=text_style),
                                    html.H4(
                                        str(normal_transactions),
                                        style=text_style,
                                    ),
                                ],
                                style=card_style,
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.H4("Fraud", style=text_style),
                                    html.H4(
                                        str(fraud_transactions),
                                        style=text_style,
                                    ),
                                ],
                                style=card_style,
                            ),
                            width=6,
                        ),
                    ],
                ),
            ],
            id="total-transaction-children",
            style={
                "textAlign": "center",
                "height": "100%",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "flexDirection": "column",
            },
        )
    ]


@app.callback(
    [
        Output("predicted-transaction", "children"),
    ],
    [Input("interval-component", "n_intervals")],
)
def update_total_transactions(_):
    prediction_history, _ = collector.get_prediction_results()
    total_transaction = len(prediction_history)
    normal_transactions = prediction_history.count(0)
    fraud_transactions = prediction_history.count(1)

    return [
        html.Div(
            [
                dbc.Row(
                    [
                        html.H4("Predicted transactions:", style=text_style),
                        html.H4(str(total_transaction), style=text_style),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.H4("Normal", style=text_style),
                                    html.H4(
                                        str(normal_transactions),
                                        style=text_style,
                                    ),
                                ],
                                style=card_style,
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.H4("Fraud", style=text_style),
                                    html.H4(
                                        str(fraud_transactions),
                                        style=text_style,
                                    ),
                                ],
                                style=card_style,
                            ),
                            width=6,
                        ),
                    ],
                ),
            ],
            id="predicted-transaction-children",
            style={
                "textAlign": "center",
                "height": "100%",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "flexDirection": "column",
            },
        )
    ]


# Model performance
@app.callback(
    [
        Output("transaction-line-chart", "figure"),
        Output("fraud-alert", "children"),
        Output("fraud-alert", "is_open"),
    ],
    [Input("interval-component", "n_intervals")],
)
def update_line_chart(_):
    df = collector.get_transactions_in_buffer()

    if df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Waiting for transactions stream!",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20),
            align="center",
        )

        empty_fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        return empty_fig, dash.no_update, dash.no_update

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["timestamp_bin"] = df["timestamp"].dt.floor("10s")  # bin per 10s

    counts = (
        df.groupby(["timestamp_bin", "is_fraud"])
        .size()
        .reset_index(name="count")
    )

    pivot_df = counts.pivot(
        index="timestamp_bin", columns="is_fraud", values="count"
    )

    # Ensure both columns 0 (Normal) and 1 (Fraud) exist
    pivot_df = pivot_df.reindex(columns=[0, 1], fill_value=0)
    pivot_df.columns = ["Normal", "Fraud"]  # Rename for clarity
    pivot_df = pivot_df.reset_index()

    # Fraud alert logic
    recent_fraud = pivot_df["Fraud"].iloc[-1] if not pivot_df.empty else 0
    alert_message = "⚠️ Fraud detected by ML model!" if recent_fraud > 0 else ""
    open_fraud_alert = True if recent_fraud > 0 else False

    line_chart = px.line(
        pivot_df,
        x="timestamp_bin",
        y=["Normal", "Fraud"],
        labels={"timestamp_bin": "Time", "value": "Message Count"},
        title="Fraud vs Normal Message Counts (5s intervals)",
        color_discrete_map={
            "Normal": "#53dfe2",
            "Fraud": "#d073f0",
        },
    )

    # Add markers to the line
    line_chart.update_traces(
        mode="lines+markers",
        hovertemplate="%{y:.2f}",
    )

    line_chart.update_layout(hovermode="x unified", **chart_layout)

    return line_chart, alert_message, open_fraud_alert


# @app.callback(
#     Output("ground-truth-fraud-pie-chart", "figure"),
#     [Input("interval-component", "n_intervals")],
# )
# def update_ground_truth_pie_chart(_):
#     df = collector.get_ground_truth_counts()

#     if df.empty:
#         empty_fig = go.Figure()
#         empty_fig.add_annotation(
#             text="Waiting for transactions stream!",
#             xref="paper",
#             yref="paper",
#             x=0.5,
#             y=0.5,
#             showarrow=False,
#             font=dict(size=20),
#             align="center",
#         )

#         empty_fig.update_layout(
#             xaxis=dict(visible=False),
#             yaxis=dict(visible=False),
#             plot_bgcolor="rgba(0,0,0,0)",
#             paper_bgcolor="rgba(0,0,0,0)",
#         )

#         return empty_fig

#     pie_chart = px.pie(
#         df,
#         names="message_type",
#         values="counts",
#         title="Fraud vs Normal Messages Ratio (Ground Truth)",
#         hole=0.6,
#         color="message_type",
#         color_discrete_map={
#             "normal": "#53dfe2",
#             "fraud": "#d073f0",
#         },
#     )

#     pie_chart.update_traces(
#         pull=[0, 0.3],
#         textinfo="label+percent",
#         textposition="outside",
#         hovertemplate="%{label}: %{value} transactions (%{percent})<extra></extra>",
#     )

#     pie_chart.update_layout(**chart_layout)

#     return pie_chart


# @app.callback(
#     Output("predicted-fraud-pie-chart", "figure"),
#     [Input("interval-component", "n_intervals")],
# )
# def update_predicted_fraud_pie_chart(_):
#     df = collector.get_prediction_counts()

#     if df.empty:
#         empty_fig = go.Figure()
#         empty_fig.add_annotation(
#             text="Waiting for transactions stream!",
#             xref="paper",
#             yref="paper",
#             x=0.5,
#             y=0.5,
#             showarrow=False,
#             font=dict(size=20),
#             align="center",
#         )

#         empty_fig.update_layout(
#             xaxis=dict(visible=False),
#             yaxis=dict(visible=False),
#             plot_bgcolor="rgba(0,0,0,0)",
#             paper_bgcolor="rgba(0,0,0,0)",
#         )

#         return empty_fig

#     pie_chart = px.pie(
#         df,
#         names="message_type",
#         values="counts",
#         title="Fraud vs Normal Messages Ratio (Predicted)",
#         hole=0.6,
#         color="message_type",
#         color_discrete_map={
#             "normal": "#53dfe2",
#             "fraud": "#d073f0",
#         },
#     )

#     pie_chart.update_traces(
#         pull=[0, 0.3],
#         textinfo="label+percent",
#         textposition="outside",
#         hovertemplate="%{label}: %{value} transactions (%{percent})<extra></extra>",
#     )

#     pie_chart.update_layout(**chart_layout)

#     return pie_chart


@app.callback(
    Output("model-performance-bar-chart", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_model_performance_bar_chart(_):
    predictions, labels = collector.get_prediction_results()

    if not predictions:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="There are no fraud transactions!",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20),
            align="center",
        )

        empty_fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        return empty_fig

    report_dict = classification_report(
        labels, predictions, output_dict=True, zero_division=0
    )

    metrics = {
        "positive_precision": (
            report_dict["1"]["precision"] if report_dict.get("1") else 0
        ),
        "positive_recall": (
            report_dict["1"]["recall"] if report_dict.get("1") else 0
        ),
        "positive_f1": (
            report_dict["1"]["f1-score"] if report_dict.get("1") else 0
        ),
        "macro_precision": report_dict["macro avg"]["precision"],
        "macro_recall": report_dict["macro avg"]["recall"],
        "macro_f1": report_dict["macro avg"]["f1-score"],
    }

    metrics_df = pd.DataFrame(
        {
            "metric": [metric for metric in metrics.keys()],
            "score": [metric for metric in metrics.values()],
        }
    )

    bar_chart = px.bar(
        metrics_df,
        x="score",
        y="metric",
        orientation="h",
        title="Model Performance",
        color_discrete_sequence=["#d073f0"],
        text="score",
    )

    bar_chart.update_traces(
        texttemplate="%{text:.2f}",
    )

    # Add vertical dotted line at x=0.8
    bar_chart.add_shape(
        type="line",
        x0=0.8,
        x1=0.8,
        y0=-0.5,
        y1=len(metrics_df["metric"]) - 0.5,
        line=dict(
            color="#53dfe2",
            width=2,
            dash="dot",
        ),
    )

    # Add annotation
    bar_chart.add_annotation(
        x=0.8,
        y=len(metrics_df["metric"]),
        text="Good model performance",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#53dfe2",
        ax=40,
        ay=0,
        font=dict(
            color="#53dfe2",
            size=12,
        ),
        bgcolor="rgba(0,0,0,0)",
    )

    bar_chart.update_layout(**chart_layout)

    bar_chart.update_layout(
        xaxis=dict(
            tickmode="linear",
            dtick=0.2,
            range=[0, 1.02],
        ),
    )

    return bar_chart


@app.callback(
    Output("model-confusion-matrix", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_confusion_matrix(_):
    predictions, labels = collector.get_prediction_results()

    if not predictions:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Waiting for transactions stream!",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20),
            align="center",
        )

        empty_fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        return empty_fig

    cm = confusion_matrix(labels, predictions)

    confusion_matrix_fig = go.Figure(
        data=go.Heatmap(
            z=cm,
            x=["Normal", "Fraud"],
            y=["Normal", "Fraud"],
            colorscale="Agsunset",
            text=cm,
            texttemplate="%{text}",
            textfont={"size": 18},
        )
    )

    confusion_matrix_fig.update_layout(
        title="Confusion Matrix",
        xaxis_title="Predicted Label",
        yaxis_title="True Label",
        yaxis_autorange="reversed",
        **chart_layout,
    )

    return confusion_matrix_fig


# System performance
@app.callback(
    Output("average-inference-latency", "children"),
    [Input("interval-component", "n_intervals")],
)
def update_average_latency(_):
    average_latency = collector.get_average_latency()

    return [
        html.Div(
            [
                html.H4("Average latency:", style=text_style),
                html.H4(
                    str(round(average_latency, 5)) + "s", style=text_style
                ),
            ],
            id="average-inference-latency-children",
            style={
                "textAlign": "center",
                "height": "100%",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "flexDirection": "column",
            },
        )
    ]


@app.callback(
    Output("latency-percentile-chart", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_latency_percentile_chart(_):
    inference_latencies = collector.get_inference_latencies()

    if inference_latencies.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Waiting for transactions stream!",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20),
            align="center",
        )

        empty_fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        return empty_fig

    inference_latencies["timestamp_bin"] = inference_latencies[
        "timestamp"
    ].dt.floor(
        "10s"
    )  # bin per 10s

    latencies_percentile_by_timestamp = (
        inference_latencies.groupby(["timestamp_bin"])["latency"]
        .agg(
            p50=lambda x: np.percentile(x * 1000, 50),
            p90=lambda x: np.percentile(x * 1000, 90),
            p95=lambda x: np.percentile(x * 1000, 95),
            p99=lambda x: np.percentile(x * 1000, 99),
        )
        .reset_index(names="timestamp_bin")
    )

    # Create figure with 4 lines
    line_chart = go.Figure()

    line_chart.add_trace(
        go.Scatter(
            x=latencies_percentile_by_timestamp["timestamp_bin"],
            y=latencies_percentile_by_timestamp["p50"],
            mode="lines+markers",
            name="P50",
            line=dict(shape="spline"),
            hovertemplate="%{y} ms",
        )
    )
    line_chart.add_trace(
        go.Scatter(
            x=latencies_percentile_by_timestamp["timestamp_bin"],
            y=latencies_percentile_by_timestamp["p90"],
            mode="lines+markers",
            name="P90",
            line=dict(shape="spline"),
            hovertemplate="%{y} ms",
        )
    )
    line_chart.add_trace(
        go.Scatter(
            x=latencies_percentile_by_timestamp["timestamp_bin"],
            y=latencies_percentile_by_timestamp["p95"],
            mode="lines+markers",
            name="P95",
            line=dict(shape="spline"),
            hovertemplate="%{y} ms",
        )
    )
    line_chart.add_trace(
        go.Scatter(
            x=latencies_percentile_by_timestamp["timestamp_bin"],
            y=latencies_percentile_by_timestamp["p99"],
            mode="lines+markers",
            name="P99",
            line=dict(shape="spline"),
            hovertemplate="%{y} ms",
        )
    )

    # Enable vertical hover line
    line_chart.update_layout(
        hovermode="x unified",
        hoverdistance=100,  # sensitivity of hover
        spikedistance=1000,
        xaxis=dict(
            title="Time",
            showspikes=True,
            spikecolor="grey",
            spikesnap="cursor",
            spikemode="across",
            showline=True,
        ),
        yaxis=dict(title="Latency (ms)"),
        title="Latency Percentiles (5s intervals)",
    )

    line_chart.update_layout(**chart_layout)

    return line_chart


@app.callback(
    Output("inferences-per-second-chart", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_inferences_per_second_chart(_):
    inference_latencies = collector.get_inference_latencies()

    if inference_latencies.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Waiting for transactions stream!",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20),
            align="center",
        )

        empty_fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        return empty_fig

    inference_latencies["timestamp_bin"] = inference_latencies[
        "timestamp"
    ].dt.floor(
        "10s"
    )  # bin per 10s

    inferences_per_second_by_timestamp = (
        inference_latencies.groupby(["timestamp_bin"])["latency"]
        .agg(
            ips=lambda x: len(x) / sum(x),
        )
        .reset_index(names="timestamp_bin")
    )

    line_chart = px.line(
        inferences_per_second_by_timestamp,
        x="timestamp_bin",
        y="ips",
        labels={
            "timestamp_bin": "Time",
            "ips": "Inferences Per Second (IPS)",
        },
        title="Inferences Per Second (5s intervals)",
        color_discrete_sequence=["#53dfe2"],
    )

    # Add markers to the line
    line_chart.update_traces(
        mode="lines+markers",
        hovertemplate="%{y}",
    )

    line_chart.update_layout(hovermode="x unified", **chart_layout)

    return line_chart


@app.callback(
    Output("latency-histogram", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_latency_histogram(_):
    inference_latencies = collector.get_inference_latencies()

    if inference_latencies.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Waiting for transactions stream!",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20),
            align="center",
        )

        empty_fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        return empty_fig

    inference_latencies["timestamp"] = pd.to_datetime(
        inference_latencies["timestamp"]
    )

    histogram = px.histogram(
        x=inference_latencies["latency"] * 1000,
        nbins=20,
        labels={"x": "Latency (ms)", "y": "Count"},
        title="Inference Latency Histogram",
        color_discrete_sequence=["#53dfe2"],
    )

    histogram.update_layout(**chart_layout)

    return histogram


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
