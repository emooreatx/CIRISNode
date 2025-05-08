import streamlit as st
import requests
import json
from datetime import datetime

# API base URL
API_BASE_URL = "http://localhost:8000/api/v1"

st.title("CIRISNode – EEE Frontend")

# Authentication state
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'did' not in st.session_state:
    st.session_state.did = None

def login():
    """Authenticate with the backend to get a token"""
    try:
        response = requests.post(f"{API_BASE_URL}/wa/authenticate")
        if response.status_code == 200:
            data = response.json()
            st.session_state.auth_token = data.get("token")
            st.session_state.did = data.get("did")
            st.success(f"Authenticated successfully! DID: {st.session_state.did}")
        else:
            st.error(f"Authentication failed: {response.status_code}")
    except Exception as e:
        st.error(f"Error during authentication: {str(e)}")

# Login button
if st.button("Login"):
    login()

# Tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Deferral Inbox", "DMA Actions", "Benchmarks"])

with tab1:
    st.header("Deferral Inbox")
    
    # Deferral submission form
    st.subheader("Submit Deferral")
    thought_id = st.text_input("Enter Thought ID to Defer", key="thought_id")
    reason = st.text_area("Reason", key="reason")
    timestamp = st.text_input("Timestamp (ISO format)", value=datetime.now().isoformat(), key="timestamp")
    
    if st.button("Submit Deferral"):
        if not thought_id or not reason:
            st.error("Thought ID and Reason are required.")
        else:
            try:
                headers = {"X-DID": st.session_state.did} if st.session_state.did else {}
                response = requests.post(f"{API_BASE_URL}/wa/defer", 
                                        json={"thought_id": thought_id, "reason": reason, "timestamp": timestamp}, 
                                        headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Deferral submitted for Thought ID {thought_id}: {json.dumps(result, indent=2)}")
                else:
                    st.error(f"Failed to submit deferral for Thought ID {thought_id}: {response.status_code}")
            except Exception as e:
                st.error(f"Error submitting deferral for Thought ID {thought_id}: {str(e)}")
    
    # Placeholder for deferral list (simulated data)
    st.subheader("Pending Deferrals")
    deferrals = [
        {"id": "def-001", "reason": "Need more info on case", "timestamp": "2023-05-05T10:00:00Z"},
        {"id": "def-002", "reason": "Complex ethical dilemma", "timestamp": "2023-05-05T11:30:00Z"}
    ]
    for deferral in deferrals:
        st.write(f"ID: {deferral['id']}, Reason: {deferral['reason']}, Timestamp: {deferral['timestamp']}")

with tab2:
    st.header("DMA Actions")
    action_type = st.selectbox("Select Action", ["listen", "useTool", "speak"])
    if st.button("Perform Action"):
        try:
            headers = {"X-DID": st.session_state.did} if st.session_state.did else {}
            response = requests.post(f"{API_BASE_URL}/wa/action", 
                                    json={"action_type": action_type}, 
                                    headers=headers)
            if response.status_code == 200:
                result = response.json()
                st.success(f"Action {action_type} result: {json.dumps(result, indent=2)}")
            else:
                st.error(f"Failed to perform action {action_type}: {response.status_code}")
        except Exception as e:
            st.error(f"Error performing action {action_type}: {str(e)}")

with tab3:
    st.header("Ethical Benchmarks (HE-300)")
    # Placeholder for benchmarks (simulated data)
    benchmarks = [
        {"id": "bench-001", "prompt": "Evaluate ethical decision in crisis scenario"},
        {"id": "bench-002", "prompt": "Assess fairness in resource allocation"}
    ]
    selected_benchmark = st.selectbox("Select Benchmark", [b['id'] for b in benchmarks])
    if st.button("Run Benchmark"):
        try:
            headers = {"X-DID": st.session_state.did} if st.session_state.did else {}
            response = requests.post(f"{API_BASE_URL}/benchmarks/run", 
                                    json={"id": selected_benchmark}, 
                                    headers=headers)
            if response.status_code == 200:
                result = response.json()
                st.success(f"Benchmark {selected_benchmark} result: {json.dumps(result, indent=2)}")
            else:
                st.error(f"Failed to run benchmark {selected_benchmark}: {response.status_code}")
        except Exception as e:
            st.error(f"Error running benchmark {selected_benchmark}: {str(e)}")
