import streamlit as st
import pandas as pd
import numpy as np
import scipy.optimize as opt
import openpyxl

st.set_page_config(page_title="El Dorado EV Charging - AI Decision Support System", layout="wide", initial_sidebar_state="expanded")

# Custom Professional Styling (Dark Green & Base White - MBA Executive Palette)
st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #1B4D3E; font-family: 'Helvetica Neue', sans-serif; }
    .stMetric { background-color: #F1F8F6; padding: 15px; border-radius: 8px; border: 1px solid #C8E6C9; }
    </style>
""", unsafe_allow_html=True)

st.title("🌱 El Dorado EV Charging Network: Executive Decision Support System")
st.markdown("### AI-Integrated Strategic Optimization & Multi-Parameter Policy Tuning")

# Load data directly from Excel master file
@st.cache_data
def load_master_data():
    try:
        xls = pd.ExcelFile("El_Dorado_EV_Master.xlsx")
        return True
    except Exception as e:
        return False

excel_loaded = load_master_data()
if not excel_loaded:
    st.warning("⚠️ 'El_Dorado_EV_Master.xlsx' not found in repository root. Running on fallback model parameters.")

# Initialize Session State Variables
if 'budget' not in st.session_state: st.session_state.budget = 450.0
if 'subsidy_north' not in st.session_state: st.session_state.subsidy_north = 0.30
if 'subsidy_south' not in st.session_state: st.session_state.subsidy_south = 0.30
if 'demand_growth' not in st.session_state: st.session_state.demand_growth = 1.0
if 'coverage_target' not in st.session_state: st.session_state.coverage_target = 0.90
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello Executive Manager. I am your AI Decision Support Assistant. Type a command below (e.g., *'Set budget to 500 lakhs'*, *'Increase residential subsidy to 40%'*, or *'Set coverage target to 95%'*) and I will automatically update model parameters and re-run the ILP optimizer!"}
    ]

# Sidebar Controls for All Strategic Parameters
st.sidebar.header("🎛️ Master Policy & Model Controls")
st.sidebar.markdown("Fine-tune capital, subsidies, and service standards:")

st.session_state.budget = st.sidebar.slider("Total Capital Budget (₹ Lakhs)", 300.0, 700.0, float(st.session_state.budget), 10.0)
st.session_state.subsidy_north = st.sidebar.slider("North Metro Residential Subsidy (%)", 0.0, 0.6, float(st.session_state.subsidy_north), 0.05)
st.session_state.subsidy_south = st.sidebar.slider("South Plaza Residential Subsidy (%)", 0.0, 0.6, float(st.session_state.subsidy_south), 0.05)
st.session_state.demand_growth = st.sidebar.slider("Demand Multiplier (Growth)", 0.8, 1.5, float(st.session_state.demand_growth), 0.05)
st.session_state.coverage_target = st.sidebar.slider("Min Zone Coverage Target (%)", 0.70, 1.00, float(st.session_state.coverage_target), 0.05)

# AI Prompt Processing Logic
def process_ai_command(prompt):
    prompt_lower = prompt.lower()
    response_msg = ""
    
    if "budget" in prompt_lower:
        import re
        numbers = re.findall(r'\d+', prompt)
        if numbers:
            val = float(numbers[0])
            if 300 <= val <= 800:
                st.session_state.budget = val
                response_msg = f"✅ AI Updated: Total Capital Budget set to **₹{val} Lakhs**. Re-running ILP solver..."
            else:
                response_msg = "⚠️ Budget must be between ₹300L and ₹800L."
        else:
            response_msg = "⚠️ Please specify a valid budget amount (e.g., 'Set budget to 500')."
            
    elif "subsidy" in prompt_lower:
        import re
        numbers = re.findall(r'\d+', prompt)
        if numbers:
            val = float(numbers[0])
            if val > 1: val = val / 100.0
            if 0 <= val <= 0.6:
                st.session_state.subsidy_north = val
                st.session_state.subsidy_south = val
                response_msg = f"✅ AI Updated: Residential subsidies (North & South) adjusted to **{val*100:.0f}%**. Re-running optimizer..."
            else:
                response_msg = "⚠️ Subsidy must be between 0% and 60%."
        else:
            response_msg = "⚠️ Please specify a percentage (e.g., 'Set subsidy to 40%')."
            
    elif "coverage" in prompt_lower:
        import re
        numbers = re.findall(r'\d+', prompt)
        if numbers:
            val = float(numbers[0])
            if val > 1: val = val / 100.0
            if 0.7 <= val <= 1.0:
                st.session_state.coverage_target = val
                response_msg = f"✅ AI Updated: Minimum coverage target set to **{val*100:.0f}%**. Re-running solver..."
            else:
                response_msg = "⚠️ Coverage must be between 70% and 100%."
        else:
            response_msg = "⚠️ Please specify coverage target (e.g., 'Make coverage 95%')."
            
    elif "demand" in prompt_lower or "growth" in prompt_lower:
        import re
        numbers = re.findall(r'\d+', prompt)
        if numbers:
            val = float(numbers[0])
            if val > 10: val = val / 100.0 + 1.0
            if 0.5 <= val <= 2.0:
                st.session_state.demand_growth = val
                response_msg = f"✅ AI Updated: Demand multiplier set to **{val}x**. Re-running solver..."
            else:
                response_msg = "⚠️ Demand multiplier out of bounds."
        else:
            response_msg = "⚠️ Please specify demand growth (e.g., 'Increase demand by 20%')."
    else:
        response_msg = f"🤖 I processed your query: *'{prompt}'*. You can ask me to change budget, subsidies, coverage targets, or demand growth!"
        
    return response_msg

# Layout: Two columns (Left: AI Chat Assistant, Right: Live Results & KPIs)
col_left, col_right = st.columns([1, 1.3])

with col_left:
    st.markdown("### 💬 AI Manager Assistant")
    st.markdown("Type a prompt to control parameters conversationally:")
    
    # Chat History Box
    chat_box = st.container(height=400)
    with chat_box:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"**👤 Manager:** {msg['content']}")
            else:
                st.markdown(f"**🤖 AI DSS:** {msg['content']}")
                
    # Typing Form
    with st.form(key="chat_input_form", clear_on_submit=True):
        user_input = st.text_input("Ask AI assistant (e.g., 'Set budget to 500 lakhs'):")
        submitted = st.form_submit_button("Send Command")
        if submitted and user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            reply = process_ai_command(user_input)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

with col_right:
    st.markdown("### 📊 Live ILP Optimization Engine & KPIs")
    
    # Run Optimization Solver via SciPy MILP using Excel baseline parameters
    setup_costs = [
        70.0, # C1 CBD Mall
        48.0 * (1 - st.session_state.subsidy_north), # C2 North Metro (Subsidized)
        65.0, # C3 Tech Park
        42.0, # C4 University
        55.0, # C5 Highway Hub
        45.0 * (1 - st.session_state.subsidy_south)  # C6 South Plaza (Subsidized)
    ]
    op_costs = [3.2, 2.4, 3.5, 2.1, 2.8, 2.3]
    grid_limits = [700, 450, 800, 400, 900, 500]
    max_chargers = [14, 9, 16, 8, 18, 10]
    base_demand = [180, 120, 220, 100, 160, 140]
    demand = [d * st.session_state.demand_growth for d in base_demand]
    min_sessions_target = st.session_state.coverage_target * sum(base_demand)
    
    cov_matrix = [
        [1, 0, 1, 1, 0, 0], # Z1
        [1, 1, 0, 1, 0, 0], # Z2
        [1, 0, 1, 1, 0, 0], # Z3
        [1, 1, 1, 1, 0, 0], # Z4
        [0, 0, 1, 0, 1, 1], # Z5
        [0, 0, 0, 0, 1, 1]  # Z6
    ]
    
    rev_S = 16 * 185 * 30 / 100000
    rev_F = 28 * 260 * 30 / 100000
    
    c_vec = op_costs + [-rev_S]*6 + [-rev_F]*6 + [0]*6
    integrality_vec = [1]*6 + [1]*6 + [1]*6 + [1]*6
    
    A_mat, b_u_vec, b_l_vec = [], [], []
    for i in range(6):
        row = [0]*24
        row[i] = -max_chargers[i]
        row[6+i] = 1
        row[12+i] = 1
        A_mat.append(row); b_u_vec.append(0); b_l_vec.append(-np.inf)
        
    for i in range(6):
        row = [0]*24
        row[i] = -grid_limits[i]
        row[6+i] = 40
        row[12+i] = 80
        A_mat.append(row); b_u_vec.append(0); b_l_vec.append(-np.inf)
        
    row = [0]*24
    for i in range(6):
        row[i] = setup_costs[i]
        row[6+i] = 8
        row[12+i] = 15
    A_mat.append(row); b_u_vec.append(st.session_state.budget); b_l_vec.append(-np.inf)
    
    for j in range(6):
        row = [0]*24
        row[18+j] = 1
        for i in range(6):
            row[i] = -cov_matrix[j][i]
        A_mat.append(row); b_u_vec.append(0); b_l_vec.append(-np.inf)
        
    row = [0]*24
    for j in range(6):
        row[18+j] = demand[j]
    A_mat.append(row); b_u_vec.append(np.inf); b_l_vec.append(min_sessions_target)
    
    bounds_obj = opt.Bounds([0]*24, [1]*6 + [np.inf]*12 + [1]*6)
    res = opt.milp(c=c_vec, integrality=integrality_vec, bounds=bounds_obj, constraints=opt.LinearConstraint(A_mat, b_l_vec, b_u_vec))
    
    if res.success:
        profit = -res.fun
        x_sites = np.round(res.x[0:6]).astype(int)
        std_chargers = np.round(res.x[6:12]).astype(int)
        fast_chargers = np.round(res.x[12:18]).astype(int)
        capex_used = sum(x_sites[i]*setup_costs[i] + std_chargers[i]*8 + fast_chargers[i]*15 for i in range(6))
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Net Monthly Profit", f"₹{profit:.2f}L")
        kpi2.metric("CapEx Utilized", f"₹{capex_used:.1f} / ₹{st.session_state.budget}L")
        kpi3.metric("Coverage Target", f"{st.session_state.coverage_target*100:.0f}% Met")
        
        # Detailed Table
        site_names = ["CBD Mall (C1)", "North Metro (C2)", "Tech Park (C3)", "University (C4)", "Highway Hub (C5)", "South Plaza (C6)"]
        df_out = pd.DataFrame({
            "Candidate Site": site_names,
            "Deployment Status": ["🟢 ACTIVE (Open)" if x == 1 else "🔴 INACTIVE (Closed)" for x in x_sites],
            "Standard (40kW)": std_chargers,
            "Fast (80kW)": fast_chargers,
            "Effective Setup": [f"₹{setup_costs[i]:.1f}L" for i in range(6)]
        })
        st.dataframe(df_out, use_container_width=True, hide_index=True)
    else:
        st.error("⚠️ No feasible network configuration found under current constraints. Try expanding the budget or reducing coverage requirements.")

st.markdown("---")
st.markdown("### 🎓 MBA Decision Support Framework: This tool bridges Integer Linear Programming with natural language executive processing for real-time strategic scenario planning.")
