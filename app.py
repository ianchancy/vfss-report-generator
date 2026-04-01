import streamlit as st

st.set_page_config(page_title="VFSS Report Generator", layout="wide")

st.title("VFSS Report Generator")
st.caption("Clinical version prototype for VFSS reporting")

# -----------------------------
# Helper functions
# -----------------------------
def residue_text(site_vals):
    parts = []
    mapping = {
        "Valleculae": "vallecular residue",
        "Pyriform sinuses": "pyriform sinus residue",
        "Posterior pharyngeal wall": "posterior pharyngeal wall residue",
    }

    for site, phrase in mapping.items():
        severity = site_vals.get(site, "None")
        if severity != "None":
            if severity == "Trace":
                parts.append(f"trace {phrase}")
            elif severity == "Mild":
                parts.append(f"mild {phrase}")
            elif severity == "Moderate":
                parts.append(f"moderate {phrase}")
            elif severity == "Severe":
                parts.append(f"severe {phrase}")
    return parts


def airway_sentence(penetration, aspiration):
    phrases = []

    if penetration == "None":
        pass
    elif penetration == "Transient":
        phrases.append("Transient laryngeal penetration was observed.")
    elif penetration == "Repeated":
        phrases.append("Repeated laryngeal penetration was observed.")
    elif penetration == "To vocal folds":
        phrases.append("Laryngeal penetration to the level of the vocal folds was observed.")

    if aspiration == "None":
        pass
    elif aspiration == "Before swallow":
        phrases.append("Aspiration occurred before swallow initiation.")
    elif aspiration == "During swallow":
        phrases.append("Aspiration occurred during the swallow.")
    elif aspiration == "After swallow":
        phrases.append("Aspiration occurred after the swallow due to pharyngeal residue.")
    elif aspiration == "Silent aspiration":
        phrases.append("Silent aspiration was observed.")

    return " ".join(phrases)


def oral_phase_sentence(findings):
    phrases = []

    if "Anterior spillage" in findings:
        phrases.append("Anterior spillage was noted.")
    if "Reduced bolus control" in findings:
        phrases.append("Reduced oral bolus control was noted.")
    if "Prolonged oral transit" in findings:
        phrases.append("Oral transit was prolonged.")
    if "Piecemal deglutition" in findings:
        phrases.append("Piecemal deglutition was observed.")
    if "Double swallow required" in findings:
        phrases.append("Double swallow was required for clearance.")

    return " ".join(phrases)


def pharyngeal_phase_sentence(findings):
    phrases = []

    if "Delayed swallow trigger" in findings:
        phrases.append("Swallow initiation was delayed.")
    if "Reduced tongue base retraction" in findings:
        phrases.append("Reduced tongue base retraction was noted.")
    if "Reduced hyolaryngeal excursion" in findings:
        phrases.append("Reduced hyolaryngeal excursion was noted.")
    if "Reduced epiglottic inversion" in findings:
        phrases.append("Reduced epiglottic inversion was noted.")
    if "Reduced pharyngeal contraction" in findings:
        phrases.append("Reduced pharyngeal contraction was noted.")
    if "Cricopharyngeal dysfunction suspected" in findings:
        phrases.append("Possible cricopharyngeal dysfunction was noted.")

    return " ".join(phrases)


def strategy_sentences(strategies):
    mapping = {
        "Chin tuck": "chin tuck",
        "Head turn": "head turn",
        "Effortful swallow": "effortful swallow",
        "Double swallow": "double swallow",
        "Small sips/bites": "small sips/bites",
        "Alternate solid/liquid": "alternating solids and liquids",
        "Slow rate": "slow rate of intake",
    }
    results = [mapping[s] for s in strategies if s in mapping]
    return results


