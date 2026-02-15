
# Asari-Rashidi 3D Lobe: Multi-Ply Automotive Analysis 🔬

## Overview

This open-source tool provides a 3D visualization of the welding process window (Lobe) for automotive steel grades. It utilizes the **Asari-Rashidi Nugget Growth Model** to predict the relationship between Current, Time, and Force across 2-ply and 3-ply metal stacks.

The app specifically addresses modern automotive challenges, such as:

* 
**Dissimilar Material Stacks:** Calculating heat generation when mixing Mild Steel with Ultra-High-Strength Steel (UHSS).


* 
**3-Ply Combinations:** Providing flexibility for complex assembly joins (with an optional 3rd layer).


* 
**Weldability Safety:** Real-time Carbon Equivalent (CE) monitoring to prevent brittle weld failures.



## Features

* 
**Dynamic Material Library:** Includes standard grades like JSC270, DP600, DP980, and Boron Steel (Usibor 1500).


* 
**2-Ply & 3-Ply Modes:** Select "NIL" for the third layer to revert to a standard 2-sheet calculation.


* **Physics-Based Calculations:**
* 
**Weighted k-Factor:** Adjusts heat generation based on the resistivity and thickness of each ply in the stack.


* 
**Zinc Coating Factor:** Automatically adjusts contact resistance for GA/GI coated steels.


* 
**Expulsion Limit:** Predicts the upper boundary of the weld lobe where excessive heat causes metal splashing.




* 
**Interactive 3D Visualization:** Explore the weldable volume using a Plotly-powered isosurface.



## Installation & Local Setup

To run this project locally, ensure you have Python installed, then follow these steps:

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/asari-rashidi-3d-lobe.git
cd asari-rashidi-3d-lobe

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Run the app:**
```bash
streamlit run app.py

```



## Technical Background

The model calculates the nugget diameter based on the energy input formula:


Where  is the thickness-weighted resistivity factor of the entire stack.

## License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

