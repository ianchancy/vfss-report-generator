# ===== MODULE START =====
import streamlit as st

# -----------------------------
# Constants
# -----------------------------
CONSISTENCY_OPTIONS = [
    "thin fluid",
    "slightly thick fluid",
    "mildly thick fluid",
    "moderately thick fluid",
    "extremely thick fluid",
    "puree",
    "minced and moist diet",
    "soft and bite-sized diet",
    "easy-to-chew diet",
    "regular diet",
    "other",
]

DELIVERY_OPTIONS = [
    "teaspoon",
    "tablepoon" if False else "tablespoon",  # keeps code readable while preserving valid option only
    "half tablespoon",
    "cup drinking",
    "cup sip",
    "sip with straw",
    "straw",
    "other",
]

EVENT_TYPE_OPTIONS = [
    "trace penetration",
    "penetration",
    "aspiration",
    "silent aspiration",
]

TIMING_OPTIONS = [
    "before swallow",
    "during swallow",
    "after swallow",
]

AMOUNT_OPTIONS = [
    "trace",
    "small",
    "mild",
    "moderate",
    "large",
]

RESPONSE_OPTIONS = [
    "fully ejected",
    "partially ejected",
    "not ejected",
    "cough present",
    "no cough response",
    "unable to follow commands to cough",
]

SUMMARY_DEFAULTS = {
    "no aspiration or penetration overall": False,
    "no aspiration or penetration for other consistencies": False,
    "coughing not related to penetration/aspiration": False,
    "throat clearing not related to penetration/aspiration": False,
    "gagging not related to penetration/aspiration": False,
    "unable to follow commands to cough": False,
    "study ended in view of high risk for aspiration": False,
}


# -----------------------------
# State helpers
# -----------------------------
def default_trial_row() -> dict:
    return {
        "consistency": "thin fluid",
        "custom_consistency": "",
        "delivery": "cup drinking",
        "custom_delivery": "",
    }


def default_aspiration_row() -> dict:
    return {
        "consistency": "thin fluid",
        "custom_consistency": "",
        "delivery": "cup drinking",
        "custom_delivery": "",
        "event_type": "trace penetration",
        "timing": "during swallow",
        "amount": "trace",
        "response": "fully ejected",
        "note": "",
    }


def ensure_module_state() -> None:
    if "vfss_trial_rows" not in st.session_state:
        st.session_state.vfss_trial_rows = [default_trial_row()]
    if "vfss_asp_rows" not in st.session_state:
        st.session_state.vfss_asp_rows = [default_aspiration_row()]
    if "vfss_summary_flags" not in st.session_state:
        st.session_state.vfss_summary_flags = SUMMARY_DEFAULTS.copy()
    if "vfss_copy_buffer" not in st.session_state:
        st.session_state.vfss_copy_buffer = ""


def reset_module_state() -> None:
    st.session_state.vfss_trial_rows = [default_trial_row()]
    st.session_state.vfss_asp_rows = [default_aspiration_row()]
    st.session_state.vfss_summary_flags = SUMMARY_DEFAULTS.copy()
    st.session_state.vfss_copy_buffer = ""


def load_normal_template() -> None:
    st.session_state.vfss_trial_rows = [
        {
            "consistency": "thin fluid",
            "custom_consistency": "",
            "delivery": "cup drinking",
            "custom_delivery": "",
        },
        {
            "consistency": "regular diet",
            "custom_consistency": "",
            "delivery": "half tablespoon",
            "custom_delivery": "",
        },
    ]
    st.session_state.vfss_asp_rows = [default_aspiration_row()]
    st.session_state.vfss_summary_flags = SUMMARY_DEFAULTS.copy()
    st.session_state.vfss_summary_flags["no aspiration or penetration overall"] = True


def load_high_aspiration_risk_template() -> None:
    st.session_state.vfss_trial_rows = [
        {
            "consistency": "moderately thick fluid",
            "custom_consistency": "",
            "delivery": "tablespoon",
            "custom_delivery": "",
        }
    ]
    st.session_state.vfss_asp_rows = [
        {
            "consistency": "moderately thick fluid",
            "custom_consistency": "",
            "delivery": "tablespoon",
            "custom_delivery": "",
            "event_type": "silent aspiration",
            "timing": "during swallow",
            "amount": "moderate",
            "response": "unable to follow commands to cough",
            "note": "",
        }
    ]
    st.session_state.vfss_summary_flags = SUMMARY_DEFAULTS.copy()
    st.session_state.vfss_summary_flags["unable to follow commands to cough"] = True
    st.session_state.vfss_summary_flags["study ended in view of high risk for aspiration"] = True


def add_trial_row() -> None:
    st.session_state.vfss_trial_rows.append(default_trial_row())


def add_aspiration_row() -> None:
    st.session_state.vfss_asp_rows.append(default_aspiration_row())


def remove_trial_row(index: int) -> None:
    rows = st.session_state.vfss_trial_rows
    if len(rows) > 1:
        rows.pop(index)


def remove_aspiration_row(index: int) -> None:
    rows = st.session_state.vfss_asp_rows
    if len(rows) > 1:
        rows.pop(index)


