# Asari-Rashidi 3-Ply Model (Open Source Version)
# License: MIT
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd 

# --- CONFIGURATION ---
st.set_page_config(page_title="Asari-Rashidi 3-Ply Analysis", layout="wide")
st.title("🔬 Asari-Rashidi 3D Lobe: Multi-Ply Analysis")

# --- MATERIAL DATABASE ---
materials_db = {
    "Mild Steel (JSC270)": {"res_factor": 1.0, "k_mod": 1.0, "ce": 0.08},
    "High Strength (JSC440)": {"res_factor": 1.15, "k_mod": 1.05, "ce": 0.14},
    "DP600 (Dual Phase)": {"res_factor": 1.35, "k_mod": 1.12, "ce": 0.18},
    "DP980 (Ultra High Strength)": {"res_factor": 1.50, "k_mod": 1.20, "ce": 0.24},
    "Boron Steel (Usibor 1500)": {"res_factor": 1.65, "k_mod": 1.25, "ce": 0.35},
    "Trip Steel (TRIP780)": {"res_factor": 1.40, "k_mod": 1.15, "ce": 0.22}
}

# --- USER INPUT PANEL ---
with st.sidebar:
    st.header("🌐 View Optimization Mode")
    graph_mode = st.radio(
        "Select Visualization Type",
        options=["Complete 3D Volumetric Lobe", "2D Plane Slice Cross-Section"]
    )
    
    if graph_mode == "2D Plane Slice Cross-Section":
        slice_plane = st.selectbox(
            "Target Orientation Plane",
            options=["X-Y Plane (Current vs. Time at Fixed Force)", 
                     "X-Z Plane (Current vs. Force at Fixed Time)"]
        )
        if "X-Y Plane" in slice_plane:
            slice_force = st.slider("Slice Location: Fixed Force (kg)", 100, 450, 250, step=10)
        else:
            slice_time = st.slider("Slice Location: Fixed Time (Cycles)", 3, 17, 10, step=1)

    st.divider()
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
    is_zinc = st.checkbox("Zinc Coated (GA/GI)?")
    d_tip = st.slider("Tip Diameter (mm)", 4.0, 10.0, 6.0)
    k_base = st.slider("Base k-factor", 0.10, 0.60, 0.35)
    expulsion_sens = st.slider("Expulsion Limit Factor", 1.2, 1.8, 1.4)

# --- CALCULATION ENGINE ---
active_plies = [
    {"mat": mat1, "t": t1, "props": materials_db[mat1]},
    {"mat": mat2, "t": t2, "props": materials_db[mat2]}
]
if mat3_choice != "NIL":
    active_plies.append({"mat": mat3_choice, "t": t3, "props": materials_db[mat3_choice]})

total_t = sum(p['t'] for p in active_plies)
t_min = min(p['t'] for p in active_plies)
avg_res = sum(p['t'] * p['props']['res_factor'] for p in active_plies) / total_t
avg_k_mod = sum(p['t'] * p['props']['k_mod'] for p in active_plies) / total_t
max_ce = max(p['props']['ce'] for p in active_plies)

k_final = k_base * avg_k_mod * avg_res
if is_zinc:
    k_final *= 0.82

target_min = 4 * np.sqrt(t_min)

# Generate 3D Space Matrices
currents = np.linspace(5000, 13000, 50)  # Upped density for cleaner 2D slicing lines
times = np.linspace(3, 17, 40)
forces = np.linspace(100, 450, 40)

# --- GRAPH GENERATION BASE LAYER ---
if graph_mode == "Complete 3D Volumetric Lobe":
    I, T, F = np.meshgrid(currents, times, forces)
    tip_eff = (6.0 / d_tip)**2 
    nugget_growth = k_final * ((I * tip_eff)/10000)**2 * (T/10) * (300/F)**0.25 * 5.5
    exp_limit_mesh = (5.5 * np.sqrt(t_min)) * (F / 300)**0.1 * (d_tip / 6.0)**0.2 * (expulsion_sens / 1.4)

    fig = go.Figure(data=go.Isosurface(
        x=I.flatten(), y=T.flatten(), z=F.flatten(),
        value=nugget_growth.flatten(),
        isomin=target_min, isomax=exp_limit_mesh.max(),
        surface_count=3, colorscale='Plasma', opacity=0.5,
        caps=dict(x_show=False, y_show=False),
        colorbar_title="Dia (mm)"
    ))
    fig.update_layout(
        scene=dict(xaxis_title='Current (A)', yaxis_title='Time (Cycles)', zaxis_title='Force (kg)'),
        margin=dict(l=0, r=0, b=0, t=40), height=700
    )

