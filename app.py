# Asari-Rashidi 3-Ply Model (Open Source Version)
# License: MIT
import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="Asari-Rashidi 3-Ply Analysis", layout="wide")
st.title("🔬 Asari-Rashidi 3D Lobe: Multi-Ply Analysis")

# --- MATERIAL DATABASE ---
# [cite_start]Standard properties including Carbon Equivalent (CE) [cite: 1]
materials_db = {
    "Mild Steel (JSC270)": {"res_factor": 1.0, "k_mod": 1.0, "ce": 0.08},
    "High Strength (JSC440)": {"res_factor": 1.15, "k_mod": 1.05, "ce": 0.14},
    "DP600 (Dual Phase)": {"res_factor": 1.35, "k_mod": 1.12, "ce": 0.18},
    "DP980 (Ultra High Strength)": {"res_factor": 1.50, "k_mod": 1.20, "ce": 0.24},
    "Boron Steel (Usibor 1500)": {"res_factor": 1.65, "k_mod": 1.25, "ce": 0.35},
    "Trip Steel (TRIP780)": {"res_factor": 1.40, "k_mod": 1.15, "ce": 0.22}
}

# --- RESET LOGIC ---
if st.sidebar.button("🔄 Reset to Default"):
    st.rerun()

# --- USER INPUT PANEL ---
with st.sidebar:
    st.header("1. Ply 1 (Top)")
    mat1 = st.selectbox("Material 1", list(materials_db.keys()))
    t1 = st.slider("Thickness 1 (mm)", 0.5, 3.0, 1.0)
    
    st.header("2. Ply 2 (Middle/Bottom)")
    mat2 = st.selectbox("Material 2", list(materials_db.keys()), index=2)
    t2 = st.slider("Thickness 2 (mm)", 0.5, 3.0, 1.2)
    
    st.header("3. Ply 3 (Optional Bottom)")
    mat3_choice = st.selectbox("Material 3", ["NIL"] + list(materials_db.keys()), index=0)
    t3 = st.slider("Thickness 3 (mm)", 0.5, 3.0, 1.0) if mat3_choice != "NIL" else 0.0

    st.header("4. Machine Settings")
    [cite_start]is_zinc = st.checkbox("Zinc Coated (GA/GI)?") [cite: 2]
    [cite_start]d_tip = st.slider("Tip Diameter (mm)", 4.0, 10.0, 6.0) [cite: 3]
    [cite_start]k_base = st.slider("Base k-factor", 0.10, 0.60, 0.35) [cite: 3]
    [cite_start]expulsion_sens = st.slider("Expulsion Limit Factor", 1.2, 1.8, 1.4) [cite: 3]

# --- CALCULATION ENGINE ---
active_plies = [
    {"mat": mat1, "t": t1, "props": materials_db[mat1]},
    {"mat": mat2, "t": t2, "props": materials_db[mat2]}
]
if mat3_choice != "NIL":
    active_plies.append({"mat": mat3_choice, "t": t3, "props": materials_db[mat3_choice]})

# Global Stack Physics
total_t = sum(p['t'] for p in active_plies)
[cite_start]t_min = min(p['t'] for p in active_plies) [cite: 3]
avg_res = sum(p['t'] * p['props']['res_factor'] for p in active_plies) / total_t
avg_k_mod = sum(p['t'] * p['props']['k_mod'] for p in active_plies) / total_t
max_ce = max(p['props']['ce'] for p in active_plies)

# Final Heat Factor
[cite_start]k_final = k_base * avg_k_mod * avg_res [cite: 4]
if is_zinc:
    [cite_start]k_final *= 0.82 [cite: 4]

# Weld Lobe Limits
[cite_start]target_min = 4 * np.sqrt(t_min) [cite: 4]

# Generate 3D Mesh
[cite_start]currents = np.linspace(5000, 13000, 25) [cite: 4]
[cite_start]times = np.linspace(3, 17, 15) [cite: 4]
[cite_start]forces = np.linspace(100, 450, 15) [cite: 4]
[cite_start]I, T, F = np.meshgrid(currents, times, forces) [cite: 4]

# [cite_start]Asari-Rashidi Growth Model Logic [cite: 4]
tip_eff = (6.0 / d_tip)**2 
nugget_growth = k_final * ((I * tip_eff)/10000)**2 * (T/10) * (300/F)**0.25 * 5.5

# [cite_start]Expulsion Limit Logic [cite: 4, 5]
exp_limit_mesh = (5.5 * np.sqrt(t_min)) * (F / 300)**0.1 * (d_tip / 6.0)**0.2 * (expulsion_sens / 1.4)

# --- VISUALIZATION ---
fig = go.Figure(data=go.Isosurface(
    x=I.flatten(), y=T.flatten(), z=F.flatten(),
    value=nugget_growth.flatten(),
    isomin=target_min, isomax=exp_limit_mesh.max(),
    surface_count=3, colorscale='Plasma', opacity=0.5,
    caps=dict(x_show=False, y_show=False),
    colorbar_title="Dia (mm)"
[cite_start])) [cite: 5]

fig.update_layout(
    scene=dict(xaxis_title='Current (A)', yaxis_title='Time (Cycles)', zaxis_title='Force (kg)'),
    margin=dict(l=0, r=0, b=0, t=40), height=700
[cite_start]) [cite: 5]

# --- DISPLAY ---
[cite_start]col1, col2 = st.columns([3, 1]) [cite: 6]
with col1:
    [cite_start]st.plotly_chart(fig, use_container_width=True) [cite: 6]

with col2:
    st.subheader("Weldability Report")
    st.write(f"**Total Stack:** {round(total_t, 2)} mm")
    [cite_start]st.metric("Effective k-Factor", round(k_final, 3)) [cite: 6]
    [cite_start]st.metric("Min Nugget Target", f"{round(target_min, 2)} mm") [cite: 6]
    
    st.write(f"**Max Carbon Equiv:** {max_ce}")
    if max_ce > 0.3:
        st.error("⚠️ HIGH RISK: Brittle Weld.")
    elif max_ce > 0.15:
        st.warning("MODERATE RISK: Possible brittle zones.")
    else:
        st.success("LOW RISK: Ductile weld.")

    if mat3_choice == "NIL":
        st.info("Mode: 2-Ply Stack")
    else:
        st.info("Mode: 3-Ply Stack")
