from __future__ import annotations

import logging

import dash
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html

from point import Point

logger = logging.getLogger(__name__)

_INTERVAL_MS = 100
_MAP_STYLE = "open-street-map"


class Visualizer:

    def __init__(self, records: list[Point]) -> None:
        self._records = records
        self._n = len(records)
        # separate info to lists by row values
        self._lats = [r.lat for r in records]
        self._lons = [r.lon for r in records]
        self._times = [r.time for r in records]
        # create the app
        self.app = dash.Dash(__name__, title="GPS Track Visualiser")
        self.app.layout = self._build_layout()
        self._register_callbacks()

    def run(self, debug: bool = False, port: int = 8050) -> None:
        # start app
        logger.info("Starting app at http://localhost:%d", port)
        self.app.run(debug=debug, port=port)

    def _build_layout(self) -> html.Div:
        anomaly_indices = [i for i, r in enumerate(self._records) if r.is_anomaly]

        return html.Div(style={"maxWidth": "960px", "margin": "0 auto", "padding": "24px",
                               "fontFamily": "sans-serif"},
                        children=[
                            # header
                            html.H2("GPS Track Visualiser", style={"marginBottom": "4px"}),
                            html.Hr(),

                            # map
                            dcc.Graph(
                                id="map",
                                figure=self._build_initial_figure(anomaly_indices),
                                style={"height": "500px", "borderRadius": "8px",
                                       "border": "1px solid #ddd"},
                                config={"scrollZoom": True},
                            ),

                            # time slider
                            html.Div(style={"marginTop": "16px"}, children=[
                                html.Label("Timeline:", style={"fontWeight": "bold"}),
                                dcc.Slider(
                                    id="frame-slider",
                                    min=0, max=self._n - 1, step=1, value=0,
                                    marks={
                                        0: f"{self._times[0]:.0f}s",
                                        self._n - 1: f"{self._times[-1]:.0f}s",
                                    },
                                    tooltip={"placement": "bottom", "always_visible": False},
                                ),
                            ]),

                            html.Div(style={"marginTop": "12px", "display": "flex",
                                            "gap": "16px", "alignItems": "center"},
                                     children=[
                                         # play button
                                         html.Button("▶ Play", id="play-pause-btn", n_clicks=0,
                                                     style={"padding": "8px 20px", "fontSize": "1rem",
                                                            "cursor": "pointer"}),
                                         html.Label("Speed:"),
                                         # x1 , x2, x5 speed control
                                         dcc.Dropdown(
                                             id="speed-selector",
                                             options=[{"label": "1×", "value": 1},
                                                      {"label": "2×", "value": 2},
                                                      {"label": "5×", "value": 5}],
                                             value=1, clearable=False,
                                             style={"width": "80px"},
                                         ),
                                     ],
                                     ),

                            # Info row
                            html.Div(style={"marginTop": "12px", "display": "flex",
                                            "gap": "24px", "fontSize": "0.95rem"},
                                     # time, speed and alt display
                                     children=[
                                         html.Span(["⏱ Time: ",
                                                    html.B(id="time-display", children=f"{self._times[0]:.1f} s")]),
                                         html.Span(["🚗 Speed: ", html.B(id="speed-display", children="—")]),
                                         html.Span(["⛰ Alt: ", html.B(id="alt-display", children="—")]),
                                         html.Span(id="anomaly-display"),
                                     ],
                                     ),

                            dcc.Store(id="playing-store", data=False),
                            dcc.Interval(id="animation-interval",
                                         interval=_INTERVAL_MS, disabled=True),
                        ],
                        )

    def _build_initial_figure(self, anomaly_indices: list[int]) -> go.Figure:
        # builds the map with the initial car position
        traces: list[go.BaseTraceType] = [
            self._make_full_track_trace(),
            self._make_car_marker_trace(0),
        ]
        if anomaly_indices:
            traces.append(self._make_anomaly_trace(anomaly_indices))

        centre_lat = sum(self._lats) / self._n
        centre_lon = sum(self._lons) / self._n

        fig = go.Figure(data=traces)
        fig.update_layout(
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            showlegend=False,
            mapbox=dict(style=_MAP_STYLE,
                        center={"lat": centre_lat, "lon": centre_lon},
                        zoom=13),
        )
        return fig

    def _make_full_track_trace(self) -> go.Scattermapbox:
        # draw the car's path
        return go.Scattermapbox(
            lat=self._lats, lon=self._lons,
            mode="lines",
            line={"color": "#888", "width": 2},
            hoverinfo="skip",
        )

    def _make_car_marker_trace(self, idx: int) -> go.Scattermapbox:
        # places car's marker at current location
        r = self._records[idx]
        return go.Scattermapbox(
            lat=[r.lat], lon=[r.lon],
            mode="markers",
            marker={"size": 14, "color": "red"},
            hovertemplate=(
                f"<b>Time:</b> {r.time:.1f} s<br>"
                f"<b>Speed:</b> {r.speed_mps * 3.6:.1f} km/h<br>"
                f"<b>Alt:</b> {r.alt:.1f} m<extra></extra>"
            ),
        )

    def _make_anomaly_trace(self, indices: list[int]) -> go.Scattermapbox:
        # color anomalous points orange
        return go.Scattermapbox(
            lat=[self._lats[i] for i in indices],
            lon=[self._lons[i] for i in indices],
            mode="markers",
            marker={"size": 10, "color": "orange"},
            hovertemplate="⚠ Anomalous point<extra></extra>",
        )

    def _register_callbacks(self) -> None:

        @self.app.callback(
            Output("playing-store", "data"),
            Output("play-pause-btn", "children"),
            Output("animation-interval", "disabled"),
            Input("play-pause-btn", "n_clicks"),
            State("playing-store", "data"),
            prevent_initial_call=True,
        )
        def toggle_playback(n_clicks: int, playing: bool):
            # toggle for play/pause button
            now_playing = not playing
            label = "⏸ Pause" if now_playing else "▶ Play"
            return now_playing, label, not now_playing

        @self.app.callback(
            Output("frame-slider", "value"),
            Input("animation-interval", "n_intervals"),
            State("frame-slider", "value"),
            State("speed-selector", "value"),
            State("playing-store", "data"),
            prevent_initial_call=True,
        )
        def advance_frame(n_intervals: int, current_idx: int,
                          speed: int, playing: bool) -> int:
            # returns new car location
            if not playing:
                return current_idx
            return min(current_idx + speed, self._n - 1)

        @self.app.callback(
            Output("map", "figure"),
            Output("time-display", "children"),
            Output("speed-display", "children"),
            Output("alt-display", "children"),
            Output("anomaly-display", "children"),
            Input("frame-slider", "value"),
            State("map", "figure"),
        )
        def update_frame(idx: int, current_figure: dict) -> tuple:
            # move the car marker to the updated location
            r = self._records[idx]
            current_figure["data"][1]["lat"] = [r.lat]
            current_figure["data"][1]["lon"] = [r.lon]
            anomaly = "⚠️ Anomaly" if r.is_anomaly else ""
            return (
                current_figure,
                f"{r.time:.1f} s",
                f"{r.speed_mps * 3.6:.1f} km/h",
                f"{r.alt:.1f} m",
                anomaly,
            )