def build_consistency_paragraph(consistency_name, entry):
    sentences = []

    delivery = entry["delivery"]
    volume = entry["volume"]

    intro = f"For {consistency_name.lower()} presented via {delivery.lower()} ({volume.lower()}),"
    sentences.append(intro)

    oral = oral_phase_sentence(entry["findings"])
    pharyngeal = pharyngeal_phase_sentence(entry["findings"])
    residue = residue_text(entry["residue"])
    airway = airway_sentence(entry["penetration"], entry["aspiration"])

    detail_parts = []
    if oral:
        detail_parts.append(oral)
    if pharyngeal:
        detail_parts.append(pharyngeal)
    if residue:
        detail_parts.append(" ".join([f"{x} was noted." for x in residue]))
    if airway:
        detail_parts.append(airway)

    if detail_parts:
        sentences.append(" ".join(detail_parts))
    else:
        sentences.append("No significant abnormality was identified.")

    return " ".join(sentences)


def build_impression(all_entries):
    abnormal_consistencies = []
    aspiration_consistencies = []
    penetration_consistencies = []
    residue_consistencies = []

    for c_name, entry in all_entries.items():
        has_abnormal = False

        if entry["findings"]:
            has_abnormal = True
        if any(v != "None" for v in entry["residue"].values()):
            has_abnormal = True
            residue_consistencies.append(c_name)
        if entry["penetration"] != "None":
            has_abnormal = True
            penetration_consistencies.append(c_name)
        if entry["aspiration"] != "None":
            has_abnormal = True
            aspiration_consistencies.append(c_name)

        if has_abnormal:
            abnormal_consistencies.append(c_name)

    lines = []

    if not abnormal_consistencies:
        lines.append("Functional oropharyngeal swallowing with no significant penetration, aspiration, or residue identified during the tested consistencies.")
        return " ".join(lines)

    lines.append(
        f"Oropharyngeal dysphagia was noted across the following tested consistencies: {', '.join(abnormal_consistencies)}."
    )

    if penetration_consistencies:
        lines.append(
            f"Laryngeal penetration was observed with {', '.join(penetration_consistencies)}."
        )

    if aspiration_consistencies:
        lines.append(
            f"Aspiration was observed with {', '.join(aspiration_consistencies)}."
        )

    if residue_consistencies:
        lines.append(
            f"Pharyngeal residue was present with {', '.join(residue_consistencies)}."
        )

    return " ".join(lines)


def build_recommendations(global_strategies, aspiration_present):
    recs = []

    if aspiration_present:
        recs.append("Consider diet modification and strict aspiration precautions based on overall clinical context.")

    strategy_list = strategy_sentences(global_strategies)
    if strategy_list:
        recs.append("Compensatory strategies trialed with potential benefit include: " + ", ".join(strategy_list) + ".")

    recs.append("Clinical correlation is recommended.")
    recs.append("Please integrate these findings with bedside swallowing performance and overall pulmonary / nutritional status.")

    return recs


# -----------------------------
# Input area
# -----------------------------
st.header("Study Information")

col1, col2 = st.columns(2)
with col1:
    patient_name = st.text_input("Patient Name")
    mrn = st.text_input("MRN / ID")
with col2:
    study_date = st.date_input("Study Date")
    examiner = st.text_input("Examiner")

tested_consistencies = st.multiselect(
    "Tested consistencies",
    [
        "Thin liquid",
        "Slightly thick liquid",
        "Mildly thick liquid",
        "Moderately thick liquid",
        "Extremely thick liquid",
        "Puree",
        "Soft solid",
        "Regular solid",
    ],
    default=["Thin liquid"],
)

st.header("Consistency-specific Findings")

all_entries = {}

