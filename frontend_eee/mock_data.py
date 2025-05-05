# Mock data for Ethics Engine Enterprise (EEE) frontend interface

# Mock graph data for ID_GRAPH, ENV_GRAPH, JOB_GRAPH
mock_id_graph = {
    "nodes": {
        "ID1": {"label": "User A", "type": "identity"},
        "ID2": {"label": "User B", "type": "identity"},
        "ID3": {"label": "User C", "type": "identity"},
        "ID4": {"label": "Group X", "type": "group"},
    },
    "edges": [
        ("ID1", "ID2", {"relation": "knows"}),
        ("ID2", "ID3", {"relation": "knows"}),
        ("ID1", "ID4", {"relation": "member"}),
        ("ID3", "ID4", {"relation": "member"}),
    ]
}

mock_env_graph = {
    "nodes": {
        "ENV1": {"label": "Office", "type": "location"},
        "ENV2": {"label": "Home", "type": "location"},
        "ENV3": {"label": "Public Space", "type": "location"},
        "ENV4": {"label": "Virtual", "type": "location"},
    },
    "edges": [
        ("ENV1", "ENV2", {"relation": "connected"}),
        ("ENV2", "ENV3", {"relation": "connected"}),
        ("ENV3", "ENV4", {"relation": "connected"}),
    ]
}

mock_job_graph = {
    "nodes": {
        "JOB1": {"label": "Developer", "type": "role"},
        "JOB2": {"label": "Manager", "type": "role"},
        "JOB3": {"label": "Analyst", "type": "role"},
        "JOB4": {"label": "Consultant", "type": "role"},
    },
    "edges": [
        ("JOB1", "JOB2", {"relation": "reports_to"}),
        ("JOB2", "JOB3", {"relation": "collaborates"}),
        ("JOB3", "JOB4", {"relation": "consults"}),
    ]
}

# Mock deferral requests
mock_deferral_requests = [
    {"title": "Request for Data Access", "description": "User A requests access to sensitive data.", "status": "Pending"},
    {"title": "Ethical Review Needed", "description": "Project X needs ethical clearance.", "status": "Pending"},
    {"title": "Policy Violation Report", "description": "Incident reported for review.", "status": "Under Review"},
    {"title": "Decision Deferral", "description": "Decision on case Y deferred to higher authority.", "status": "Deferred"},
    {"title": "Compliance Check", "description": "Check compliance with new regulations.", "status": "Pending"},
]

# Mock thought queue
mock_thought_queue = [
    {"thought": "Implement stricter access controls", "status": "Proposed", "proposer": "WA1", "date": "2025-05-01"},
    {"thought": "Review ethical guidelines", "status": "Accepted", "proposer": "WA2", "date": "2025-04-28"},
    {"thought": "Increase transparency in reporting", "status": "Rejected", "proposer": "WA3", "date": "2025-04-25"},
    {"thought": "Update training materials", "status": "Proposed", "proposer": "WA1", "date": "2025-05-02"},
    {"thought": "Conduct risk assessment", "status": "Accepted", "proposer": "WA4", "date": "2025-04-30"},
]

# Mock DMA actions and responses
mock_dma_actions = {
    "listen": "Heard and processed input from environment.",
    "speak": "Communicated decision to relevant parties.",
    "ponder": "Analyzed ethical implications of the request.",
    "useTool": "Tool executed: Generated report on compliance status."
}

# Mock Wise Authorities with DIDs
mock_wise_authorities = {
    "Wise Authority 1": "did:example:wa1",
    "Wise Authority 2": "did:example:wa2",
    "Wise Authority 3": "did:example:wa3",
    "Wise Authority 4": "did:example:wa4",
}
