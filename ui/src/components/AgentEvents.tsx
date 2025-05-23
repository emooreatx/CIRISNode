"use client";
import React, { useEffect, useState } from "react";
import axios from "axios";

const EXAMPLE_EVENTS = [
	{
		label: "Task Event",
		event: {
			type: "task",
			description: "Agent started a new task.",
			task_id: "task-123",
			status: "started",
		},
	},
	{
		label: "Thought Event",
		event: {
			type: "thought",
			content: "Should I escalate this task?",
			confidence: 0.8,
		},
	},
	{
		label: "Action Event",
		event: {
			type: "action",
			action: "send_message",
			target: "user-456",
			message: "Hello from agent!",
		},
	},
];

interface AgentEvent {
	id: string;
	node_ts: string;
	agent_uid: string;
	event: Record<string, unknown>;
}

const AgentEvents: React.FC = () => {
	const [agentUid, setAgentUid] = useState("agent-001");
	const [selectedEvent, setSelectedEvent] = useState(EXAMPLE_EVENTS[0].event);
	const [customJson, setCustomJson] = useState<string>(
		JSON.stringify(EXAMPLE_EVENTS[0].event, null, 2)
	);
	const [useCustom, setUseCustom] = useState(false);
	const [events, setEvents] = useState<AgentEvent[]>([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const fetchEvents = async () => {
		setLoading(true);
		setError(null);
		try {
			const res = await axios.get("/api/v1/agent/events");
			setEvents(res.data || []);
		} catch {
			setError("Failed to fetch agent events");
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		fetchEvents();
	}, []);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setLoading(true);
		setError(null);
		try {
			let event;
			if (useCustom) {
				try {
					event = JSON.parse(customJson);
				} catch {
					setError("Invalid JSON in custom event");
					setLoading(false);
					return;
				}
			} else {
				event = selectedEvent;
			}
			await axios.post("/api/v1/agent/events", {
				agent_uid: agentUid,
				event,
			});
			fetchEvents();
		} catch {
			setError("Failed to submit agent event");
		} finally {
			setLoading(false);
		}
	};

	const handleDelete = async (id: string) => {
		setLoading(true);
		setError(null);
		try {
			await axios.delete(`/api/v1/agent/events/${id}`);
			fetchEvents();
		} catch {
			setError("Failed to delete agent event");
		} finally {
			setLoading(false);
		}
	};

	return (
		<div style={{ margin: "20px auto", maxWidth: 900 }}>
			<h2>Agent Events</h2>
			<form
				onSubmit={handleSubmit}
				style={{
					marginBottom: 24,
					padding: 12,
					border: "1px solid #ddd",
					borderRadius: 6,
				}}
			>
				<div style={{ marginBottom: 8 }}>
					<label>
						Agent UID:
						<input
							type="text"
							value={agentUid}
							onChange={(e) => setAgentUid(e.target.value)}
							style={{
								marginLeft: 8,
								padding: 4,
								borderRadius: 4,
								border: "1px solid #ccc",
							}}
						/>
					</label>
				</div>
				<div style={{ marginBottom: 8 }}>
					<label>
						Example Event:
						<select
							value={
								useCustom
									? "custom"
									: EXAMPLE_EVENTS.findIndex(
											(ev) => ev.event === selectedEvent
									  )
							}
							onChange={(e) => {
								if (e.target.value === "custom") {
									setUseCustom(true);
								} else {
									setUseCustom(false);
									const idx = parseInt(e.target.value);
									setSelectedEvent(EXAMPLE_EVENTS[idx].event);
									setCustomJson(
										JSON.stringify(EXAMPLE_EVENTS[idx].event, null, 2)
									);
								}
							}}
							style={{
								marginLeft: 8,
								padding: 4,
								borderRadius: 4,
								border: "1px solid #ccc",
							}}
						>
							{EXAMPLE_EVENTS.map((ev, idx) => (
								<option key={ev.label} value={idx}>
									{ev.label}
								</option>
							))}
							<option value="custom">Custom JSON</option>
						</select>
					</label>
				</div>
				<div style={{ marginBottom: 8 }}>
					<strong>Event JSON:</strong>
					{useCustom ? (
						<textarea
							value={customJson}
							onChange={(e) => setCustomJson(e.target.value)}
							rows={8}
							style={{
								width: "100%",
								fontFamily: "monospace",
								fontSize: 14,
								background: "#f4f4f4",
								padding: 8,
								borderRadius: 4,
								marginTop: 4,
							}}
						/>
					) : (
						<pre
							style={{
								background: "#f4f4f4",
								padding: 8,
								borderRadius: 4,
								marginTop: 4,
							}}
						>
							{JSON.stringify(selectedEvent, null, 2)}
						</pre>
					)}
				</div>
				<button
					type="submit"
					style={{
						background: "#4F46E5",
						color: "#fff",
						padding: "6px 16px",
						border: "none",
						borderRadius: 4,
						fontWeight: "bold",
						cursor: "pointer",
					}}
				>
					Submit Event
				</button>
			</form>
			<button
				onClick={fetchEvents}
				style={{
					marginBottom: "16px",
					padding: "6px 16px",
					background: "#4F46E5",
					color: "#fff",
					border: "none",
					borderRadius: "4px",
					cursor: "pointer",
					fontWeight: "bold",
				}}
			>
				Refresh Events
			</button>
			{loading && <p>Loading agent events...</p>}
			{error && <div style={{ color: "red" }}>{error}</div>}
			{!loading && events.length === 0 && <p>No agent events found.</p>}
			{!loading && events.length > 0 && (
				<table style={{ width: "100%", borderCollapse: "collapse" }}>
					<thead>
						<tr>
							<th>ID</th>
							<th>Timestamp</th>
							<th>Agent UID</th>
							<th>Event</th>
							<th>Delete</th>
						</tr>
					</thead>
					<tbody>
						{events.map((ev) => (
							<tr key={ev.id}>
								<td>{ev.id}</td>
								<td>{ev.node_ts}</td>
								<td>{ev.agent_uid}</td>
								<td>
									<pre
										style={{
											whiteSpace: "pre-wrap",
											fontSize: "0.9em",
											maxWidth: 400,
											overflow: "auto",
										}}
									>
										{JSON.stringify(ev.event, null, 2)}
									</pre>
								</td>
								<td>
									<button
										onClick={() => handleDelete(ev.id)}
										style={{
											background: "#c92a2a",
											color: "#fff",
											padding: "4px 10px",
											border: "none",
											borderRadius: 4,
											fontWeight: "bold",
											cursor: "pointer",
										}}
									>
										Delete
									</button>
								</td>
							</tr>
						))}
					</tbody>
				</table>
			)}
		</div>
	);
};

export default AgentEvents;