for consistency in tested_consistencies:
    with st.expander(consistency, expanded=True):
        c1, c2 = st.columns(2)

        with c1:
            delivery = st.selectbox(
                f"{consistency} - Delivery method",
                ["Teaspoon", "Cup sip", "Straw", "Self-fed", "Assisted feeding"],
                key=f"{consistency}_delivery",
            )

            volume = st.selectbox(
                f"{consistency} - Volume",
                ["Small", "Moderate", "Large"],
                key=f"{consistency}_volume",
            )

            findings = st.multiselect(
                f"{consistency} - Findings",
                [
                    "Anterior spillage",
                    "Reduced bolus control",
                    "Prolonged oral transit",
                    "Piecemal deglutition",
                    "Delayed swallow trigger",
                    "Reduced tongue base retraction",
                    "Reduced hyolaryngeal excursion",
                    "Reduced epiglottic inversion",
                    "Reduced pharyngeal contraction",
                    "Double swallow required",
                    "Cricopharyngeal dysfunction suspected",
                ],
                key=f"{consistency}_findings",
            )

        with c2:
            penetration = st.selectbox(
                f"{consistency} - Penetration",
                ["None", "Transient", "Repeated", "To vocal folds"],
                key=f"{consistency}_penetration",
            )

            aspiration = st.selectbox(
                f"{consistency} - Aspiration",
                ["None", "Before swallow", "During swallow", "After swallow", "Silent aspiration"],
                key=f"{consistency}_aspiration",
            )

            st.markdown("**Residue severity**")
            valleculae = st.selectbox(
                f"{consistency} - Valleculae",
                ["None", "Trace", "Mild", "Moderate", "Severe"],
                key=f"{consistency}_valleculae",
            )
            pyriform = st.selectbox(
                f"{consistency} - Pyriform sinuses",
                ["None", "Trace", "Mild", "Moderate", "Severe"],
                key=f"{consistency}_pyriform",
            )
            ppw = st.selectbox(
                f"{consistency} - Posterior pharyngeal wall",
                ["None", "Trace", "Mild", "Moderate", "Severe"],
                key=f"{consistency}_ppw",
            )

        all_entries[consistency] = {
            "delivery": delivery,
            "volume": volume,
            "findings": findings,
            "penetration": penetration,
            "aspiration": aspiration,
            "residue": {
                "Valleculae": valleculae,
                "Pyriform sinuses": pyriform,
                "Posterior pharyngeal wall": ppw,
            },
        }

st.header("Compensatory Strategies / Global Recommendations")

global_strategies = st.multiselect(
    "Strategies trialed / considered",
    [
        "Chin tuck",
        "Head turn",
        "Effortful swallow",
        "Double swallow",
        "Small sips/bites",
        "Alternate solid/liquid",
        "Slow rate",
    ],
)

free_text_comment = st.text_area("Additional comments", height=120)

# -----------------------------
# Generate report
# -----------------------------
report_lines = []

report_lines.append("VFSS REPORT")
report_lines.append("")
report_lines.append(f"Patient Name: {patient_name if patient_name else '[Not entered]'}")
report_lines.append(f"MRN / ID: {mrn if mrn else '[Not entered]'}")
report_lines.append(f"Study Date: {study_date}")
report_lines.append(f"Examiner: {examiner if examiner else '[Not entered]'}")
report_lines.append("")

report_lines.append("Procedure:")
report_lines.append(
    "Videofluoroscopic swallowing study was performed in lateral view with selected consistencies and delivery methods as outlined below."
)
report_lines.append("")

report_lines.append("Findings by Consistency:")
if tested_consistencies:
    for c in tested_consistencies:
        report_lines.append(build_consistency_paragraph(c, all_entries[c]))
else:
    report_lines.append("No consistency selected.")
report_lines.append("")

report_lines.append("Impression:")
report_lines.append(build_impression(all_entries if tested_consistencies else {}))
report_lines.append("")

aspiration_present = any(
    entry["aspiration"] != "None" for entry in all_entries.values()
)

report_lines.append("Recommendations:")
for rec in build_recommendations(global_strategies, aspiration_present):
    report_lines.append(f"- {rec}")

if free_text_comment.strip():
    report_lines.append("")
    report_lines.append("Additional Comments:")
    report_lines.append(free_text_comment.strip())

report_text = "\n".join(report_lines)

# -----------------------------
# Output
# -----------------------------
st.header("Generated Report")
st.text_area("Report Output", report_text, height=650)

st.download_button(
    label="Download report as TXT",
    data=report_text,
    file_name="vfss_report.txt",
    mime="text/plain",
)