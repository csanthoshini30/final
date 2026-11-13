"""
Aircraft Predictive Maintenance System - Premium Streamlit Dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.engine_agent import EngineAgent
from agents.electrical_agent import ElectricalAgent
from agents.hydraulic_agent import HydraulicAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.rag_agent import RAGMaintenanceAgent

# Page configuration
st.set_page_config(
    page_title="Aircraft Maintenance System",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for aerospace theme
st.markdown("""
    <style>
    :root {
        --primary-color: #0066cc;
        --secondary-color: #001a4d;
        --accent-color: #00ccff;
        --danger-color: #ff4444;
        --warning-color: #ffaa00;
        --success-color: #00dd44;
    }

    .main {
        background: linear-gradient(135deg, #001a4d 0%, #003366 100%);
        color: #ffffff;
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(0, 102, 204, 0.1);
        border-radius: 10px;
        padding: 5px;
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(0, 102, 204, 0.2), rgba(0, 204, 255, 0.1));
        border-left: 4px solid #00ccff;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }

    .health-critical {
        color: #ff4444;
        font-weight: bold;
    }

    .health-warning {
        color: #ffaa00;
        font-weight: bold;
    }

    .health-good {
        color: #00dd44;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize agents
@st.cache_resource
def load_agents():
    """Load all agents"""
    engine_agent = EngineAgent()
    electrical_agent = ElectricalAgent()
    hydraulic_agent = HydraulicAgent()
    coordinator_agent = CoordinatorAgent(engine_agent, electrical_agent, hydraulic_agent)
    rag_agent = RAGMaintenanceAgent()
    return {
        'engine': engine_agent,
        'electrical': electrical_agent,
        'hydraulic': hydraulic_agent,
        'coordinator': coordinator_agent,
        'rag': rag_agent
    }

def create_gauge_chart(value, max_value=100, title="Health Score"):
    """Create a gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': 80},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 33], 'color': "rgba(255, 68, 68, 0.2)"},
                {'range': [33, 66], 'color': "rgba(255, 170, 0, 0.2)"},
                {'range': [66, 100], 'color': "rgba(0, 221, 68, 0.2)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 2},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=300
    )
    return fig

def get_health_color(health_score):
    """Get color based on health score"""
    if health_score >= 80:
        return "🟢 Healthy"
    elif health_score >= 60:
        return "🟡 Degraded"
    else:
        return "🔴 Faulty"

def generate_dummy_data():
    """Generate dummy sensor data for demonstration"""
    np.random.seed(42)
    seq_length = 30

    engine_data = np.random.randn(seq_length, 21) * 10 + 50  # 21 sensor channels
    electrical_data = np.random.randn(seq_length, 10) * 5 + 50  # 10 feature channels
    hydraulic_data = np.random.randn(seq_length, 10) * 8 + 50  # 10 feature channels

    return engine_data, electrical_data, hydraulic_data

def main():
    """Main dashboard function"""

    # Header
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
        <h1 style='color: #00ccff; text-shadow: 0 0 10px rgba(0, 204, 255, 0.5);'>
            ✈️ AIRCRAFT PREDICTIVE MAINTENANCE SYSTEM
        </h1>
        <p style='color: #cccccc; font-size: 14px;'>
            Real-time Health Monitoring & Predictive Analytics
        </p>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Load agents
    agents = load_agents()

    # Sidebar
    st.sidebar.markdown("""
        <div style='text-align: center; padding: 15px; background: rgba(0, 102, 204, 0.2); border-radius: 10px;'>
        <h3 style='color: #00ccff;'>⚙️ SYSTEM CONTROL</h3>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.divider()

    # Generate or upload data option
    data_source = st.sidebar.radio(
        "Data Source",
        ["Generate Demo Data", "Upload CSV", "Real-time Stream"],
        key="data_source"
    )

    st.sidebar.divider()

    # Generate demo data
    if data_source == "Generate Demo Data":
        engine_data, electrical_data, hydraulic_data = generate_dummy_data()

        # Get diagnostics
        engine_result = agents['engine'].diagnose(engine_data[np.newaxis, :, :])
        electrical_result = agents['electrical'].diagnose(electrical_data[np.newaxis, :, :])
        hydraulic_result = agents['hydraulic'].diagnose(hydraulic_data[np.newaxis, :, :])

        # Get coordinator assessment
        coordinator_result = agents['coordinator'].coordinate(
            engine_data[np.newaxis, :, :],
            electrical_data[np.newaxis, :, :],
            hydraulic_data[np.newaxis, :, :]
        )

        # Overall Aircraft Status Tab
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🛩️ Aircraft Overview",
            "🔧 Engine Diagnostics",
            "⚡ Electrical Diagnostics",
            "🔷 Hydraulic Diagnostics",
            "📋 Maintenance Guidance"
        ])

        # Tab 1: Aircraft Overview
        with tab1:
            st.markdown("<h2 style='color: #00ccff;'>🛩️ AIRCRAFT STATUS</h2>", unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Overall Health",
                    f"{coordinator_result['overall_health']}%" if coordinator_result['overall_health'] else "N/A",
                    delta="↓ 5%" if coordinator_result['overall_health'] else None
                )

            with col2:
                st.metric(
                    "Risk Level",
                    coordinator_result['overall_risk'],
                    delta="Normal" if coordinator_result['overall_risk'] == "Normal" else None
                )

            with col3:
                st.metric(
                    "Priority Action",
                    coordinator_result['priority'],
                    delta="Check Systems"
                )

            with col4:
                st.metric(
                    "Active Alerts",
                    len(coordinator_result['recommendations']),
                    delta="+1"
                )

            st.divider()

            # Subsystem health overview
            st.markdown("<h3 style='color: #00ccff;'>Subsystem Health Overview</h3>", unsafe_allow_html=True)

            subsystem_data = {
                'Subsystem': ['Engine', 'Electrical', 'Hydraulic'],
                'Health': [
                    engine_result['health_score'] or 0,
                    electrical_result['health_score'] or 0,
                    hydraulic_result['health_score'] or 0
                ],
                'Risk': [engine_result['risk'], electrical_result['risk'], hydraulic_result['risk']]
            }

            fig = go.Figure(data=[
                go.Bar(
                    x=subsystem_data['Subsystem'],
                    y=subsystem_data['Health'],
                    marker=dict(
                        color=['#FF6B6B', '#4ECDC4', '#45B7D1'],
                        line=dict(color='#00ccff', width=2)
                    )
                )
            ])

            fig.update_layout(
                title="Subsystem Health Scores",
                yaxis_title="Health Score (%)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                height=350
            )

            st.plotly_chart(fig, use_container_width=True)

            # Subsystem ranking
            st.markdown("<h3 style='color: #00ccff;'>Subsystem Priority Ranking</h3>", unsafe_allow_html=True)

            for i, subsystem in enumerate(coordinator_result['ranked_subsystems'], 1):
                if subsystem == 'Engine':
                    health = engine_result['health_score']
                    risk = engine_result['risk']
                elif subsystem == 'Electrical':
                    health = electrical_result['health_score']
                    risk = electrical_result['risk']
                else:
                    health = hydraulic_result['health_score']
                    risk = hydraulic_result['risk']

                st.markdown(f"""
                    <div style='background: rgba(0, 102, 204, 0.15); border-left: 4px solid #00ccff; padding: 15px; margin: 10px 0; border-radius: 5px;'>
                    <p><strong>#{i}: {subsystem}</strong> - Health: {health}% | Risk: {risk}</p>
                    </div>
                """, unsafe_allow_html=True)

            # Recommendations
            st.markdown("<h3 style='color: #00ccff;'>⚠️ MAINTENANCE RECOMMENDATIONS</h3>", unsafe_allow_html=True)

            for rec in coordinator_result['recommendations'][:5]:
                priority_color = {
                    'Critical': '#ff4444',
                    'High': '#ffaa00',
                    'Medium': '#ffdd00',
                    'Low': '#00dd44'
                }.get(rec.get('priority', 'Low'), '#cccccc')

                st.markdown(f"""
                    <div style='background: rgba(0, 102, 204, 0.1); border-left: 4px solid {priority_color}; padding: 15px; margin: 10px 0; border-radius: 5px;'>
                    <p style='color: {priority_color}; font-weight: bold;'>[{rec.get('priority', 'N/A')}] {rec.get('subsystem', 'System')}</p>
                    <p>{rec.get('action', 'N/A')}</p>
                    </div>
                """, unsafe_allow_html=True)

        # Tab 2: Engine Diagnostics
        with tab2:
            st.markdown("<h2 style='color: #FF6B6B;'>🔧 ENGINE DIAGNOSTICS</h2>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.plotly_chart(
                    create_gauge_chart(engine_result['health_score'] or 0, title="Engine Health"),
                    use_container_width=True
                )

            with col2:
                st.markdown("<h3>Engine Status</h3>", unsafe_allow_html=True)
                st.markdown(f"<p>Fault: <strong>{engine_result['fault']}</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p>Risk Level: <strong>{engine_result['risk']}</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p>RUL: <strong>{engine_result['rul']} hours</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p>Anomaly Detected: <strong>{'Yes' if engine_result['anomaly'] else 'No'}</strong></p>", unsafe_allow_html=True)

            # Engine trends
            st.markdown("<h3>Trend Analysis</h3>", unsafe_allow_html=True)

            trend_data = pd.DataFrame({
                'Time': range(30),
                'Engine_Health': np.cumsum(np.random.randn(30) * 2) + 75,
                'Engine_Temperature': np.cumsum(np.random.randn(30) * 1.5) + 85,
                'Engine_Vibration': np.cumsum(np.random.randn(30) * 0.5) + 10
            })

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=trend_data['Time'], y=trend_data['Engine_Health'],
                                    mode='lines+markers', name='Health Score',
                                    line=dict(color='#FF6B6B', width=2)))

            fig.update_layout(
                title="Engine Performance Trend",
                xaxis_title="Time (hours)",
                yaxis_title="Value",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                height=350
            )

            st.plotly_chart(fig, use_container_width=True)

        # Tab 3: Electrical Diagnostics
        with tab3:
            st.markdown("<h2 style='color: #4ECDC4;'>⚡ ELECTRICAL DIAGNOSTICS</h2>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.plotly_chart(
                    create_gauge_chart(electrical_result['health_score'] or 0, title="Electrical Health"),
                    use_container_width=True
                )

            with col2:
                st.markdown("<h3>Electrical Status</h3>", unsafe_allow_html=True)
                st.markdown(f"<p>Fault: <strong>{electrical_result['fault']}</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p>Risk Level: <strong>{electrical_result['risk']}</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p>RUL: <strong>{electrical_result['rul']} hours</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p>Anomaly Detected: <strong>{'Yes' if electrical_result['anomaly'] else 'No'}</strong></p>", unsafe_allow_html=True)

        # Tab 4: Hydraulic Diagnostics
        with tab4:
            st.markdown("<h2 style='color: #45B7D1;'>🔷 HYDRAULIC DIAGNOSTICS</h2>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.plotly_chart(
                    create_gauge_chart(hydraulic_result['health_score'] or 0, title="Hydraulic Health"),
                    use_container_width=True
                )

            with col2:
                st.markdown("<h3>Hydraulic Status</h3>", unsafe_allow_html=True)
                st.markdown(f"<p>Fault: <strong>{hydraulic_result['fault']}</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p>Risk Level: <strong>{hydraulic_result['risk']}</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p>RUL: <strong>{hydraulic_result['rul']} hours</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p>Anomaly Detected: <strong>{'Yes' if hydraulic_result['anomaly'] else 'No'}</strong></p>", unsafe_allow_html=True)

        # Tab 5: Maintenance Guidance
        with tab5:
            st.markdown("<h2 style='color: #FFD700;'>📋 RAG MAINTENANCE GUIDANCE</h2>", unsafe_allow_html=True)

            # Select subsystem for detailed guidance
            selected_subsystem = st.selectbox(
                "Select Subsystem",
                ["Engine", "Electrical", "Hydraulic"]
            )

            if selected_subsystem == "Engine":
                fault_info = {
                    'subsystem': 'Engine',
                    'fault': engine_result['fault']
                }
            elif selected_subsystem == "Electrical":
                fault_info = {
                    'subsystem': 'Electrical',
                    'fault': electrical_result['fault']
                }
            else:
                fault_info = {
                    'subsystem': 'Hydraulic',
                    'fault': hydraulic_result['fault']
                }

            # Generate RAG response
            rag_result = agents['rag'].search(fault_info)

            if rag_result['found']:
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown("<h3>Possible Causes</h3>", unsafe_allow_html=True)
                    for cause in rag_result['causes']:
                        st.markdown(f"• {cause}", help="Possible root cause")

                with col2:
                    st.markdown("<h3>Recommended Spare Parts</h3>", unsafe_allow_html=True)
                    for part in rag_result['spare_parts']:
                        st.markdown(f"• {part}", help="Required spare part")

                st.divider()

                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown("<h3>Inspection Procedures</h3>", unsafe_allow_html=True)
                    for proc in rag_result['inspection_procedures']:
                        st.markdown(f"• {proc}")

                with col2:
                    st.markdown("<h3>Corrective Actions</h3>", unsafe_allow_html=True)
                    for action in rag_result['corrective_actions']:
                        st.markdown(f"• {action}")

                st.divider()

                st.markdown("<h3>⚠️ Safety Considerations</h3>", unsafe_allow_html=True)
                for safety in rag_result['safety_considerations']:
                    st.warning(f"🔒 {safety}")
            else:
                st.info("⚠️ No specific guidance found for this fault. Consult maintenance manuals.")

    st.divider()

    # Footer
    st.markdown("""
        <div style='text-align: center; padding: 20px; color: #666666; font-size: 12px;'>
        Aircraft Predictive Maintenance System v1.0 | Powered by AI/ML | Last Updated: """ +
        datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
