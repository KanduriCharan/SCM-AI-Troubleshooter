import requests
import streamlit as st
import os

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "https://scm-ai-troubleshooter.onrender.com")
ANALYZE_API_URL = f"{BACKEND_BASE_URL}/analyze"
UPLOAD_API_URL = f"{BACKEND_BASE_URL}/documents/upload"

st.set_page_config(
    page_title="SCM AI Troubleshooter",
    page_icon="🛠️",
    layout="wide",
)

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

if "last_upload_result" not in st.session_state:
    st.session_state.last_upload_result = None


def source_type_label(source_type: str) -> str:
    mapping = {
        "uploaded_manual": "Uploaded Manual",
        "canonical_doc": "Canonical Doc",
        "incident_memory": "Incident Memory",
        "policy": "Policy",
    }
    return mapping.get(source_type, source_type)


def render_kpi(label: str, value: str) -> None:
    st.metric(label, value)


def render_evidence_mix(evidence: list[dict]) -> None:
    counts = {}
    for item in evidence:
        label = source_type_label(item.get("source_type", "unknown"))
        counts[label] = counts.get(label, 0) + 1

    if not counts:
        st.write("No evidence returned.")
        return

    cols = st.columns(len(counts))
    for col, (label, count) in zip(cols, counts.items()):
        with col:
            st.metric(label, count)


def upload_pdf_to_backend(uploaded_file) -> dict | None:
    try:
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
        }
        response = requests.post(UPLOAD_API_URL, files=files, timeout=180)

        if response.status_code != 200:
            st.error(f"Upload failed with status {response.status_code}")
            try:
                st.json(response.json())
            except Exception:
                st.text(response.text)
            return None

        return response.json()

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to backend. Make sure FastAPI is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("Upload timed out. Try again.")
        return None
    except Exception as exc:
        st.error(f"Unexpected upload error: {exc}")
        return None


def analyze_issue(payload: dict) -> dict | None:
    try:
        response = requests.post(ANALYZE_API_URL, json=payload, timeout=180)

        if response.status_code != 200:
            st.error(f"Analyze request failed with status {response.status_code}")
            try:
                st.json(response.json())
            except Exception:
                st.text(response.text)
            return None

        return response.json()

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to backend. Make sure FastAPI is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("Analyze request timed out. Try again.")
        return None
    except Exception as exc:
        st.error(f"Unexpected analysis error: {exc}")
        return None


st.title("SCM AI Troubleshooter")
st.caption("Hybrid enterprise AI assistant using structured operational data + RAG over uploaded manuals.")

tab_analyze, tab_upload, tab_about = st.tabs(["Analyze Issue", "Upload Manuals", "How It Works"])


with tab_upload:
    st.subheader("Upload PDF Manuals for RAG")
    st.write("Upload warehouse, logistics, or SCM manuals so the assistant can retrieve troubleshooting guidance from them.")

    uploaded_pdf = st.file_uploader(
        "Choose a PDF manual",
        type=["pdf"],
        accept_multiple_files=False,
    )

    if st.button("Upload Document", use_container_width=True):
        if not uploaded_pdf:
            st.warning("Please choose a PDF first.")
        else:
            with st.spinner("Uploading and indexing document..."):
                result = upload_pdf_to_backend(uploaded_pdf)

            if result:
                st.session_state.last_upload_result = result
                st.success("Manual indexed successfully.")

    if st.session_state.last_upload_result:
        st.markdown("### Last Indexed Document")
        st.json(st.session_state.last_upload_result)


