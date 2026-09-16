
import streamlit as st
import pandas as pd
import numpy as np
import scipy.optimize as opt

st.set_page_config(page_title="El Dorado EV Charging - AI Decision Support System", layout="wide")

# Custom CSS styling for professional MBA look (Dark Green & Base White)
st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #1B4D3E; font-family: 'Helvetica Neue', sans-serif; }
    .metric-card { background-color: #E8F5E9; padding: 20px; border-radius: 10px; border-left: 5px solid #1B4D3E; }
    .chat-box { background-color: #F1F8F6; padding: 15px; border-radius: 8px; border: 1px solid #C8E6C9; }
    </style>
""", unsafe_allow_html=True)

st.title("🌱 El Dorado EV Charging Network: AI Decision Support System")
st.markdown("### Executive Intelligence Dashboard & Natural Language Parameter Control")

# Initialize Session State for parameters if not already present
if 'budget' not in st.session_state:
    st.session_state.budget = 450.0
if 'subsidy_north' not in st.session_state:
    st.session_state.subsidy_north = 0.30
if 'subsidy_south' not in st.session_state:
    st.session_state.subsidy_south = 0.30
if 'demand_growth' not in st.session_state:
    st.session_state.demand_growth = 1.0
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello Manager. I am your AI Decision Support Assistant for El Dorado EV Network. Type a prompt below (e.g., *'Increase budget to 500 lakhs'*, *'Set residential subsidy to 40%'*, or *'Run optimization with 20% demand growth'*) and I will automatically adjust the model parameters and re-run the solver!"}
    ]

# Sidebar for manual controls
st.sidebar.header("🎛️ Model Master Controls")
st.session_state.budget = st.sidebar.slider("Total Capital Budget (Lakhs)", 300.0, 700.0, float(st.session_state.budget), 10.0)
st.session_state.subsidy_north = st.sidebar.slider("North Metro Subsidy (%)", 0.0, 0.6, float(st.session_state.subsidy_north), 0.05)
st.session_state.subsidy_south = st.sidebar.slider("South Plaza Subsidy (%)", 0.0, 0.6, float(st.session_state.subsidy_south), 0.05)
st.session_state.demand_growth = st.sidebar.slider("Demand Multiplier", 0.8, 1.5, float(st.session_state.demand_growth), 0.05)

# AI Prompt Processing Function
def process_ai_command(prompt):
    prompt_lower = prompt.lower()
    response_msg = ""
    
    if "budget" in prompt_lower:
        import re
        numbers = re.findall(r'\d+', prompt)
        if numbers:
            new_val = float(numbers[0])
            if 300 <= new_val <= 800:
                st.session_state.budget = new_val
                response_msg = f"✅ AI Parameter Update: Capital budget successfully updated to **₹{new_val} Lakhs**. Re-running ILP optimizer..."
            else:
                response_msg = "⚠️ Budget must be between ₹300L and ₹800L."
        else:
                response_msg = "⚠️ Please specify a valid budget amount (e.g., 'Set budget to 500')."
                
    elif "subsidy" in prompt_lower:
        import re
        numbers = re.findall(r'\d+', prompt)
        if numbers:
            val = float(numbers[0])
            if val > 1: val = val / 100.0 # handle percentage like 40 -> 0.4
            if 0 <= val <= 0.6:
                st.session_state.subsidy_north = val
                st.session_state.subsidy_south = val
                response_msg = f"✅ AI Parameter Update: Residential subsidies (North & South) updated to **{val*100:.0f}%**. Re-running optimizer..."
            else:
                response_msg = "⚠️ Subsidy must be between 0% and 60%."
        else:
            response_msg = "⚠️ Please specify a subsidy percentage (e.g., 'Set subsidy to 40%')."
            
    elif "demand" in prompt_lower or "growth" in prompt_lower:
        import re
        numbers = re.findall(r'\d+', prompt)
        if numbers:
            val = float(numbers[0])
            if val > 10: val = val / 100.0 + 1.0 # handle 20% -> 1.2
            if 0.5 <= val <= 2.0:
                st.session_state.demand_growth = val
                response_msg = f"✅ AI Parameter Update: Demand growth multiplier updated to **{val}x**. Re-running optimizer..."
            else:
                response_msg = "⚠️ Demand multiplier out of bounds."
        else:
            response_msg = "⚠️ Please specify demand growth (e.g., 'Increase demand by 20%')."
    else:
        response_msg = f"🤖 I processed your query: *'{prompt}'*. You can ask me to adjust budget, subsidies, or demand growth, and I will re-optimize the network!"
        
    return response_msg

# Layout: Two Columns (Left: Chat & Controls, Right: Optimization Results & KPIs)
col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown("### 💬 AI Manager Assistant Chat")
    
    # Display Chat History
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**👤 Manager:** {message['content']}")
        else:
            st.markdown(f"**🤖 AI DSS:** {message['content']}")
            
    # User Typing Area
    with st.form(key="chat_form", clear_on_submit=True):
        user_prompt = st.text_input("Type a command or question for the AI (e.g., 'Set budget to 500 lakhs' or 'Make subsidy 40%'):")
        submit_button = st.form_submit_button(label="Send to AI Assistant")
        
        if submit_button and user_prompt:
            st.session_state.chat_history.append({"role": "user", "content": user_prompt})
            ai_reply = process_ai_command(user_prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
            st.rerun()

with col2:
    st.markdown("### 📈 Live Optimization Engine Results")
    
    # Run Optimization Solver in Python using SciPy MILP based on current session state
    setup_costs = [70.0, 48.0 * (1 - st.session_state.subsidy_north), 65.0, 42.0, 55.0, 45.0 * (1 - st.session_state.subsidy_south)]
    op_costs = [3.2, 2.4, 3.5, 2.1, 2.8, 2.3]
    grid_limits = [700, 450, 800, 400, 900, 500]
    max_chargers_list = [14, 9, 16, 8, 18, 10]
    base_demand = [180, 120, 220, 100, 160, 140]
    demand = [d * st.session_state.demand_growth for d in base_demand]
    total_demand_val = sum(demand)
    min_coverage_target = 0.9 * sum(base_demand) # 828 sessions baseline
    
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
        row[i] = -max_chargers_list[i]
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
    A_mat.append(row); b_u_vec.append(np.inf); b_l_vec.append(min_coverage_target)
    
    bounds_obj = opt.Bounds([0]*24, [1]*6 + [np.inf]*12 + [1]*6)
    res = opt.milp(c=c_vec, integrality=integrality_vec, bounds=bounds_obj, constraints=opt.LinearConstraint(A_mat, b_l_vec, b_u_vec))
    
    if res.success:
        profit = -res.fun
        x_sites = np.round(res.x[0:6]).astype(int)
        std_chargers = np.round(res.x[6:12]).astype(int)
        fast_chargers = np.round(res.x[12:18]).astype(int)
        
        capex_used = sum(x_sites[i]*setup_costs[i] + std_chargers[i]*8 + fast_chargers[i]*15 for i in range(6))
        
        # Display Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Net Monthly Profit", f"₹{profit:.2f} Lakhs")
        m2.metric("CapEx Utilized", f"₹{capex_used:.1f} / ₹{st.session_state.budget}L")
        m3.metric("Status", "🟢 Optimal Solution Found")
        
        # Site Deployment Table
        site_names = ["CBD Mall (C1)", "North Metro (C2)", "Tech Park (C3)", "University (C4)", "Highway Hub (C5)", "South Plaza (C6)"]
        df_results = pd.DataFrame({
            "Site Name": site_names,
            "Status": ["Open" if x == 1 else "Closed" for x in x_sites],
            "Standard Chargers": std_chargers,
            "Fast Chargers": fast_chargers,
            "Effective Setup (Lakhs)": [f"₹{setup_costs[i]:.1f}" for i in range(6)]
        })
        st.table(df_results)
    else:
        st.error("⚠️ No feasible solution found under current constraints and budget. Try increasing budget or adjusting subsidies.")

st.markdown("---")
st.markdown("### 🎓 MBA Defense Note: This Decision Support System bridges static Excel solvers with conversational AI, allowing executives to dynamically test policy scenarios in real-time.")
