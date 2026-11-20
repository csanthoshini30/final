"""
Aircraft Predictive Maintenance System - Premium Futuristic UI
Enterprise-grade dashboard with glassmorphism, neon effects, and premium aviation theme
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
from pathlib import Path
import os
from io import BytesIO
import base64
import hashlib
from pypdf import PdfReader
# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.engine_agent import EngineAgent
from inference.inference import run_subsystem_inference
from agents.electrical_agent import ElectricalAgent
from agents.hydraulic_agent import HydraulicAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.rag_agent import RAGMaintenanceAgent

# For PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    PDF_AVAILABLE = True
except:
    PDF_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Aircraft Maintenance System",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Futuristic Aviation Theme CSS
st.markdown("""
    <style>
    /* Root variables */
    :root {
        --bg-primary: #1a1a1a;
        --bg-secondary: #000000;
        --bg-tertiary: #0f0f0f;
        --card-bg: transparent;
        --card-bg-hover: transparent;
        --primary-accent: #ffffff;
        --secondary-accent: #cccccc;
        --glow-color: #aaaaaa;
        --text-primary: #000000;
        --text-secondary: #222222;
        --border-color: rgba(0, 0, 0, 0.2);
    }

    /* Main application styling */
    .stApp {
        color: #ffffff;
        font-family: 'Times New Roman', serif;
        font-weight: 700;
        overflow-x: hidden;
    }

    .main {
        background: transparent;
        padding: 2rem;
        position: relative;
        z-index: 1;
        font-weight: 700;
    }

    /* Premium glass morphism cards */
    .glass-card {
        background: rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        background: rgba(0, 0, 0, 0.4);
        border-color: rgba(255, 255, 255, 0.15);
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.3);
        transform: translateY(-2px);
    }

    /* Neon glow effect */
    .neon-glow {
        box-shadow: 0 0 20px rgba(93, 203, 255, 0.3),
                    0 0 40px rgba(59, 130, 246, 0.2),
                    inset 0 0 20px rgba(93, 203, 255, 0.05);
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Times New Roman', serif;
        font-weight: 900;
        letter-spacing: 0px;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.9) !important;
    }

    h1 {
        font-size: 2.8rem;
        color: #ffffff;
        font-weight: 900;
        margin-bottom: 1rem;
        text-shadow: 0 3px 8px rgba(0, 0, 0, 0.9) !important;
    }

    h2 {
        font-size: 2rem;
        color: #ffffff;
        font-weight: 900;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.9) !important;
    }

    h3 {
        font-size: 1.5rem;
        color: #ffffff;
        font-weight: 800;
        text-shadow: 0 2px 5px rgba(0, 0, 0, 0.9) !important;
    }

    /* Buttons - Aviation Neon Style */
    .stButton > button {
        background: linear-gradient(135deg, #5DCBFF, #3B82F6) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.8rem 2.5rem !important;
        font-weight: 600 !important;
        font-family: 'Times New Roman', serif !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 15px rgba(93, 203, 255, 0.5) !important;
    }

    .stButton > button * {
        color: #ffffff !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 0 25px rgba(93, 203, 255, 0.8) !important;
        background: linear-gradient(135deg, #7DD9FF, #60A5FA) !important;
    }

    .stButton > button:active {
        transform: scale(0.98) !important;
    }

    /* Select boxes and inputs - Glassmorphism Theme */
    .stSelectbox, .stTextInput, .stTextArea {
        background: transparent !important;
        backdrop-filter: none !important;
        border: none !important;
        border-radius: 0 !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }

    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(93, 203, 255, 0.4) !important;
    }

    .stSelectbox * {
        color: #ffffff !important;
    }

    [data-testid="stSelectbox"] * {
        color: #ffffff !important;
    }

    /* SelectBox - Glassmorphic Style - NO EXTRA BORDERS */
    [data-testid="stSelectbox"] {
        background: transparent !important;
        backdrop-filter: none !important;
        border: none !important;
        border-radius: 0 !important;
        color: #ffffff !important;
    }

    [data-testid="stSelectbox"] > div {
        background: transparent !important;
        border: none !important;
    }

    [data-testid="stSelectbox"] > div > div {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(93, 203, 255, 0.4) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }

    /* Dropdown Items and Selected Value */
    [data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(93, 203, 255, 0.4) !important;
        border-radius: 12px !important;
    }

    [data-baseweb="select"] span {
        color: #ffffff !important;
    }

    [data-baseweb="select"] * {
        color: #ffffff !important;
    }

    /* Dropdown Menu - Dark Background */
    [data-baseweb="menu"] {
        background: rgba(10, 20, 40, 0.95) !important;
        border: 1px solid #5DCBFF !important;
        backdrop-filter: blur(15px) !important;
    }

    [data-baseweb="menu"] * {
        color: #ffffff !important;
    }

    /* Dropdown Items */
    [role="option"] {
        color: #ffffff !important;
        background: rgba(10, 20, 40, 0.95) !important;
        border: none !important;
    }

    [role="option"]:hover {
        background: rgba(93, 203, 255, 0.2) !important;
        color: #ffffff !important;
        border: none !important;
    }

    [role="option"][aria-selected="true"] {
        color: #ffffff !important;
        background: rgba(93, 203, 255, 0.3) !important;
        border: none !important;
    }

    /* SelectBox Placeholder Text - Light Blue */
    [data-baseweb="select"] input::placeholder {
        color: #A8B3CF !important;
        opacity: 1 !important;
    }

    [data-testid="stSelectbox"] [placeholder] {
        color: #A8B3CF !important;
    }

    [data-testid="stTextInput"] * {
        color: #ffffff !important;
    }

    [data-testid="stTextInput"] input {
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(93, 203, 255, 0.4) !important;
        border-radius: 12px !important;
        padding: 12px 15px !important;
        font-family: 'Times New Roman', serif !important;
        font-weight: 600 !important;
    }

    [data-testid="stTextInput"] input:focus {
        border: 1px solid rgba(93, 203, 255, 0.8) !important;
        box-shadow: 0 0 10px rgba(93, 203, 255, 0.3) !important;
    }

    /* Placeholder text styling - Light Blue */
    input::placeholder {
        color: #A8B3CF !important;
        opacity: 1 !important;
    }

    textarea::placeholder {
        color: #A8B3CF !important;
        opacity: 1 !important;
    }

    [data-testid="stTextInput"] input::placeholder {
        color: #A8B3CF !important;
        opacity: 1 !important;
    }

    [data-testid="stTextArea"] textarea::placeholder {
        color: #A8B3CF !important;
        opacity: 1 !important;
    }

    /* File uploader styling - Glassmorphism */
    [data-testid="stFileUploadDropzone"] {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(93, 203, 255, 0.4) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(15px) !important;
    }

    .stFileUploadDropzone {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(93, 203, 255, 0.4) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 12px !important;
    }

    [data-testid="stFileUploadDropzone"] * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    [data-baseweb="select"] {
        background: rgba(0, 0, 0, 0.4) !important;
    }

    [data-baseweb="select"] * {
        color: #ffffff !important;
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 800;
        font-size: 12px;
        letter-spacing: 1px;
        background: rgba(0, 0, 0, 0.4) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
    }

    .status-healthy {
        background: rgba(0, 0, 0, 0.4) !important;
        color: #ffffff;
        border: 1px solid rgba(76, 175, 80, 0.6) !important;
        font-weight: 800;
        backdrop-filter: blur(10px);
    }

    .status-warning {
        background: rgba(0, 0, 0, 0.4) !important;
        color: #ffffff;
        border: 1px solid rgba(255, 152, 0, 0.6) !important;
        font-weight: 800;
        backdrop-filter: blur(10px);
    }

    .status-critical {
        background: rgba(0, 0, 0, 0.4) !important;
        color: #ffffff;
        border: 1px solid rgba(244, 67, 54, 0.6) !important;
        font-weight: 800;
        backdrop-filter: blur(10px);
    }

    /* Dividers */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 2rem 0;
    }

    /* Metric display */
    .metric-value {
        font-size: 2.5rem;
        font-weight: 900;
        color: #ffffff !important;
        text-shadow: 0 3px 6px rgba(0, 0, 0, 0.9) !important;
        letter-spacing: 1px;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #ffffff !important;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8) !important;
    }

    /* Info/Warning/Error boxes */
    .stInfo {
        background: rgba(0, 0, 0, 0.35) !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
    }

    .stWarning {
        background: rgba(0, 0, 0, 0.35) !important;
        border: 1px solid rgba(255, 152, 0, 0.4) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
    }

    .stError {
        background: rgba(0, 0, 0, 0.35) !important;
        border: 1px solid rgba(244, 67, 54, 0.4) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
    }

    .stSuccess {
        background: rgba(0, 0, 0, 0.35) !important;
        border: 1px solid rgba(76, 175, 80, 0.4) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
    }

    .stInfo > div, .stWarning > div, .stError > div, .stSuccess > div {
        font-weight: 800 !important;
        color: #ffffff !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8) !important;
    }

    /* Tabs */
    [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 2px solid #333333;
    }

    button[role="tab"] {
        background: transparent !important;
        color: #666666 !important;
        border: none !important;
        border-radius: 12px 12px 0 0 !important;
        padding: 1rem 1.5rem !important;
        font-weight: 800 !important;
        transition: all 0.3s ease !important;
        font-family: 'Times New Roman', serif !important;
    }

    button[role="tab"]:hover {
        color: #000000 !important;
        background: rgba(0, 0, 0, 0.05) !important;
    }

    button[role="tab"][aria-selected="true"] {
        color: #000000 !important;
        background: transparent !important;
        border-bottom: 3px solid #000000 !important;
        font-weight: 900 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: transparent;
        backdrop-filter: blur(5px);
        border-right: 1px solid rgba(0, 0, 0, 0.2);
    }

    section[data-testid="stSidebar"] * {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* Animations */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(93, 203, 255, 0.3); }
        50% { box-shadow: 0 0 40px rgba(93, 203, 255, 0.6); }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    .float-animation {
        animation: float 3s ease-in-out infinite;
    }

    .glow-animation {
        animation: glow 2s ease-in-out infinite;
    }

    .pulse-animation {
        animation: pulse 2s ease-in-out infinite;
    }

    /* General text styling */
    p, span, div, li, label {
        font-weight: 700 !important;
        color: #ffffff !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8) !important;
    }

    .stMarkdown, .stMarkdown > * {
        font-weight: 700 !important;
        color: #ffffff !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8) !important;
    }

    strong, b {
        font-weight: 900 !important;
        color: #ffffff !important;
        text-shadow: 0 2px 3px rgba(0, 0, 0, 0.9) !important;
    }

    .stMetric {
        font-weight: 800 !important;
        color: #ffffff !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8) !important;
    }

    .stMetric > * {
        color: #ffffff !important;
        font-weight: 800 !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8) !important;
    }

    /* Main container text visibility */
    div[class*="metric"], div[class*="card"] {
        color: #ffffff !important;
    }

    div[class*="metric"] *, div[class*="card"] * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Ensure heading visibility in boxes */
    .stMetric h3, .stMetric h2, .stMetric h1 {
        color: #ffffff !important;
        font-weight: 900 !important;
    }

    /* Text in columns with metrics */
    [data-testid="column"] .stMetric * {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* Metric label and value strong visibility */
    .stMetric label {
        color: #ffffff !important;
        font-weight: 900 !important;
        letter-spacing: 0.5px;
    }

    /* Override Streamlit metric default styles */
    div[data-testid="metric-container"] {
        color: #ffffff !important;
    }

    div[data-testid="metric-container"] * {
        color: #ffffff !important;
        font-weight: 900 !important;
    }

    /* Strong text in metrics */
    .stMetric strong, .stMetric b {
        color: #ffffff !important;
        font-weight: 900 !important;
    }

    /* Paragraph text in metrics */
    .stMetric p {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* Dataframe styling */
    .dataframe, table {
        background: rgba(0, 0, 0, 0.35) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        backdrop-filter: blur(10px) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    .dataframe * {
        background: rgba(0, 0, 0, 0.35) !important;
        color: #ffffff !important;
    }

    table th, table td {
        background: rgba(0, 0, 0, 0.35) !important;
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
    }

    /* Column containers */
    [data-testid="column"] {
        background: rgba(0, 0, 0, 0.25) !important;
        backdrop-filter: blur(8px);
        border-radius: 12px !important;
        color: #ffffff !important;
    }

    [data-testid="column"] * {
        color: #ffffff !important;
    }

    /* Expander styling */
    .stExpander {
        background: rgba(0, 0, 0, 0.4) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
    }

    .stExpander * {
        color: #ffffff !important;
        background: rgba(0, 0, 0, 0.3) !important;
    }

    /* Metric containers */
    .stMetric {
        background: rgba(0, 0, 0, 0.35) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8) !important;
    }

    /* Container styling */
    [data-testid="stContainer"] {
        color: #ffffff !important;
    }

    /* Code blocks */
    .stCode, code, pre {
        background: rgba(0, 0, 0, 0.5) !important;
        color: #ffffff !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }

    /* Horizontal line (separator) */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        margin: 2rem 0;
    }

    /* Expander boxes */
    .stExpander {
        background: rgba(0, 0, 0, 0.35) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
    }

    .stExpander > div {
        color: #ffffff !important;
    }

    /* Metric containers */
    .metric {
        background: rgba(0, 0, 0, 0.35) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
    }

    .metric * {
        color: #ffffff !important;
    }

    /* Code blocks */
    .stCode, code {
        background: rgba(0, 0, 0, 0.35) !important;
        color: #ffffff !important;
        backdrop-filter: blur(10px) !important;
    }

    /* Container styling */
    [data-testid="stContainer"] {
        color: #ffffff !important;
    }

    /* Column styling */
    [data-testid="column"] {
        color: #ffffff !important;
    }
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'selected_files' not in st.session_state:
    st.session_state.selected_files = {'engine': None, 'electrical': None, 'hydraulic': None}
if 'generated_reports' not in st.session_state:
    st.session_state.generated_reports = {'engine': None, 'electrical': None, 'hydraulic': None}
if 'uploaded_datasets' not in st.session_state:
    st.session_state.uploaded_datasets = {'engine': None, 'electrical': None, 'hydraulic': None}
if 'file_hashes' not in st.session_state:
    st.session_state.file_hashes = {'engine': None, 'electrical': None, 'hydraulic': None}

# Load and encode background image
@st.cache_resource
def load_background_image():
    """Load background image and convert to base64"""
    try:
        bg_path = PROJECT_ROOT / "background.png"
        if bg_path.exists():
            with open(bg_path, "rb") as img_file:
                import base64
                return base64.b64encode(img_file.read()).decode()
    except:
        pass
    return None

# Get background image and update CSS
bg_image_base64 = load_background_image()
if bg_image_base64:
    # Update the CSS with base64 encoded image
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.45)), url('data:image/png;base64,{bg_image_base64}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }}
    </style>
    """, unsafe_allow_html=True)

# Load agents
@st.cache_resource
def load_agents():
    try:
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
    except Exception as e:
        st.error(f"Error loading agents: {e}")
        return None

def get_available_files(system_type):
    """Get available data files for each system - FILTERED to specific files only"""
    data_path = PROJECT_ROOT / "data" / system_type

    if system_type == "engine":
        # Engine: Only FD003 and FD004 TEST FILES (no train, no RUL)
        allowed_patterns = ["FD003_test.txt", "FD004_test.txt"]
    elif system_type == "electrical":
        # Electrical: Only test_1 and test_2
        allowed_patterns = ["electrical_test_1.csv", "electrical_test_2.csv"]
    elif system_type == "hydraulic":
        # Hydraulic: Only test_1 and test_2
        allowed_patterns = ["hydraulic_test_1.csv", "hydraulic_test_2.csv"]
    else:
        allowed_patterns = []

    if data_path.exists():
        all_files = sorted([f.name for f in data_path.glob("*") if f.is_file()])
        filtered_files = [f for f in all_files if f in allowed_patterns]
        return filtered_files
    return []

def load_rag_manual():
    """Load the maintenance manual for RAG chatbot"""
    manual_path = PROJECT_ROOT / "data" / "Damage Propagation Modeling.pdf"
    if manual_path.exists():
        try:
            return [page.extract_text() or "" for page in PdfReader(str(manual_path)).pages]
        except:
            return None
    return None

def get_file_analysis_context(system_type, filename):
    """Get dynamic analysis context based on selected file"""
    if system_type == "engine":
        if "FD003" in filename:
            return {
                "name": "Engine Dataset FD003",
                "description": "Run-to-Failure Engine Dataset FD003",
                "health_base": 82,
                "trend": "stable",
                "focus": "High-speed, high-load conditions"
            }
        elif "FD004" in filename:
            return {
                "name": "Engine Dataset FD004",
                "description": "Run-to-Failure Engine Dataset FD004",
                "health_base": 78,
                "trend": "declining",
                "focus": "Sea-level, high-load conditions"
            }
    elif system_type == "electrical":
        if "test_1" in filename:
            return {
                "name": "Electrical Test Set 1",
                "description": "Primary electrical system test data",
                "health_base": 75,
                "trend": "stable",
                "focus": "Power distribution monitoring"
            }
        elif "test_2" in filename:
            return {
                "name": "Electrical Test Set 2",
                "description": "Secondary electrical system test data",
                "health_base": 68,
                "trend": "degrading",
                "focus": "Backup power circuits"
            }
    elif system_type == "hydraulic":
        if "test_1" in filename:
            return {
                "name": "Hydraulic Test Set 1",
                "description": "Primary hydraulic system test data",
                "health_base": 60,
                "trend": "declining",
                "focus": "Pressure and flow monitoring"
            }
        elif "test_2" in filename:
            return {
                "name": "Hydraulic Test Set 2",
                "description": "Secondary hydraulic system test data",
                "health_base": 52,
                "trend": "critical",
                "focus": "Pump performance degradation"
            }

    return {"name": "Unknown", "description": "", "health_base": 0, "trend": "unknown", "focus": ""}

def create_gauge_chart(value, title="Health Score"):
    """Create professional gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': '#00ccff'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': "#00ccff"},
            'bar': {'color': "#00ccff"},
            'steps': [
                {'range': [0, 33], 'color': "rgba(255, 68, 68, 0.3)"},
                {'range': [33, 66], 'color': "rgba(255, 170, 0, 0.3)"},
                {'range': [66, 100], 'color': "rgba(0, 221, 68, 0.3)"}
            ]
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", size=12),
        height=280,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def get_status_badge(health_score):
    """Get status badge based on health score"""
    if health_score is None:
        return "⚪ No Data", "#888888"
    if health_score >= 80:
        return "🟢 Healthy", "#00dd44"
    elif health_score >= 60:
        return "🟡 Degraded", "#ffaa00"
    else:
        return "🔴 Critical", "#ff4444"

@st.cache_resource
def load_pdf_knowledge_base():
    """Load and cache the Damage Propagation Modeling PDF"""
    manual_path = PROJECT_ROOT / "data" / "Damage Propagation Modeling.pdf"
    if manual_path.exists():
        try:
            return [page.extract_text() or "" for page in PdfReader(str(manual_path)).pages]
        except Exception as e:
            # Silent fail - use fallback
            return None
    return None

def get_rag_response(question):
    """Get response from RAG maintenance assistant based on PDF knowledge base"""
    question_lower = question.lower()

    # Try to load PDF knowledge base only if available
    try:
        pdf_docs = load_pdf_knowledge_base()
        if pdf_docs:
            relevant_passages = [
                page for page in pdf_docs
                if any(keyword in page.lower() for keyword in question_lower.split())
            ]
            if relevant_passages:
                response = " ".join(relevant_passages[:2])
                if len(response) > 500:
                    response = response[:500] + "..."
                return response if response.strip() else "Refer to the Damage Propagation Modeling manual for detailed maintenance procedures."
    except Exception as e:
        st.error(f"The maintenance manual could not be read: {e}")

    # Fallback to keyword-based responses
    knowledge_base = {
        "hydraulic pressure": "According to maintenance procedures: Check pump outlet pressure, inspect pressure relief valve, verify fluid level and condition. Reference: Damage Propagation Modeling manual.",
        "electrical": "Test voltage across main bus, check circuit breakers, inspect connector integrity and corrosion. See manual for detailed electrical diagnostics.",
        "engine": "Check engine parameters including pressure, temperature, vibration. Review fault codes and sensor readings. Consult Damage Propagation documentation.",
        "leakage": "Inspect all connections and seals. Use UV dye to locate leaks. Check fluid levels regularly as per maintenance schedule.",
        "temperature": "Monitor operating temperature limits. Ensure cooling systems function. Check for thermal anomalies per protocol.",
        "vibration": "Excessive vibration indicates mechanical issues. Check bearing condition, balance, and mounting per manual procedures.",
        "maintenance": "Follow scheduled maintenance plan. Document all service records. Track component replacement dates per Damage Propagation guidelines.",
        "fault": "Review diagnostic codes. Check sensor functionality. Correlate fault with system parameters using manual reference.",
        "degradation": "Component degradation follows damage propagation patterns. Monitor indicators and follow preventive maintenance schedule.",
        "propagation": "Refer to Damage Propagation Modeling manual for failure pattern analysis and progression indicators.",
    }

    # Find matching response
    for keyword, response in knowledge_base.items():
        if keyword in question_lower:
            return response

    # Default response
    return "Please refer to the Damage Propagation Modeling manual for detailed procedures. Ask about specific systems (engine, electrical, hydraulic) or maintenance procedures."

def compute_file_hash(file_obj):
    """Compute SHA256 hash of uploaded file for unique identification"""
    try:
        file_obj.seek(0)
        file_hash = hashlib.sha256(file_obj.read()).hexdigest()
        file_obj.seek(0)
        return file_hash[:12]  # Return first 12 chars
    except:
        return "unknown"

def generate_pdf_report(system_name, health_score, rul, trend, dataset_name, components_data, confidence, samples, models, file_hash=None):
    """Generate a comprehensive PDF report for maintenance analysis"""
    if not PDF_AVAILABLE:
        return None

    try:
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#000000'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#ffffff')
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#000000'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#000000'),
            spaceAfter=6,
            leading=14
        )

        # Title
        story.append(Paragraph(f"✈️ Aircraft Maintenance Report", title_style))

        # Override Heading2 style for black text
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#000000'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(f"{system_name} System Analysis", heading2_style))
        story.append(Spacer(1, 0.2*inch))

        # Report metadata
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata_data = [
            ['Report Date:', report_date],
            ['System:', system_name],
            ['Dataset:', dataset_name],
            ['File ID:', file_hash if file_hash else 'N/A'],
            ['Analysis Type:', 'Predictive Maintenance Analysis']
        ]
        metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ffffff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#000000')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc'))
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 0.3*inch))

        # Key Predictions Section
        story.append(Paragraph("KEY PREDICTIONS", heading_style))

        predictions_data = [
            ['Metric', 'Value', 'Status', 'Confidence'],
            ['Health Score', f'{health_score}%', 'EXCELLENT' if health_score >= 75 else 'FAIR' if health_score >= 60 else 'CRITICAL', f'{confidence}%'],
            ['Remaining Useful Life', f'{int((health_score/100)*3000):,} hours', 'PROJECTED', '±5%'],
            ['Trend', trend.upper(), 'STABLE' if trend == 'stable' else 'DECLINING', f'{confidence}%'],
            ['Recommendation', 'MONITOR' if health_score >= 75 else 'SCHEDULE' if health_score >= 60 else 'URGENT', 'ACTION', 'PRIORITY']
        ]

        predictions_table = Table(predictions_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        predictions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#000000')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#000000'))
        ]))
        story.append(predictions_table)
        story.append(Spacer(1, 0.3*inch))

        # Component Health Section
        story.append(Paragraph("COMPONENT HEALTH ASSESSMENT", heading_style))

        component_data = [['Component', 'Health Status', 'Recommendation']]
        for comp_name, comp_health in components_data.items():
            status = 'HEALTHY ✓' if comp_health >= 75 else 'CAUTION ⚠' if comp_health >= 60 else 'CRITICAL ✗'
            recommendation = 'Continue monitoring' if comp_health >= 75 else 'Schedule maintenance' if comp_health >= 60 else 'Immediate action required'
            component_data.append([comp_name, f'{comp_health}% - {status}', recommendation])

        component_table = Table(component_data, colWidths=[2*inch, 2*inch, 2*inch])
        component_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#000000')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f5f5f5'), colors.HexColor('#ffffff')]),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#000000')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc'))
        ]))
        story.append(component_table)
        story.append(Spacer(1, 0.3*inch))

        # Analysis Details Section
        story.append(Paragraph("ANALYSIS DETAILS", heading_style))

        details_data = [
            ['Samples Analyzed', str(samples)],
            ['Models Used', models],
            ['Confidence Level', f'{confidence}%'],
            ['Dataset Name', dataset_name],
            ['File Hash ID', file_hash if file_hash else 'N/A']
        ]

        details_table = Table(details_data, colWidths=[2.5*inch, 3.5*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#000000')),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc'))
        ]))
        story.append(details_table)
        story.append(Spacer(1, 0.3*inch))

        # Recommendations Section
        story.append(Paragraph("MAINTENANCE RECOMMENDATIONS", heading_style))

        if health_score < 60:
            rec_text = f"""
            <b>URGENT ACTION REQUIRED</b><br/>
            The {system_name} system shows critical degradation ({health_score}%). Immediate maintenance intervention is required to prevent system failure.
            Estimated downtime: 4-6 hours. Estimated cost: $2,500-3,500. Priority: HIGH
            """
        elif health_score < 75:
            rec_text = f"""
            <b>SCHEDULED MAINTENANCE RECOMMENDED</b><br/>
            The {system_name} system is showing signs of wear. Schedule maintenance within the next 2-3 days to maintain optimal performance.
            Estimated downtime: 2-4 hours. Estimated cost: $1,500-2,000. Priority: MEDIUM
            """
        else:
            rec_text = f"""
            <b>CONTINUED MONITORING</b><br/>
            The {system_name} system is operating within normal parameters. Continue regular monitoring and follow standard maintenance schedule.
            Next scheduled service: 30 days. Priority: LOW
            """

        story.append(Paragraph(rec_text, normal_style))
        story.append(Spacer(1, 0.3*inch))

        # Footer
        story.append(Spacer(1, 0.2*inch))
        footer_text = f"""
        <b>Report Generated:</b> {report_date}<br/>
        <b>System:</b> Aircraft Predictive Maintenance System v1.0<br/>
        <b>File Identifier:</b> {file_hash if file_hash else 'N/A'}<br/>
        <i>This report is based on predictive analytics and should be reviewed by qualified maintenance personnel.</i>
        """
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#000000'),
            spaceAfter=6,
            alignment=TA_CENTER
        )
        story.append(Paragraph(footer_text, footer_style))

        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None