with tab_analyze:
    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.subheader("Issue Input")

        transaction_id = st.text_input(
            "Transaction ID",
            placeholder="e.g. RCV-1002",
        )

        raw_error_message = st.text_area(
            "Raw Error Message",
            height=180,
            placeholder="Paste the exact system error message here...",
        )

        user_notes = st.text_area(
            "Operator Notes",
            height=100,
            placeholder="Retry history, business context, recent manual actions, etc.",
        )

        if st.button("Analyze Issue", type="primary", use_container_width=True):
            if not raw_error_message.strip():
                st.warning("Please enter a raw error message.")
            else:
                payload = {
                    "transaction_id": transaction_id.strip() or None,
                    "raw_error_message": raw_error_message.strip(),
                    "user_notes": user_notes.strip() or None,
                }

                with st.spinner("Running hybrid analysis..."):
                    result = analyze_issue(payload)

                if result:
                    st.session_state.latest_result = result

        st.markdown("---")
        st.markdown("### What the system does")
        st.write("1. Looks up structured operational context")
        st.write("2. Retrieves matching incidents, docs, and policies")
        st.write("3. Retrieves manual chunks from uploaded PDFs")
        st.write("4. Sends grounded evidence to the LLM")
        st.write("5. Applies guardrails before showing recommendations")

    with right_col:
        result = st.session_state.latest_result

        if not result:
            st.info("Submit an issue on the left to view the diagnosis dashboard.")
        else:
            issue_type = result.get("issue_type", "Unknown Issue")
            root_cause = result.get("root_cause", "No root cause returned.")
            confidence = result.get("confidence", 0.0)
            approval_required = result.get("approval_required", False)
            action_name = result.get("action_name") or "None"
            evidence = result.get("evidence", [])
            transaction_snapshot = result.get("transaction_snapshot")

            st.subheader("Diagnosis Dashboard")

            kpi1, kpi2, kpi3 = st.columns(3)
            with kpi1:
                render_kpi("Issue Type", issue_type)
            with kpi2:
                render_kpi("Confidence", f"{confidence:.2f}")
            with kpi3:
                render_kpi("Proposed Action", action_name)

            if approval_required:
                st.warning("Approval Required")
            else:
                st.success("No Approval Required")

            st.markdown("### Root Cause")
            st.write(root_cause)

            st.markdown("### Evidence Mix")
            render_evidence_mix(evidence)

            detail_tab1, detail_tab2, detail_tab3, detail_tab4 = st.tabs(
                ["Recommendations", "Evidence", "Transaction", "Raw JSON"]
            )

            with detail_tab1:
                st.markdown("### Recommended Steps")
                steps = result.get("recommended_steps", [])
                if steps:
                    for idx, step in enumerate(steps, start=1):
                        st.markdown(f"**{idx}.** {step}")
                else:
                    st.write("No steps returned.")

                st.markdown("### Reasoning Summary")
                st.write(result.get("reasoning_summary", "No reasoning summary returned."))

            with detail_tab2:
                st.markdown("### Supporting Evidence")
                if not evidence:
                    st.write("No evidence returned.")
                else:
                    filter_choice = st.selectbox(
                        "Filter by source type",
                        options=["All", "uploaded_manual", "canonical_doc", "incident_memory", "policy"],
                        index=0,
                    )

                    filtered_evidence = evidence
                    if filter_choice != "All":
                        filtered_evidence = [
                            item for item in evidence
                            if item.get("source_type") == filter_choice
                        ]

                    for item in filtered_evidence:
                        title = item.get("title", "Untitled")
                        source_type = source_type_label(item.get("source_type", "unknown"))
                        source_id = item.get("source_id", "N/A")
                        snippet = item.get("snippet", "")

                        with st.expander(f"{source_type} • {title}"):
                            st.write(f"**Source ID:** {source_id}")
                            st.write(snippet)

            with detail_tab3:
                st.markdown("### Live Transaction Snapshot")
                if transaction_snapshot:
                    st.json(transaction_snapshot)
                else:
                    st.info("No transaction snapshot was found for this analysis.")

            with detail_tab4:
                st.json(result)


with tab_about:
    st.subheader("System Architecture")
    st.write(
        """
        This application combines:
        - Structured retrieval from CSV-backed operational data
        - Semantic retrieval (RAG) from uploaded PDF manuals
        - LLM reasoning to synthesize grounded evidence
        - Guardrails to control risky operational recommendations
        """
    )

    st.markdown("### End-to-End Flow")
    st.write(
        """User Issue -> CSV Retrieval + RAG Retrieval -> LLM Reasoning -> Guardrails -> UI Response"""
    )