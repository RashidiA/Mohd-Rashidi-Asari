# Asari-Rashidi 3-Ply Model (Open Source Version)
# License: MIT
import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="Asari-Rashidi 3-Ply Analysis", layout="wide")
st.title("🔬 Asari-Rashidi 3D Lobe: Multi-Ply Analysis")

# --- MATERIAL DATABASE ---
# Standard properties including Carbon Equivalent (CE) [cite: 1]
materials_db = {
    "Mild Steel (JSC270)": {"res_factor": 1.0, "k_mod": 1.0, "ce": 0.08},
    "High Strength (JSC440)": {"res_factor": 1.15, "k_mod": 1.05, "ce": 0.14},
    "DP600 (Dual Phase)": {"res_factor": 1.35, "k_mod": 1.12, "ce": 0.18},
    "DP980 (Ultra High Strength)": {"res_factor": 1.50, "k_mod": 1.20, "ce": 0.24},
    "Boron Steel (Usibor 1500)": {"res_factor": 1.65, "k_mod": 1.25, "ce": 0.35},
    "Trip Steel (TRIP780)": {"res_factor": 1.40, "k_mod": 1.15, "ce": 0.22}
}

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("📋 Stack Configuration")
    mat1 = st.selectbox("Ply 1 (Top)", list(materials_db.keys()))
    t1 = st.slider("Thickness 1 (mm)", 0.5, 3.0, 1.0) [cite: 3]
    
    mat2 = st.selectbox("Ply 2 (Middle/Bottom)", list(materials_db.keys()), index=2)
    t2 = st.slider("Thickness 2 (mm)", 0.5, 3.0, 1.2) [cite: 3]
    
    mat3_choice = st.selectbox("Ply 3 (Optional)", ["NIL"] + list(materials_db.keys()))
    t3 = st.slider("Thickness 3 (mm)", 0.5, 3.0, 1.0) if mat3_choice != "NIL" else 0.0

    st.header("⚙️ Machine Settings")
    is_zinc = st.checkbox("Zinc Coated?") [cite: 2]
    d_tip = st.slider("Tip Diameter (mm)", 4.0, 10.0, 6.0) [cite: 3]
    k_base = st.slider("Base k-factor", 0.10, 0.60, 0.35) [cite: 3]

# --- CALCULATION LOGIC ---
active_plies = [{"mat": mat1, "t": t1, "props": materials_db[mat1]},
                {"mat": mat2, "t": t2, "props": materials_db[mat2]}]
if mat3_choice != "NIL":
    active_plies.append({"mat": mat3_choice, "t": t3, "props": materials_db[mat3_choice]})

# Global Physics [cite: 4]
total_t = sum(p['t'] for p in active_plies)
t_min = min(p['t'] for p in active_plies) [cite: 3]
avg_res = sum(p['t'] * p['props']['res_factor'] for p in active_plies) / total_t
max_ce = max(p['props']['ce'] for p in active_plies)

# Heat Factor
k_final = k_base * avg_res
if is_zinc: k_final *= 0.82 [cite: 4]

# Model Generation [cite: 4, 5]
target_min = 4 * np.sqrt(t_min) [cite: 4]
I, T, F = np.meshgrid(np.linspace(5000, 13000, 20), np.linspace(3, 17, 12), np.linspace(150, 450, 12))
tip_eff = (6.0 / d_tip)**2 
nugget_growth = k_final * ((I * tip_eff)/10000)**2 * (T/10) * (300/F)**0.25 * 5.5
exp_limit = (5.5 * np.sqrt(t_min)) * (F / 300)**0.1 * (d_tip / 6.0)**0.2

# --- UI LAYOUT ---
col1, col2 = st.columns([3, 1])
with col1:
    fig = go.Figure(data=go.Isosurface(
        x=I.flatten(), y=T.flatten(), z=F.flatten(),
        value=nugget_growth.flatten(),
        isomin=target_min, isomax=exp_limit.max(),
        surface_count=3, colorscale='Viridis', opacity=0.4
    ))
    fig.update_layout(scene=dict(xaxis_title='Current (A)', yaxis_title='Cycles', zaxis_title='Force (kg)'))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Results")
    st.metric("Total Thickness", f"{round(total_t, 2)} mm")
    st.metric("Max Carbon Equiv", f"{max_ce}")
    
    # Nugget Offset Logic
    res_vals = [p['props']['res_factor'] for p in active_plies]
    if max(res_vals) != min(res_vals):
        st.warning("⚠️ Nugget Offset: Heat will concentrate toward the higher resistivity sheet.")
    
    if max_ce > 0.3:
        st.error("High CE: Risk of brittle failure.")
    else:
        st.success("Weldability looks good.")