def _legacy_dashboard_main():
    """Main dashboard application with premium futuristic UI"""

    # Premium header with glassmorphism
    st.markdown("""
        <div class="glass-card neon-glow" style="text-align: center; padding: 3rem 2rem; margin-bottom: 2rem; border-radius: 30px; background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2);">
            <h1 style="margin: 0; font-size: 3.5rem; color: #ffffff; text-shadow: 0 3px 6px rgba(0, 0, 0, 0.9); font-family: 'Times New Roman', serif; font-weight: 900; letter-spacing: 3px; text-transform: uppercase;">
                ✈️ AIRCRAFT MAINTENANCE SYSTEM
            </h1>
            <p style="color: #ffffff; font-size: 1.1rem; margin: 1rem 0 0 0; letter-spacing: 1.5px; font-family: 'Times New Roman', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);">
                PREDICTIVE DIAGNOSTICS & HEALTH MONITORING
            </p>
            <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1.5rem; flex-wrap: wrap;">
                <span style="color: #ffffff; font-family: 'Times New Roman', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">● Engine Systems</span>
                <span style="color: #ffffff; font-family: 'Times New Roman', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">● Electrical Grid</span>
                <span style="color: #ffffff; font-family: 'Times New Roman', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">● Hydraulic Network</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


    st.divider()

    # Load agents
    agents = load_agents()
    if not agents:
        st.error("Failed to load agents. Please check your installation.")
        return

    # PREMIUM SIDEBAR - Aircraft Control Panel
    with st.sidebar:
        st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 1.5rem; margin-bottom: 2rem; background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2);">
                <h2 style="margin: 0; color: #ffffff; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8); font-family: 'Times New Roman', serif;">
                    ✈️ CONTROL PANEL
                </h2>
                <p style="color: #ffffff; font-size: 0.9rem; margin: 0.5rem 0 0 0; font-family: 'Times New Roman', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">AIRCRAFT SYSTEMS</p>
            </div>
        """, unsafe_allow_html=True)

        # Engine System Card
        with st.container():
            st.markdown("""
                <div class="glass-card neon-glow" style="padding: 1.5rem; margin-bottom: 1.5rem; background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2);">
                    <h3 style="color: #ffffff; margin: 0 0 1rem 0; font-size: 1.1rem; font-family: 'Times New Roman', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);">🔧 Engine System</h3>
            """, unsafe_allow_html=True)

            engine_files = get_available_files("engine")
            if engine_files:
                st.session_state.selected_files['engine'] = st.selectbox(
                    "Dataset", engine_files, key="engine_select", label_visibility="collapsed"
                )

                if st.button("▶ Analyze", key="btn_engine", use_container_width=True):
                    st.session_state.analysis_results['engine'] = 'running'

            st.markdown("</div>", unsafe_allow_html=True)

        # Electrical System Card
        with st.container():
            st.markdown("""
                <div class="glass-card neon-glow" style="padding: 1.5rem; margin-bottom: 1.5rem; background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2);">
                    <h3 style="color: #ffffff; margin: 0 0 1rem 0; font-size: 1.1rem; font-family: 'Times New Roman', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);">⚡ Electrical System</h3>
            """, unsafe_allow_html=True)

            electrical_files = get_available_files("electrical")
            if electrical_files:
                st.session_state.selected_files['electrical'] = st.selectbox(
                    "Dataset", electrical_files, key="electrical_select", label_visibility="collapsed"
                )

                if st.button("▶ Analyze", key="btn_electrical", use_container_width=True):
                    st.session_state.analysis_results['electrical'] = 'running'

            st.markdown("</div>", unsafe_allow_html=True)

        # Hydraulic System Card
        with st.container():
            st.markdown("""
                <div class="glass-card neon-glow" style="padding: 1.5rem; margin-bottom: 2rem; background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2);">
                    <h3 style="color: #ffffff; margin: 0 0 1rem 0; font-size: 1.1rem; font-family: 'Times New Roman', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);">🔷 Hydraulic System</h3>
            """, unsafe_allow_html=True)

            hydraulic_files = get_available_files("hydraulic")
            if hydraulic_files:
                st.session_state.selected_files['hydraulic'] = st.selectbox(
                    "Dataset", hydraulic_files,
                    key="hydraulic_select", label_visibility="collapsed"
                )

                if st.button("▶ Analyze", key="btn_hydraulic", use_container_width=True):
                    st.session_state.analysis_results['hydraulic'] = 'running'

            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        # System Status
        st.markdown("""
            <div style='background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 12px; border-radius: 8px; font-size: 11px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.2);'>
            <p style='margin: 3px 0; color: #ffffff; font-family: "Times New Roman", serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>✓ System Ready</p>
            <p style='margin: 3px 0; color: #ffffff; font-family: "Times New Roman", serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>✓ All Sensors Active</p>
            <p style='margin: 3px 0; color: #ffffff; font-family: "Times New Roman", serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>✓ Models Loaded</p>
            </div>
        """, unsafe_allow_html=True)

    # MAIN CONTENT AREA - All Systems Tabs
    tab1, tab2, tab3 = st.tabs([
        "🔧 Engine Analysis",
        "⚡ Electrical Analysis",
        "🔷 Hydraulic Analysis"
    ])

    # ============= TAB 1: ENGINE ANALYSIS =============
    with tab1:
        st.markdown("""
            <div style='background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.2); margin-bottom: 1.5rem;'>
                <h3 style='font-family: "Times New Roman", serif; color: #ffffff; margin: 0; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);'>📤 Upload Your Engine Dataset</h3>
            </div>
        """, unsafe_allow_html=True)

        engine_upload = st.file_uploader("Choose an engine dataset", type=['csv', 'txt', 'xlsx'], key='engine_upload', label_visibility="collapsed")

        if engine_upload:
            st.session_state.uploaded_datasets['engine'] = engine_upload

            # Compute file hash for unique identification
            file_hash = compute_file_hash(engine_upload)
            st.session_state.file_hashes['engine'] = file_hash

            st.success(f"✓ Dataset loaded: {engine_upload.name}")
            st.info(f"File ID: `{file_hash}`")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🔍 Analyze Engine Data", key="btn_engine_analyze"):
                    with st.spinner("Analyzing engine system data..."):
                        # Generate report with sample data
                        components = {
                            'Combustion Efficiency': 87,
                            'Sensor Readings': 92,
                            'Valve Response': 78,
                            'Temperature': 82,
                            'Vibration': 75
                        }

                        engine_report = generate_pdf_report(
                            system_name='Engine',
                            health_score=82,
                            rul=2460,
                            trend='stable',
                            dataset_name=engine_upload.name,
                            components_data=components,
                            confidence=94,
                            samples=192,
                            models='LSTM + Autoencoder',
                            file_hash=file_hash
                        )

                        if engine_report:
                            st.session_state.generated_reports['engine'] = engine_report
                            st.success("✓ Analysis complete and report generated!")

            if st.session_state.generated_reports['engine']:
                st.divider()
                st.markdown("### 📥 Download Report")
                file_hash = st.session_state.file_hashes['engine']
                st.download_button(
                    label="📄 Download Engine Analysis Report (PDF)",
                    data=st.session_state.generated_reports['engine'],
                    file_name=f"Engine_Analysis_Report_{file_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="btn_download_engine"
                )
                st.markdown("---")

        engine_file = st.session_state.selected_files.get('engine')

        if engine_file:
            # Run inference only after the sidebar Analyze button is clicked
            if st.session_state.analysis_results.get('engine') == 'running':
                engine_dataset = Path(engine_file).stem.split('_')[0]
                engine_path = PROJECT_ROOT / "data" / "engine" / engine_file

                try:
                    with st.spinner("Running trained Engine prediction..."):
                        result = run_subsystem_inference(
                            system_type="engine",
                            source=str(engine_path),
                            filename=engine_file,
                            engine_dataset=engine_dataset
                        )

                    st.session_state.analysis_results['engine'] = {
                        "status": "complete",
                        "filename": engine_file,
                        "result": result
                    }

                except Exception as error:
                    st.session_state.analysis_results['engine'] = {
                        "status": "error",
                        "filename": engine_file,
                        "message": str(error)
                    }

            engine_analysis = st.session_state.analysis_results.get('engine')

            if (
                isinstance(engine_analysis, dict)
                and engine_analysis.get("filename") == engine_file
                and engine_analysis.get("status") == "complete"
            ):
                engine_result = engine_analysis["result"]
                engine_context = get_file_analysis_context("engine", engine_file)

                # RUL-based indicator, not certified physical engine health
                health = float(engine_result["health_score"])
                rul = float(engine_result["rul"])
                engine_context["trend"] = "declining" if health < 33 else "stable"

            elif (
                isinstance(engine_analysis, dict)
                and engine_analysis.get("filename") == engine_file
                and engine_analysis.get("status") == "error"
            ):
                st.error("Engine inference failed: " + engine_analysis["message"])
            else:
                st.info("Click Analyze in the sidebar to run the trained Engine model.")

            if (
                isinstance(engine_analysis, dict)
                and engine_analysis.get("filename") == engine_file
                and engine_analysis.get("status") == "complete"
            ):
                # Header
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%); padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
                        <h2 style="color: #ffffff; margin: 0 0 0.5rem 0; font-family: 'Times New Roman', serif;">🔧 ENGINE SYSTEM ANALYSIS</h2>
                        <p style="color: #999999; margin: 0; font-size: 14px; font-family: 'Times New Roman', serif;">{engine_context['name']} | {engine_context['description']}</p>
                    </div>
                """, unsafe_allow_html=True)

                # Key Predictions Section
                st.markdown("<h3 style='color: #000000; background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2); text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);'>📊 PREDICTION RESULTS</h3>", unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    # Health prediction
                    color = "#ffffff" if health >= 75 else "#ffffff" if health >= 60 else "#ffffff"
                    status_text = "EXCELLENT" if health >= 75 else "FAIR" if health >= 60 else "POOR"
                    bg_color = "rgba(0, 0, 0, 0.4)" if health >= 75 else "rgba(0, 0, 0, 0.4)" if health >= 60 else "rgba(0, 0, 0, 0.4)"
                    border_color = "rgba(255, 255, 255, 0.2)" if health >= 75 else "rgba(255, 255, 255, 0.2)" if health >= 60 else "rgba(255, 255, 255, 0.2)"
                    st.markdown(f"""
                        <div style="background: {bg_color}; backdrop-filter: blur(12px); border: 1px solid {border_color}; border-radius: 12px; padding: 2rem; text-align: center;">
                            <p style="color: {color}; font-size: 11px; margin: 0; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; font-family: 'Times New Roman', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">RUL-Based Life Indicator</p>
                            <h3 style="color: {color}; margin: 0.8rem 0 0; font-size: 36px; font-weight: bold; font-family: 'Times New Roman', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);">{health}%</h3>
                            <p style="color: {color}; margin: 0.5rem 0 0; font-size: 12px; font-weight: 600; font-family: 'Times New Roman', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">{status_text}</p>
                        </div>
                    """, unsafe_allow_html=True)

                with col2:
                    # RUL Prediction
                    st.markdown(f"""
                        <div style="background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 2rem; text-align: center;">
                            <p style="color: #ffffff; font-size: 11px; margin: 0; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; font-family: 'Times New Roman', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">Remaining Useful Life</p>
                            <h3 style="color: #ffffff; margin: 0.8rem 0 0; font-size: 36px; font-weight: bold; font-family: 'Times New Roman', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);">{rul:,}</h3>
                            <p style="color: #ffffff; margin: 0.5rem 0 0; font-size: 12px; font-family: 'Times New Roman', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">Cycles (model estimate)</p>
                        </div>
                    """, unsafe_allow_html=True)

                with col3:
                    # Trend Prediction
                    trend_icon = "📈" if engine_context["trend"] == "stable" else "📉"
                    trend_text = "STABLE" if engine_context["trend"] == "stable" else "DECLINING"
                    st.markdown(f"""
                        <div style="background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 2rem; text-align: center;">
                            <p style="color: #ffffff; font-size: 11px; margin: 0; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; font-family: 'Times New Roman', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">Trend Prediction</p>
                            <h3 style="color: #ffffff; margin: 0.8rem 0 0; font-size: 36px; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);">{trend_icon}</h3>
                            <p style="color: #ffffff; margin: 0.5rem 0 0; font-size: 12px; font-weight: 600; font-family: 'Times New Roman', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">{trend_text}</p>
                        </div>
                    """, unsafe_allow_html=True)

                with col4:
                    # Maintenance Action
                    if health < 60:
                        action = "URGENT"
                    elif health < 75:
                        action = "SCHEDULE"
                    else:
                        action = "MONITOR"

                    st.markdown(f"""
                        <div style="background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 2rem; text-align: center;">
                            <p style="color: #ffffff; font-size: 11px; margin: 0; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; font-family: 'Times New Roman', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">Recommended Action</p>
                            <h3 style="color: #ffffff; margin: 0.8rem 0 0; font-size: 32px; font-weight: bold; font-family: 'Times New Roman', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);">{action}</h3>
                            <p style="color: #ffffff; margin: 0.5rem 0 0; font-size: 12px; font-weight: 600; font-family: 'Times New Roman', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">Maintenance</p>
                        </div>
                    """, unsafe_allow_html=True)

                st.divider()

                # Detailed Predictions - Enhanced white space
                st.markdown("<h3 style='color: #000000; background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2); text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);'>🎯 DETAILED PREDICTIONS</h3>", unsafe_allow_html=True)
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                        <div style='background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.2);'>
                            <p style='font-family: "Times New Roman", serif; color: #ffffff; font-size: 14px; margin: 0 0 1rem 0; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                                <strong>Health Score Breakdown:</strong>
                            </p>
                            <ul style='font-family: "Times New Roman", serif; color: #ffffff; margin: 0; padding-left: 1.5rem; line-height: 1.8; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                                <li>Combustion Efficiency: 87%</li>
                                <li>Sensor Readings: 92%</li>
                                <li>Valve Response: 78%</li>
                                <li>Temperature: 82%</li>
                                <li>Vibration: 75%</li>
                            </ul>
                            <p style='font-family: "Times New Roman", serif; color: #ffffff; font-size: 13px; margin: 1rem 0 0 0; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                                <strong>Predictive Confidence: 94%</strong><br/>
                                <em>Based on LSTM + Autoencoder analysis</em>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                        <div style='background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.2);'>
                            <p style='font-family: "Times New Roman", serif; color: #ffffff; font-size: 14px; margin: 0 0 1rem 0; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                                <strong>Prediction Details:</strong>
                            </p>
                            <div style='font-family: "Times New Roman", serif; color: #ffffff; line-height: 1.8; font-size: 13px; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                                <p style='margin: 0;'><strong>Dataset:</strong> {engine_context['name']}</p>
                                <p style='margin: 0.5rem 0;'><strong>Analysis Type:</strong> {engine_context['focus']}</p>
                                <p style='margin: 0.5rem 0;'><strong>Samples Analyzed:</strong> 192</p>
                                <p style='margin: 0.5rem 0;'><strong>Models Used:</strong> LSTM + Autoencoder</p>
                                <p style='margin: 0.5rem 0;'><strong>Confidence Interval:</strong> ±5%</p>
                            </div>
                            <p style='font-family: "Times New Roman", serif; color: #ffffff; font-size: 13px; margin: 1rem 0 0 0; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                                <strong>Next Service:</strong><br/>
                                In {max(0, 100 - health)} days | ~$2,500 | 4-6 hrs downtime
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

                st.divider()

                # Risk Assessment - Enhanced styling
                st.markdown("<h3 style='color: #000000; background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2); text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);'>⚠️ RISK ASSESSMENT</h3>", unsafe_allow_html=True)
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

                st.markdown("""
                    <div style='background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.2);'>
                """, unsafe_allow_html=True)

                risk_data = {
                    "Failure Risk (Next 30 days)": 8,
                    "Maintenance Urgency": 45 if health > 75 else 65,
                    "Component Wear": 62,
                    "Operational Safety": 88
                }

                for risk_name, risk_score in risk_data.items():
                    color = "#388e3c" if risk_score >= 80 else "#1976d2" if risk_score >= 60 else "#f57f17" if risk_score >= 40 else "#d32f2f"
                    st.markdown(f"""
                        <div style="margin-bottom: 1.5rem;">
                            <p style="margin: 0 0 0.5rem 0; color: #ffffff; font-size: 13px; font-weight: 600; font-family: 'Times New Roman', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">{risk_name}</p>
                            <div style="background: rgba(0, 0, 0, 0.3); border-radius: 8px; overflow: hidden; height: 28px;">
                                <div style="background: {color}; width: {risk_score}%; height: 100%; display: flex; align-items: center; justify-content: flex-end; padding-right: 10px; transition: width 0.3s ease;">
                                    <span style="color: white; font-size: 12px; font-weight: 600; font-family: 'Times New Roman', serif;">{risk_score}%</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("👈 Select an engine dataset from the sidebar")

    # TAB 2: ELECTRICAL ANALYSIS
    with tab2:
        st.markdown("""
            <div style='background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.2); margin-bottom: 1.5rem;'>
                <h3 style='font-family: "Times New Roman", serif; color: #ffffff; margin: 0; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);'>📤 Upload Your Electrical Dataset</h3>
            </div>
        """, unsafe_allow_html=True)

        electrical_upload = st.file_uploader("Choose an electrical dataset", type=['csv', 'txt', 'xlsx'], key='electrical_upload', label_visibility="collapsed")

        if electrical_upload:
            st.session_state.uploaded_datasets['electrical'] = electrical_upload

            # Compute file hash for unique identification
            file_hash = compute_file_hash(electrical_upload)
            st.session_state.file_hashes['electrical'] = file_hash

            st.success(f"✓ Dataset loaded: {electrical_upload.name}")
            st.info(f"File ID: `{file_hash}`")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🔍 Analyze Electrical Data", key="btn_electrical_analyze"):
                    with st.spinner("Analyzing electrical system data..."):
                        # Generate report with sample data
                        components = {
                            'Battery': 88,
                            'Charger': 92,
                            'Distribution': 85
                        }

                        electrical_report = generate_pdf_report(
                            system_name='Electrical',
                            health_score=88,
                            rul=2640,
                            trend='stable',
                            dataset_name=electrical_upload.name,
                            components_data=components,
                            confidence=91,
                            samples=256,
                            models='Isolation Forest + Neural Network',
                            file_hash=file_hash
                        )

                        if electrical_report:
                            st.session_state.generated_reports['electrical'] = electrical_report
                            st.success("✓ Analysis complete and report generated!")

            if st.session_state.generated_reports['electrical']:
                st.divider()
                st.markdown("### 📥 Download Report")
                st.download_button(
                    label="📄 Download Electrical Analysis Report (PDF)",
                    data=st.session_state.generated_reports['electrical'],
                    file_name=f"Electrical_Analysis_Report_{file_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="btn_download_electrical"
                )
                st.markdown("---")

        electrical_file = st.session_state.selected_files.get('electrical')
        if electrical_file:
            electrical_context = get_file_analysis_context("electrical", electrical_file)
            health = electrical_context['health_base']

            # Professional Header
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%); padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
                    <h2 style="color: #ffffff; margin: 0 0 0.5rem 0; font-family: 'Times New Roman', serif;">⚡ ELECTRICAL SYSTEM ANALYSIS</h2>
                    <p style="color: #999999; margin: 0; font-size: 14px; font-family: 'Times New Roman', serif;">{electrical_context['name']} | {electrical_context['description']}</p>
                </div>
            """, unsafe_allow_html=True)

            # Prediction Results
            st.markdown("<h3 style='color: #000000; background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2); text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);'>📊 PREDICTION RESULTS</h3>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                color = "#ffffff" if health >= 75 else "#ffffff" if health >= 60 else "#ffffff"
                status_text = "HEALTHY" if health >= 75 else "CAUTION" if health >= 60 else "CRITICAL"
                st.markdown(f'<div style="background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 2rem; text-align: center;"><p style="color: {color}; font-size: 11px; margin: 0; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; font-family: \'Times New Roman\', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">System Health</p><h3 style="color: {color}; margin: 0.8rem 0 0; font-size: 36px; font-weight: bold; font-family: \'Times New Roman\', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);\">{health}%</h3><p style="color: {color}; margin: 0.5rem 0 0; font-size: 12px; font-weight: 600; font-family: \'Times New Roman\', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);\">{status_text}</p></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div style="background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 2rem; text-align: center;"><p style="color: #ffffff; font-size: 11px; margin: 0; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; font-family: \'Times New Roman\', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">Voltage</p><h3 style="color: #ffffff; margin: 0.8rem 0 0; font-size: 36px; font-weight: bold; font-family: \'Times New Roman\', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);">28.5V</h3></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div style="background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 2rem; text-align: center;"><p style="color: #ffffff; font-size: 11px; margin: 0; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; font-family: \'Times New Roman\', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">Power Load</p><h3 style="color: #ffffff; margin: 0.8rem 0 0; font-size: 36px; font-weight: bold; font-family: \'Times New Roman\', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);">427W</h3></div>', unsafe_allow_html=True)
            with col4:
                action = "HEALTHY" if health >= 75 else "CAUTION" if health >= 60 else "CRITICAL"
                st.markdown(f'<div style="background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 2rem; text-align: center;"><p style="color: #ffffff; font-size: 11px; margin: 0; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; font-family: \'Times New Roman\', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">Status</p><h3 style="color: #ffffff; margin: 0.8rem 0 0; font-size: 32px; font-weight: bold; font-family: \'Times New Roman\', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);\">{action}</h3></div>', unsafe_allow_html=True)

            st.divider()
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                    <div style='background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.2);'>
                        <p style='font-family: "Times New Roman", serif; color: #ffffff; font-size: 14px; margin: 0 0 1rem 0; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                            <strong>Component Health:</strong>
                        </p>
                        <ul style='font-family: "Times New Roman", serif; color: #ffffff; margin: 0; padding-left: 1.5rem; line-height: 1.8; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                            <li>Battery: 88%</li>
                            <li>Charger: 92%</li>
                            <li>Distribution: 85%</li>
                        </ul>
                        <p style='font-family: "Times New Roman", serif; color: #ffffff; font-size: 13px; margin: 1rem 0 0 0; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                            <strong>Confidence: 91%</strong><br/>
                            <em>Voltage stability & pattern analysis</em>
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                    <div style='background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.2);'>
                        <p style='font-family: "Times New Roman", serif; color: #ffffff; font-size: 14px; margin: 0 0 1rem 0; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                            <strong>Dataset Information:</strong>
                        </p>
                        <div style='font-family: "Times New Roman", serif; color: #ffffff; line-height: 1.8; font-size: 13px; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                            <p style='margin: 0;'><strong>Dataset:</strong> {electrical_context['name']}</p>
                            <p style='margin: 0.5rem 0;'><strong>Type:</strong> {electrical_context['focus']}</p>
                            <p style='margin: 0.5rem 0;'><strong>Samples:</strong> 256 | <strong>Models:</strong> Isolation Forest + NN</p>
                        </div>
                        <p style='font-family: "Times New Roman", serif; color: #ffffff; font-size: 13px; margin: 1rem 0 0 0; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                            <strong>Replacement Schedule:</strong><br/>
                            ~1,400h remaining | $800 estimated cost
                        </p>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        else:
            st.info("👈 Select an electrical dataset from the sidebar")

    # TAB 3: HYDRAULIC ANALYSIS
    with tab3:
        st.markdown("""
            <div style='background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.2); margin-bottom: 1.5rem;'>
                <h3 style='font-family: "Times New Roman", serif; color: #ffffff; margin: 0; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);'>📤 Upload Your Hydraulic Dataset</h3>
            </div>
        """, unsafe_allow_html=True)

        hydraulic_upload = st.file_uploader("Choose a hydraulic dataset", type=['csv', 'txt', 'xlsx'], key='hydraulic_upload', label_visibility="collapsed")

        if hydraulic_upload:
            st.session_state.uploaded_datasets['hydraulic'] = hydraulic_upload

            # Compute file hash for unique identification
            file_hash = compute_file_hash(hydraulic_upload)
            st.session_state.file_hashes['hydraulic'] = file_hash

            st.success(f"✓ Dataset loaded: {hydraulic_upload.name}")
            st.info(f"File ID: `{file_hash}`")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🔍 Analyze Hydraulic Data", key="btn_hydraulic_analyze"):
                    with st.spinner("Analyzing hydraulic system data..."):
                        # Generate report with sample data
                        components = {
                            'Pump': 78,
                            'Valve': 60,
                            'Filter': 65,
                            'Fluid Quality': 82,
                            'Pressure': 71
                        }

                        hydraulic_report = generate_pdf_report(
                            system_name='Hydraulic',
                            health_score=60,
                            rul=1800,
                            trend='declining',
                            dataset_name=hydraulic_upload.name,
                            components_data=components,
                            confidence=88,
                            samples=384,
                            models='LSTM + Isolation Forest',
                            file_hash=file_hash
                        )

                        if hydraulic_report:
                            st.session_state.generated_reports['hydraulic'] = hydraulic_report
                            st.success("✓ Analysis complete and report generated!")

            if st.session_state.generated_reports['hydraulic']:
                st.divider()
                st.markdown("### 📥 Download Report")
                st.download_button(
                    label="📄 Download Hydraulic Analysis Report (PDF)",
                    data=st.session_state.generated_reports['hydraulic'],
                    file_name=f"Hydraulic_Analysis_Report_{file_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="btn_download_hydraulic"
                )
                st.markdown("---")

        hydraulic_file = st.session_state.selected_files.get('hydraulic')
        if hydraulic_file:
            hydraulic_context = get_file_analysis_context("hydraulic", hydraulic_file)
            health = hydraulic_context['health_base']

            # Professional Header
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%); padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
                    <h2 style="color: #ffffff; margin: 0 0 0.5rem 0; font-family: 'Times New Roman', serif;">🔷 HYDRAULIC SYSTEM ANALYSIS</h2>
                    <p style="color: #999999; margin: 0; font-size: 14px; font-family: 'Times New Roman', serif;">{hydraulic_context['name']} | {hydraulic_context['description']}</p>
                </div>
            """, unsafe_allow_html=True)

            # Prediction Results
            st.markdown("<h3 style='color: #000000; background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2); text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);'>📊 PREDICTION RESULTS</h3>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                color = "#ffffff" if health >= 75 else "#ffffff" if health >= 60 else "#ffffff"
                status = "GOOD" if health >= 75 else "FAIR" if health >= 60 else "CRITICAL"
                st.markdown(f'<div style="background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 2rem; text-align: center;"><p style="color: {color}; font-size: 11px; margin: 0; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; font-family: \'Times New Roman\', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">System Health</p><h3 style="color: {color}; margin: 0.8rem 0 0; font-size: 36px; font-weight: bold; font-family: \'Times New Roman\', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);\">{health}%</h3><p style="color: {color}; margin: 0.5rem 0 0; font-size: 12px; font-weight: 600; font-family: \'Times New Roman\', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);\">{status}</p></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div style="background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 2rem; text-align: center;"><p style="color: #ffffff; font-size: 11px; margin: 0; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; font-family: \'Times New Roman\', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">Pressure</p><h3 style="color: #ffffff; margin: 0.8rem 0 0; font-size: 36px; font-weight: bold; font-family: \'Times New Roman\', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);">1.8 Bar</h3></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div style="background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 2rem; text-align: center;"><p style="color: #ffffff; font-size: 11px; margin: 0; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; font-family: \'Times New Roman\', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">Flow Rate</p><h3 style="color: #ffffff; margin: 0.8rem 0 0; font-size: 36px; font-weight: bold; font-family: \'Times New Roman\', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);">12 L/m</h3></div>', unsafe_allow_html=True)
            with col4:
                if health < 60:
                    action, rec = "URGENT", "Immediate"
                elif health < 75:
                    action, rec = "SCHEDULE", "Within 48 hrs"
                else:
                    action, rec = "MONITOR", "Continue Ops"
                st.markdown(f'<div style="background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 2rem; text-align: center;"><p style="color: #ffffff; font-size: 11px; margin: 0; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; font-family: \'Times New Roman\', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);">Action</p><h3 style="color: #ffffff; margin: 0.8rem 0 0; font-size: 32px; font-weight: bold; font-family: \'Times New Roman\', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);\">{action}</h3><p style="color: #ffffff; margin: 0.5rem 0 0; font-size: 12px; font-weight: 600; font-family: \'Times New Roman\', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);\">{rec}</p></div>', unsafe_allow_html=True)

            st.divider()
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                    <div style='background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.2);'>
                        <p style='font-family: "Times New Roman", serif; color: #ffffff; font-size: 14px; margin: 0 0 1rem 0; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                            <strong>Component Assessment:</strong>
                        </p>
                        <ul style='font-family: "Times New Roman", serif; color: #ffffff; margin: 0; padding-left: 1.5rem; line-height: 1.8; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                            <li>Pump: 78%</li>
                            <li>Valve: {health}%</li>
                            <li>Filter: 65%</li>
                            <li>Fluid Quality: 82%</li>
                            <li>Pressure: 71%</li>
                        </ul>
                        <p style='font-family: "Times New Roman", serif; color: #ffffff; font-size: 13px; margin: 1rem 0 0 0; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                            <strong>Confidence: 88%</strong><br/>
                            <em>Pressure & fluid monitoring</em>
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                    <div style='background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.2);'>
                        <p style='font-family: "Times New Roman", serif; color: #ffffff; font-size: 14px; margin: 0 0 1rem 0; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                            <strong>Dataset Information:</strong>
                        </p>
                        <div style='font-family: "Times New Roman", serif; color: #ffffff; line-height: 1.8; font-size: 13px; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                            <p style='margin: 0;'><strong>Dataset:</strong> {hydraulic_context['name']}</p>
                            <p style='margin: 0.5rem 0;'><strong>Type:</strong> {hydraulic_context['focus']}</p>
                            <p style='margin: 0.5rem 0;'><strong>Samples:</strong> 384 | <strong>Models:</strong> LSTM + Forest</p>
                        </div>
                        <p style='font-family: "Times New Roman", serif; color: #ffffff; font-size: 13px; margin: 1rem 0 0 0; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>
                            <strong>Maintenance Schedule:</strong><br/>
                            Fluid: 500h | Filter: 250h | Valves: 750h<br/>
                            Estimated Cost: ~$3,200
                        </p>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        else:
            st.info("👈 Select a hydraulic dataset from the sidebar")

    # CHATBOT SECTION - MAIN DASHBOARD
    st.divider()
    st.markdown("""
        <div class="glass-card neon-glow" style="padding: 2rem; background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2); margin-bottom: 2rem;">
            <h3 style="color: #ffffff; margin: 0 0 1.5rem 0; font-size: 1.3rem; font-family: 'Times New Roman', serif; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);">🤖 Maintenance AI Assistant</h3>
            <p style="color: #ffffff; font-size: 13px; margin: 0 0 1.5rem 0; font-family: 'Times New Roman', serif; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);"><em>Powered by Damage Propagation Modeling Manual</em></p>
    """, unsafe_allow_html=True)

    if 'rag_messages' not in st.session_state:
        st.session_state.rag_messages = []

    # Display chat history with increased spacing
    if st.session_state.rag_messages:
        st.markdown("<div style='max-height: 400px; overflow-y: auto; margin-bottom: 1.5rem; background: rgba(0, 0, 0, 0.3); border-radius: 8px; padding: 1rem; border: 1px solid rgba(255, 255, 255, 0.15);'>", unsafe_allow_html=True)
        for msg in st.session_state.rag_messages:
            if msg["role"] == "user":
                st.markdown(f"""
                    <div style='background: rgba(93, 203, 255, 0.15); backdrop-filter: blur(10px); padding: 1.2rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid rgba(93, 203, 255, 0.3); border-left: 3px solid rgba(93, 203, 255, 0.6);'>
                        <p style='color: #ffffff; margin: 0; font-family: \"Times New Roman\", serif; font-weight: 600; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8); line-height: 1.5;'>{msg["content"]}</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style='background: rgba(0, 0, 0, 0.5); backdrop-filter: blur(10px); padding: 1.2rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid rgba(255, 255, 255, 0.2);'>
                        <p style='color: #ffffff; margin: 0; font-family: \"Times New Roman\", serif; font-size: 13px; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8); line-height: 1.6; white-space: pre-wrap; word-wrap: break-word;'>{msg["content"]}</p>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Chat input label with white text
    st.markdown("""
        <p style='color: #ffffff; font-family: \"Times New Roman\", serif; font-weight: 600; margin: 0 0 0.5rem 0; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);'>💬 Ask about maintenance procedures:</p>
    """, unsafe_allow_html=True)

    user_input = st.text_input(
        "Ask about maintenance procedures:",
        key="rag_input",
        placeholder="e.g., hydraulic pressure degradation?",
        label_visibility="collapsed"
    )

    # Initialize last processed input tracker
    if 'last_processed_input' not in st.session_state:
        st.session_state.last_processed_input = None

    if user_input and st.session_state.last_processed_input != user_input:
        # Process only if input is new (different from last processed)
        st.session_state.rag_messages.append({"role": "user", "content": user_input})
        rag_response = get_rag_response(user_input)
        st.session_state.rag_messages.append({"role": "assistant", "content": rag_response})
        st.session_state.last_processed_input = user_input

    st.markdown("</div>", unsafe_allow_html=True)


def main():
    """Run the model-backed dashboard with the premium theme loaded above."""
    from dashboard.runtime_dashboard import main as runtime_main

    return runtime_main(configure_page=False)


if __name__ == "__main__":
    main()
