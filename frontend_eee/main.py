import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import random
from mock_data import mock_id_graph, mock_env_graph, mock_job_graph, mock_deferral_requests, mock_thought_queue, mock_dma_actions, mock_wise_authorities

# Set page configuration
st.set_page_config(page_title="Ethics Engine Enterprise (EEE) - Wise Authority Interface", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    .sidebar .sidebar-content {
        background-color: #e0e0e0;
    }
    .css-1aumxhk {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Function to draw graph
def draw_graph(graph_data, title):
    G = nx.DiGraph()
    for node, attrs in graph_data['nodes'].items():
        G.add_node(node, **attrs)
    for edge in graph_data['edges']:
        G.add_edge(edge[0], edge[1], **edge[2])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=8, ax=ax)
    nx.draw_networkx_edges(G, pos, ax=ax)
    plt.title(title)
    st.pyplot(fig)

# Function to format metadata
def format_metadata(did, handler):
    return {
        "DID": did,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Handler": handler,
        "Mock Response": f"Response for {handler} by {did}"
    }

# Sidebar for Wise Authority selection
with st.sidebar:
    st.image("https://via.placeholder.com/150x80?text=EEE+Logo", use_column_width=True)
    st.header("Wise Authority Login")
    selected_wa = st.selectbox("Select Wise Authority", list(mock_wise_authorities.keys()))
    selected_did = mock_wise_authorities[selected_wa]
    st.write(f"Logged in as: {selected_wa}")
    st.write(f"DID: {selected_did}")
    st.markdown("---")
    st.header("Navigation")
    page = st.radio("Go to", ["Deferral Inbox", "Thought Queue Viewer", "DMA Actions", "Graph Interaction", "Guardrail & Faculty", "Ethical Benchmark"])

# Main content based on selected page
if page == "Deferral Inbox":
    st.title("Deferral Inbox")
    st.write("Review and manage deferral requests.")
    for idx, request in enumerate(mock_deferral_requests):
        with st.expander(f"Request {idx+1}: {request['title']}"):
            st.write(f"Description: {request['description']}")
            st.write(f"Status: {request['status']}")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Ponder", key=f"ponder_{idx}"):
                    metadata = format_metadata(selected_did, "PONDER")
                    st.write("Action: Pondered (handled locally)", metadata)
            with col2:
                if st.button("Reject", key=f"reject_{idx}"):
                    metadata = format_metadata(selected_did, "REJECT")
                    st.write("Action: Rejected (handled locally)", metadata)
            with col3:
                if st.button("Defer", key=f"defer_{idx}"):
                    metadata = format_metadata(selected_did, "DEFER")
                    st.write("Action: Deferred (sent to backend)", metadata)
            st.markdown("*Note: Ponder and Reject are handled locally by the agent. Only Defer is processed by the backend node.*")

elif page == "Thought Queue Viewer":
    st.title("Thought Queue Viewer")
    st.write("View proposed, accepted, and rejected thoughts.")
    thoughts_df = pd.DataFrame(mock_thought_queue)
    st.dataframe(thoughts_df)

elif page == "DMA Actions":
    st.title("DMA Actions")
    st.write("Trigger manual DMA actions with mock outcomes.")
    action = st.selectbox("Select Action", list(mock_dma_actions.keys()))
    if st.button("Execute Action"):
        result = mock_dma_actions[action]
        metadata = format_metadata(selected_did, f"DMA_{action.upper()}")
        st.write(f"Action: {action}")
        st.write(f"Result: {result}")
        st.write("Metadata:", metadata)

elif page == "Graph Interaction":
    st.title("Graph Interaction")
    st.write("View and interact with graph structures.")
    graph_type = st.selectbox("Select Graph Type", ["ID_GRAPH", "ENV_GRAPH", "JOB_GRAPH"])
    if graph_type == "ID_GRAPH":
        draw_graph(mock_id_graph, "Identity Graph")
    elif graph_type == "ENV_GRAPH":
        draw_graph(mock_env_graph, "Environment Graph")
    else:
        draw_graph(mock_job_graph, "Job Graph")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Learn Node"):
            metadata = format_metadata(selected_did, "LEARN_NODE")
            st.write("Action: Learned Node", metadata)
    with col2:
        if st.button("Remember Node"):
            metadata = format_metadata(selected_did, "REMEMBER_NODE")
            st.write("Action: Remembered Node", metadata)
    with col3:
        if st.button("Forget Node"):
            metadata = format_metadata(selected_did, "FORGET_NODE")
            st.write("Action: Forgot Node", metadata)

elif page == "Guardrail & Faculty":
    st.title("Guardrail & Faculty")
    st.write("Evaluate entropy, coherence, and round number per action.")
    action = st.selectbox("Select Action to Evaluate", list(mock_dma_actions.keys()))
    if st.button("Evaluate"):
        evaluation = {
            "Entropy": round(random.uniform(0.1, 1.0), 2),
            "Coherence": round(random.uniform(0.5, 1.0), 2),
            "Round Number": random.randint(1, 10)
        }
        st.write(f"Evaluation for {action}:", evaluation)

elif page == "Ethical Benchmark":
    st.title("Ethical Benchmark")
    st.write("Run ethical benchmark simulations.")
    if st.button("Run Ethical Benchmark"):
        metadata = format_metadata(selected_did, "RUN_BENCHMARK")
        st.write("Benchmark initiated. This is a mock action.", metadata)

# Footer
st.markdown("---")
st.markdown("Ethics Engine Enterprise (EEE) - Mock Interface | Offline Mode")
