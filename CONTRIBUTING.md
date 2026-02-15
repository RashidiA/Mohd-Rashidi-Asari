
# 🤝 Contributing to the Asari-Rashidi 3D Lobe

Thank you for your interest in improving the **Asari-Rashidi Energy Balance Model**. To maintain the scientific integrity of this tool, please follow these guidelines when contributing.

## 📈 Adding New Material Grades

To add a new material to the `materials_db` in `app.py`, we require specific physical properties. Please provide:

1. **Resistivity Factor ():** Relative to Mild Steel ().
2. **Thermal Modifier ():** How the material's thermal conductivity affects nugget growth.
3. **Carbon Equivalent ():** Calculated using the formula:



### Example Entry Format:

```python
"Your Steel Name": {"res_factor": 1.45, "k_mod": 1.18, "ce": 0.21}

```

---

## 🛠️ Code Standards

* **Physical Accuracy:** Any changes to the core logic in the `Calculation Engine` must be accompanied by a citation or experimental data.
* **Dependencies:** If you add a new library, ensure you update the `requirements.txt` file.
* **UI Consistency:** Keep the 3-ply selector logic intact so the app remains compatible with complex automotive stack-ups.

---

## 🔬 Research & PhD Collaboration

If you are a researcher using this model for academic purposes:

* **Validation:** We welcome "Pull Requests" that include experimental validation data (e.g., actual vs. predicted nugget diameters).
* **Nugget Offset:** We are specifically looking for contributors to help refine the 3-ply offset logic.

---

## 📝 How to Submit a Change

1. **Fork** the repository.
2. Create a **Feature Branch** (`git checkout -b feature/NewSteelGrade`).
3. **Commit** your changes with a clear description.
4. Open a **Pull Request** and link any relevant research papers.

---

