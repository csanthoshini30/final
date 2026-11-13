from __future__ import annotations

import base64
import hashlib
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from config.config import PROJECT_ROOT
from inference.inference import run_subsystem_inference

SYSTEMS = {
    "engine": {
        "label": "Engine",
        "files": [f"FD00{index}_test.txt" for index in range(1, 5)],
        "extensions": ["txt", "csv", "xlsx"],
    },
    "electrical": {
        "label": "Electrical",
        "files": ["electrical_test_1.csv", "electrical_test_2.csv"],
        "extensions": ["csv", "xlsx"],
    },
    "hydraulic": {
        "label": "Hydraulic",
        "files": ["hydraulic_test_1.csv", "hydraulic_test_2.csv"],
        "extensions": ["csv", "xlsx"],
    },
}


def _engine_variant(filename: str, selected_variant: str = "FD003") -> str:
    for variant in ("FD001", "FD002", "FD003", "FD004"):
        if variant in filename.upper():
            return variant
    return selected_variant


def _build_pdf_report(result: dict) -> bytes:
    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], textColor=colors.HexColor("#17324d")
    )
    story = [
        Paragraph("Aircraft Maintenance Prediction Report", title_style),
        Spacer(1, 0.2 * inch),
    ]
    health = result["health_score"]
    metrics = [
        ["System", result["system"].title()],
        ["Dataset", result["dataset"]],
        ["Rows analyzed", str(result["rows"])],
        ["Prediction windows sampled", str(result["sampled_windows"])],
        ["Health score", f"{health:.1f}%" if health is not None else "Not provided by the engine model"],
        ["Model RUL estimate", f"{result['rul']:.2f} model units"],
        ["Fault classification", result["fault"]],
        ["Fault confidence", f"{result['confidence']:.1f}%"],
        ["Anomaly detected in latest window", "Yes" if result["anomaly"] else "No"],
        ["Models loaded", ", ".join(result["models"])],
    ]
    table = Table(metrics, colWidths=[2.5 * inch, 4 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8eef3")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b7c3cc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([table, Spacer(1, 0.2 * inch)])
    if result["system"] == "engine":
        story.append(Paragraph(
            "The engine LSTM was trained on remaining-useful-life targets. Its output is reported as an LSTM RUL estimate, not as a health score.",
            styles["BodyText"],
        ))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(
        "Predictions are decision support and must be reviewed by qualified maintenance personnel.",
        styles["BodyText"],
    ))
    document.build(story)
    return output.getvalue()


def _run_analysis(system: str, source, filename: str, engine_variant: str = "FD003") -> None:
    try:
        with st.spinner(f"Loading {SYSTEMS[system]['label'].lower()} models and analyzing data..."):
            result = run_subsystem_inference(
                system,
                source,
                filename,
                engine_dataset=_engine_variant(filename, engine_variant),
            )
            st.session_state.apm_results[system] = result
            st.session_state.apm_reports[system] = _build_pdf_report(result)
    except Exception as exc:
        st.session_state.apm_results.pop(system, None)
        st.session_state.apm_reports.pop(system, None)
        st.error(f"Analysis failed: {exc}")


def _render_result(result: dict) -> None:
    health = result["health_score"]
    columns = st.columns(4)
    columns[0].metric("Health score", f"{health:.1f}%" if health is not None else "Not modeled")
    columns[1].metric("RUL estimate", f"{result['rul']:.2f} model units")
    columns[2].metric("Fault class", result["fault"])
    columns[3].metric("Fault confidence", f"{result['confidence']:.1f}%")
    if result["system"] == "engine":
        st.caption(
            f"Engine health is not reported: its LSTM was trained on RUL targets. "
            f"The separate LSTM RUL estimate is {result['lstm_rul_estimate']:.2f} model units."
        )

    positions = result["row_positions"]
    anomaly_scores = result["anomaly_scores"]
    if result["system"] == "engine":
        rul_figure = go.Figure()
        rul_figure.add_trace(go.Scatter(
            x=positions, y=result["rul_series"], mode="lines", name="Random Forest RUL",
            line={"color": "#35a7c8", "width": 2},
        ))
        if result["lstm_rul_series"] is not None:
            rul_figure.add_trace(go.Scatter(
                x=positions, y=result["lstm_rul_series"], mode="lines", name="LSTM RUL",
                line={"color": "#e08a3a", "width": 1.5, "dash": "dot"},
            ))
        anomaly_indices = [index for index, flag in enumerate(result["anomaly_flags"]) if flag]
        if anomaly_indices:
            rul_figure.add_trace(go.Scatter(
                x=[positions[index] for index in anomaly_indices],
                y=[result["rul_series"][index] for index in anomaly_indices],
                mode="markers", name="Anomaly windows",
                marker={"color": "#d94f4f", "size": 8, "symbol": "x"},
            ))
        rul_figure.update_layout(
            title="Engine life estimates over the test run",
            xaxis_title="Input row ending the window",
            yaxis_title="Remaining useful life (model units)",
            height=390,
            margin={"l": 15, "r": 15, "t": 50, "b": 20},
            legend={"orientation": "h", "y": -0.25},
        )
        st.plotly_chart(rul_figure, use_container_width=True)

        anomaly_figure = go.Figure(go.Scatter(
            x=positions, y=anomaly_scores, mode="lines",
            name="Reconstruction error", line={"color": "#c06c84"},
            fill="tozeroy", fillcolor="rgba(192, 108, 132, 0.16)",
        ))
        anomaly_figure.update_layout(
            title="Engine anomaly profile",
            xaxis_title="Input row ending the window",
            yaxis_title="Autoencoder reconstruction error",
            height=280,
            margin={"l": 15, "r": 15, "t": 50, "b": 20},
            showlegend=False,
        )
        st.plotly_chart(anomaly_figure, use_container_width=True)

    elif result["system"] == "electrical":
        sensor_frame = pd.DataFrame(result["feature_series"])
        correlation = sensor_frame.corr().fillna(0)
        for index in range(len(correlation)):
            correlation.iloc[index, index] = 1
        heatmap = go.Figure(go.Heatmap(
            z=correlation.to_numpy(),
            x=correlation.columns.tolist(),
            y=correlation.index.tolist(),
            zmin=-1,
            zmax=1,
            zmid=0,
            colorscale="RdBu",
            colorbar={"title": "Pearson r"},
            texttemplate="%{z:.2f}",
            hovertemplate="%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>",
        ))
        heatmap.update_layout(
            title="Electrical sensor correlation",
            height=390,
            margin={"l": 15, "r": 15, "t": 50, "b": 20},
        )
        st.plotly_chart(heatmap, use_container_width=True)

        health_distribution = go.Figure(go.Histogram(
            x=result["health_series"],
            nbinsx=20,
            marker={"color": "#35a7c8", "line": {"color": "#e5f4f8", "width": 1}},
        ))
        health_distribution.update_layout(
            title="Electrical predicted health distribution",
            xaxis_title="Predicted health (%)",
            yaxis_title="Sampled windows",
            height=280,
            margin={"l": 15, "r": 15, "t": 50, "b": 20},
            bargap=0.08,
        )
        st.plotly_chart(health_distribution, use_container_width=True)

    else:
        feature_series = result["feature_series"]
        names = list(feature_series)
        pressure_name = next((name for name in names if "pressure" in name.lower()), names[0])
        flow_name = next((name for name in names if "flow" in name.lower()), next((name for name in names if name != pressure_name), names[0]))
        hydraulic_figure = go.Figure(go.Scatter(
            x=feature_series[pressure_name],
            y=feature_series[flow_name],
            mode="markers",
            marker={
                "size": 8,
                "color": result["health_series"],
                "colorscale": "RdYlGn",
                "cmin": 0,
                "cmax": 100,
                "colorbar": {"title": "Health %"},
                "symbol": ["x" if flag else "circle" for flag in result["anomaly_flags"]],
                "line": {"width": 0.5, "color": "#263238"},
            },
            customdata=list(zip(positions, anomaly_scores)),
            hovertemplate=(
                f"{pressure_name}: %{{x:.2f}}<br>{flow_name}: %{{y:.2f}}"
                "<br>Input row: %{customdata[0]}<br>Anomaly score: %{customdata[1]:.5f}<extra></extra>"
            ),
            name="Sampled operating windows",
        ))
        hydraulic_figure.update_layout(
            title="Hydraulic pressure-flow operating envelope",
            xaxis_title=pressure_name,
            yaxis_title=flow_name,
            height=420,
            margin={"l": 15, "r": 15, "t": 50, "b": 20},
        )
        st.plotly_chart(hydraulic_figure, use_container_width=True)
        st.caption("Marker color represents predicted health; x markers identify autoencoder anomaly windows.")

    st.caption(
        f"Used {result['sampled_windows']} evenly spaced windows from {result['rows']} rows; "
        "the final window is included. Charts show model outputs, not fabricated component scores."
    )
    with st.expander("Latest input features"):
        st.dataframe(
            pd.DataFrame([result["latest_features"]]),
            use_container_width=True,
            hide_index=True,
        )


def _render_chatbot() -> None:
    st.subheader("Maintenance AI Assistant")
    if "apm_chat" not in st.session_state:
        st.session_state.apm_chat = []
    for message in st.session_state.apm_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask about engine, electrical, hydraulic, or maintenance procedures")
    if question:
        st.session_state.apm_chat.append({"role": "user", "content": question})
        try:
            manual_path = PROJECT_ROOT / "data" / "Damage Propagation Modeling.pdf"
            pages = [page.extract_text() or "" for page in PdfReader(str(manual_path)).pages] if manual_path.exists() else []
            words = [word.lower().strip(".,?!:;()") for word in question.split() if len(word) > 2]
            matches = [page for page in pages if any(word in page.lower() for word in words)]
            if matches:
                answer = " ".join(matches[:2])[:1200]
            else:
                answer = (
                    "I could not find a matching passage in the maintenance manual. "
                    "Try a more specific engine, electrical, hydraulic, pressure, temperature, or vibration question."
                )
        except Exception as exc:
            answer = f"The maintenance manual could not be read: {exc}"
        st.session_state.apm_chat.append({"role": "assistant", "content": answer})
        st.rerun()


def main(configure_page: bool = True) -> None:
    if configure_page:
        st.set_page_config(
            page_title="Aircraft Maintenance System",
            page_icon="✈️",
            layout="wide",
            initial_sidebar_state="expanded",
        )
    if "apm_results" not in st.session_state:
        st.session_state.apm_results = {}
    if "apm_reports" not in st.session_state:
        st.session_state.apm_reports = {}

    background_path = PROJECT_ROOT / "background.png"
    if background_path.exists():
        image = base64.b64encode(background_path.read_bytes()).decode("ascii")
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(7, 18, 30, .68), rgba(7, 18, 30, .82)),
                    url('data:image/png;base64,{image}');
                background-size: cover;
                background-attachment: fixed;
            }}
            .block-container {{ padding-top: 1.5rem; }}
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<style>.block-container {padding-top: 1.5rem;}</style>", unsafe_allow_html=True)

    st.markdown("# AIRCRAFT MAINTENANCE SYSTEM")
    st.caption("PREDICTIVE DIAGNOSTICS AND HEALTH MONITORING")

    with st.sidebar:
        st.header("Control Panel")
        for system, configuration in SYSTEMS.items():
            available = [
                filename for filename in configuration["files"]
                if (PROJECT_ROOT / "data" / system / filename).is_file()
            ]
            st.subheader(configuration["label"])
            if not available:
                st.warning(f"No sample test data is available for {configuration['label'].lower()}.")
                continue
            selected = st.selectbox(
                f"{configuration['label']} test dataset",
                available,
                key=f"{system}_sample_file",
                label_visibility="collapsed",
            )
            if st.button(f"Analyze {configuration['label']}", key=f"{system}_sample_analyze", use_container_width=True):
                _run_analysis(
                    system,
                    PROJECT_ROOT / "data" / system / selected,
                    selected,
                    _engine_variant(selected),
                )

    tabs = st.tabs(["Engine Analysis", "Electrical Analysis", "Hydraulic Analysis"])
    for (system, configuration), tab in zip(SYSTEMS.items(), tabs):
        with tab:
            st.subheader(f"{configuration['label']} data")
            uploaded = st.file_uploader(
                f"Upload {configuration['label'].lower()} data",
                type=configuration["extensions"],
                key=f"{system}_upload",
            )
            engine_variant = "FD003"
            if system == "engine" and uploaded:
                name_variant = _engine_variant(uploaded.name, "")
                if name_variant == "":
                    engine_variant = st.selectbox(
                        "Choose the matching trained engine model",
                        ["FD001", "FD002", "FD003", "FD004"],
                        key="uploaded_engine_variant",
                    )
                else:
                    engine_variant = name_variant
            if uploaded and st.button(f"Analyze uploaded {configuration['label'].lower()} data", key=f"{system}_upload_analyze"):
                _run_analysis(system, uploaded, uploaded.name, engine_variant)

            result = st.session_state.apm_results.get(system)
            if result:
                st.markdown(f"### {configuration['label']} prediction results")
                _render_result(result)
                report = st.session_state.apm_reports.get(system)
                if report:
                    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        "Download analysis report (PDF)",
                        data=report,
                        file_name=f"{system}_analysis_{stamp}.pdf",
                        mime="application/pdf",
                        key=f"{system}_report_download",
                    )
            else:
                st.info("Choose a sample dataset in the control panel or upload data, then run an analysis.")

    st.divider()
    _render_chatbot()


if __name__ == "__main__":
    main()