else:
    # --- 2D SECTIONING PROCESSING LAYER ---
    tip_eff = (6.0 / d_tip)**2
    
    if "X-Y Plane" in slice_plane:
        # Fixed Force (Z Axis), Vary Current (X) and Time (Y)
        I_2d, T_2d = np.meshgrid(currents, times)
        F_fixed = slice_force
        
        nugget_growth_2d = k_final * ((I_2d * tip_eff)/10000)**2 * (T_2d/10) * (300/F_fixed)**0.25 * 5.5
        exp_limit_2d = (5.5 * np.sqrt(t_min)) * (F_fixed / 300)**0.1 * (d_tip / 6.0)**0.2 * (expulsion_sens / 1.4)
        
        fig = go.Figure()
        
        # Heatmap Background Contours
        fig.add_trace(go.Contour(
            x=currents, y=times, z=nugget_growth_2d,
            colorscale='Plasma',
            colorbar=dict(title='Dia (mm)'),
            contours=dict(showlabels=True, labelfont=dict(size=12, color='white'))
        ))
        
        # Minimum Nugget Boundary Line (4*sqrt(t))
        fig.add_trace(go.Contour(
            x=currents, y=times, z=nugget_growth_2d,
            contours_type='constraint',
            contours=dict(type='equal', value=target_min),
            line=dict(color='cyan', width=4),
            name=f'Min Nugget ({round(target_min,2)}mm)'
        ))
        
        # Expulsion Upper Boundary Limit Line
        fig.add_trace(go.Contour(
            x=currents, y=times, z=nugget_growth_2d,
            contours_type='constraint',
            contours=dict(type='equal', value=exp_limit_2d),
            line=dict(color='red', width=4, dash='dash'),
            name=f'Expulsion Bound ({round(exp_limit_2d,2)}mm)'
        ))
        
        fig.update_layout(
            title=f"2D Cross-Section (Weld Lobe Window) at Force = {F_fixed} kg",
            xaxis_title="Welding Current (A)",
            yaxis_title="Welding Time (Cycles)",
            height=700,
            showlegend=True,
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0.5)")
        )
        
    else:
        # Fixed Time (Y Axis), Vary Current (X) and Force (Z)
        I_2d, F_2d = np.meshgrid(currents, forces)
        T_fixed = slice_time
        
        nugget_growth_2d = k_final * ((I_2d * tip_eff)/10000)**2 * (T_fixed/10) * (300/F_2d)**0.25 * 5.5
        exp_limit_2d = (5.5 * np.sqrt(t_min)) * (F_2d / 300)**0.1 * (d_tip / 6.0)**0.2 * (expulsion_sens / 1.4)
        
        fig = go.Figure()
        
        # Heatmap Background Contours
        fig.add_trace(go.Contour(
            x=currents, y=forces, z=nugget_growth_2d,
            colorscale='Plasma',
            colorbar=dict(title='Dia (mm)'),
            contours=dict(showlabels=True, labelfont=dict(size=12, color='white'))
        ))
        
        # Minimum Nugget Boundary Line
        fig.add_trace(go.Contour(
            x=currents, y=forces, z=nugget_growth_2d,
            contours_type='constraint',
            contours=dict(type='equal', value=target_min),
            line=dict(color='cyan', width=4),
            name=f'Min Nugget ({round(target_min,2)}mm)'
        ))
        
        # Expulsion Boundary Line (Dynamic along the profile)
        # For non-flat boundary limits, we match where nugget growth hits the limit values
        fig.add_trace(go.Contour(
            x=currents, y=forces, z=nugget_growth_2d - exp_limit_2d,
            contours_type='constraint',
            contours=dict(type='equal', value=0),
            line=dict(color='red', width=4, dash='dash'),
            name='Expulsion Bound Line'
        ))
        
        fig.update_layout(
            title=f"2D Cross-Section (Weld Lobe Window) at Time = {T_fixed} Cycles",
            xaxis_title="Welding Current (A)",
            yaxis_title="Welding Force (kg)",
            height=700,
            showlegend=True,
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0.5)")
        )

# --- DISPLAY & EXPORT ---
col1, col2 = st.columns([3, 1])
with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Weldability Report")
    st.metric("Total Thickness", f"{round(total_t, 2)} mm")
    st.metric("Effective k-Factor", round(k_final, 3))
    st.metric("Min Nugget Target", f"{round(target_min, 2)} mm")
    
    # Brittle Failure Risk Assessment
    risk_level = "Low"
    if max_ce > 0.3:
        risk_level = "High"
        st.error(f"⚠️ {risk_level} RISK: Brittle Weld.")
    elif max_ce > 0.15:
        risk_level = "Moderate"
        st.warning(f"⚠️ {risk_level} RISK: Possible brittle zones.")
    else:
        st.success(f"✅ {risk_level} RISK: Ductile weld.")

    # --- CSV DOWNLOAD LOGIC ---
    report_data = {
        "Parameter": ["Ply 1 Material", "Ply 1 Thick", "Ply 2 Material", "Ply 2 Thick", 
                      "Ply 3 Material", "Ply 3 Thick", "Total Thickness", 
                      "Effective k-factor", "Max CE", "Weldability Risk"],
        "Value": [mat1, t1, mat2, t2, mat3_choice, t3, total_t, k_final, max_ce, risk_level]
    }
    df = pd.DataFrame(report_data)
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Download Results (CSV)",
        data=csv,
        file_name="weld_analysis_report.csv",
        mime="text/csv",
    )