# -----------------------------
# Formatting helpers
# -----------------------------
def resolve_consistency(row: dict) -> str:
    value = row.get("consistency", "")
    if value == "other":
        custom = row.get("custom_consistency", "").strip()
        return custom if custom else ""
    return value.strip()


def resolve_delivery(row: dict) -> str:
    value = row.get("delivery", "")
    if value == "other":
        custom = row.get("custom_delivery", "").strip()
        return custom if custom else ""
    return value.strip()


def format_trial_item(row: dict) -> str:
    consistency = resolve_consistency(row)
    delivery = resolve_delivery(row)
    if consistency and delivery:
        return f"{consistency} ({delivery})"
    if consistency:
        return consistency
    return ""


def format_list_with_and(items: list[str]) -> str:
    items = [item for item in items if item]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f" and {items[-1]}"


def get_trialed_consistencies_sentence(rows: list[dict]) -> str:
    items = [format_trial_item(row) for row in rows]
    items = [item for item in items if item]
    if not items:
        return ""
    return f"The patient was fed {format_list_with_and(items)}."


def sentence_case(text: str) -> str:
    if not text:
        return ""
    return text[0].upper() + text[1:]


def get_aspiration_row_sentence(row: dict) -> str:
    consistency = resolve_consistency(row)
    delivery = resolve_delivery(row)
    event_type = row.get("event_type", "").strip()
    timing = row.get("timing", "").strip()
    amount = row.get("amount", "").strip()
    response = row.get("response", "").strip()
    note = row.get("note", "").strip()

    subject = format_trial_item(
        {
            "consistency": consistency,
            "delivery": delivery,
            "custom_consistency": "",
            "custom_delivery": "",
        }
    )
    if not subject:
        return ""

    descriptor = " ".join(part for part in [amount, event_type, timing] if part)
    base = f"{sentence_case(subject)}: {descriptor} was seen"
    if response:
        base += f", {response}"
    if note:
        cleaned_note = note.rstrip(".")
        base += f". {sentence_case(cleaned_note)}."
    else:
        base += "."
    return base


def get_aspiration_findings_text(rows: list[dict], summary_flags: dict) -> str:
    if summary_flags.get("no aspiration or penetration overall", False):
        return "No aspiration or penetration was seen."

    lines = []
    for row in rows:
        sentence = get_aspiration_row_sentence(row)
        if sentence:
            lines.append(sentence)

    if summary_flags.get("no aspiration or penetration for other consistencies", False):
        lines.append("No aspiration or penetration was seen during trials for other consistencies.")
    if summary_flags.get("coughing not related to penetration/aspiration", False):
        lines.append("Coughing in the study was not related to penetration or aspiration.")
    if summary_flags.get("throat clearing not related to penetration/aspiration", False):
        lines.append("Throat clearing in the study was not related to penetration or aspiration.")
    if summary_flags.get("gagging not related to penetration/aspiration", False):
        lines.append("Gagging in the study was not related to penetration or aspiration.")
    if summary_flags.get("unable to follow commands to cough", False):
        lines.append("The patient did not follow commands to cough.")
    if summary_flags.get("study ended in view of high risk for aspiration", False):
        lines.append("The study ended in view of high risk for aspiration.")

    return "\n".join(lines).strip()


def build_report(rows_trial: list[dict], rows_asp: list[dict], summary_flags: dict) -> str:
    lines = ["VIDEOFLUOROSCOPY - BARIUM SWALLOW", ""]
    trial_sentence = get_trialed_consistencies_sentence(rows_trial)
    if trial_sentence:
        lines.append(trial_sentence)
        lines.append("")
    lines.append("[ASPIRATION FINDINGS]")
    aspiration_text = get_aspiration_findings_text(rows_asp, summary_flags)
    lines.append(aspiration_text if aspiration_text else "")
    return "\n".join(lines).strip()


# -----------------------------
# UI rendering helpers
# -----------------------------
def render_trial_row(index: int) -> None:
    row = st.session_state.vfss_trial_rows[index]

    st.markdown(f"**Trialed consistency #{index + 1}**")
    c1, c2, c3 = st.columns([2.2, 2.2, 1.0])

    with c1:
        row["consistency"] = st.selectbox(
            "Consistency",
            CONSISTENCY_OPTIONS,
            index=CONSISTENCY_OPTIONS.index(row["consistency"]) if row["consistency"] in CONSISTENCY_OPTIONS else 0,
            key=f"trial_consistency_{index}",
        )
        if row["consistency"] == "other":
            row["custom_consistency"] = st.text_input(
                "Custom consistency",
                value=row.get("custom_consistency", ""),
                key=f"trial_custom_consistency_{index}",
            )

    with c2:
        row["delivery"] = st.selectbox(
            "Delivery method",
            DELIVERY_OPTIONS,
            index=DELIVERY_OPTIONS.index(row["delivery"]) if row["delivery"] in DELIVERY_OPTIONS else 0,
            key=f"trial_delivery_{index}",
        )
        if row["delivery"] == "other":
            row["custom_delivery"] = st.text_input(
                "Custom delivery method",
                value=row.get("custom_delivery", ""),
                key=f"trial_custom_delivery_{index}",
            )

    with c3:
        st.write("")
        st.write("")
        if st.button("Remove", key=f"remove_trial_{index}", use_container_width=True):
            remove_trial_row(index)
            st.rerun()


