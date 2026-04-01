import streamlit as st

st.set_page_config(page_title="VFSS Report Generator", layout="wide")

st.title("VFSS Report Generator")
st.write("This is the first prototype of the web app.")

patient_name = st.text_input("Patient Name")
consistency = st.selectbox(
    "Select consistency",
    ["Thin liquid", "Slightly thick", "Mildly thick", "Moderately thick", "Puree", "Soft solid", "Regular solid"]
)

finding_options = st.multiselect(
    "Select findings",
    [
        "Anterior spillage",
        "Delayed swallow trigger",
        "Vallecular residue",
        "Pyriform sinus residue",
        "Penetration",
        "Aspiration",
        "Double swallow required",
        "Reduced tongue base retraction"
    ]
)

report = f"""Patient: {patient_name if patient_name else '[Not entered]'}

VFSS was performed with {consistency.lower()} consistency.

Findings:
"""

if finding_options:
    for item in finding_options:
        report += f"- {item}\n"
else:
    report += "- No specific finding selected.\n"

st.subheader("Generated Report")
st.text_area("Report Output", report, height=300)