def render_aspiration_row(index: int) -> None:
    row = st.session_state.vfss_asp_rows[index]

    st.markdown(f"**Aspiration finding #{index + 1}**")
    c1, c2 = st.columns(2)

    with c1:
        row["consistency"] = st.selectbox(
            "Consistency",
            CONSISTENCY_OPTIONS,
            index=CONSISTENCY_OPTIONS.index(row["consistency"]) if row["consistency"] in CONSISTENCY_OPTIONS else 0,
            key=f"asp_consistency_{index}",
        )
        if row["consistency"] == "other":
            row["custom_consistency"] = st.text_input(
                "Custom consistency",
                value=row.get("custom_consistency", ""),
                key=f"asp_custom_consistency_{index}",
            )

        row["delivery"] = st.selectbox(
            "Delivery method",
            DELIVERY_OPTIONS,
            index=DELIVERY_OPTIONS.index(row["delivery"]) if row["delivery"] in DELIVERY_OPTIONS else 0,
            key=f"asp_delivery_{index}",
        )
        if row["delivery"] == "other":
            row["custom_delivery"] = st.text_input(
                "Custom delivery method",
                value=row.get("custom_delivery", ""),
                key=f"asp_custom_delivery_{index}",
            )

        row["event_type"] = st.selectbox(
            "Event type",
            EVENT_TYPE_OPTIONS,
            index=EVENT_TYPE_OPTIONS.index(row["event_type"]) if row["event_type"] in EVENT_TYPE_OPTIONS else 0,
            key=f"asp_event_type_{index}",
        )

        row["timing"] = st.selectbox(
            "Timing",
            TIMING_OPTIONS,
            index=TIMING_OPTIONS.index(row["timing"]) if row["timing"] in TIMING_OPTIONS else 0,
            key=f"asp_timing_{index}",
        )

    with c2:
        row["amount"] = st.selectbox(
            "Amount",
            AMOUNT_OPTIONS,
            index=AMOUNT_OPTIONS.index(row["amount"]) if row["amount"] in AMOUNT_OPTIONS else 0,
            key=f"asp_amount_{index}",
        )

        row["response"] = st.selectbox(
            "Response",
            RESPONSE_OPTIONS,
            index=RESPONSE_OPTIONS.index(row["response"]) if row["response"] in RESPONSE_OPTIONS else 0,
            key=f"asp_response_{index}",
        )

        row["note"] = st.text_area(
            "Note",
            value=row.get("note", ""),
            key=f"asp_note_{index}",
            height=100,
        )

        st.write("")
        if st.button("Remove", key=f"remove_asp_{index}", use_container_width=True):
            remove_aspiration_row(index)
            st.rerun()


def render_summary_checkboxes() -> None:
    st.markdown("**Aspiration summary**")
    for label in SUMMARY_DEFAULTS:
        st.session_state.vfss_summary_flags[label] = st.checkbox(
            label,
            value=st.session_state.vfss_summary_flags.get(label, False),
            key=f"summary_{label}",
        )


# -----------------------------
# Module main
# -----------------------------
ensure_module_state()

st.subheader("VFSS Prototype Module: Trialed Consistencies + Aspiration Findings")

toolbar_cols = st.columns([1, 1, 1, 1])
with toolbar_cols[0]:
    if st.button("Clear Form", use_container_width=True):
        reset_module_state()
        st.rerun()
with toolbar_cols[1]:
    if st.button("Load Normal Template", use_container_width=True):
        load_normal_template()
        st.rerun()
with toolbar_cols[2]:
    if st.button("Load High Aspiration Risk Template", use_container_width=True):
        load_high_aspiration_risk_template()
        st.rerun()

left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown("### B. Trialed consistencies")
    for i in range(len(st.session_state.vfss_trial_rows)):
        render_trial_row(i)
        st.divider()

    if st.button("Add Trialed Consistency", use_container_width=True):
        add_trial_row()
        st.rerun()

    st.markdown("### E. Aspiration Findings")
    for i in range(len(st.session_state.vfss_asp_rows)):
        render_aspiration_row(i)
        st.divider()

    if st.button("Add Aspiration Finding", use_container_width=True):
        add_aspiration_row()
        st.rerun()

    render_summary_checkboxes()

with right_col:
    st.markdown("### Report Preview")

    report_text = build_report(
        st.session_state.vfss_trial_rows,
        st.session_state.vfss_asp_rows,
        st.session_state.vfss_summary_flags,
    )
    st.session_state.vfss_copy_buffer = report_text

    st.text_area(
        "Generated Report",
        value=report_text,
        height=520,
        key="vfss_report_preview",
    )

    st.markdown("**Copy Report**")
    st.text_area(
        "Select all and copy manually",
        value=st.session_state.vfss_copy_buffer,
        height=160,
        key="vfss_copy_area",
    )

# ===== MODULE END =====