import requests
import json
import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime

# Ensure the parent directory is in the path so we can import from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# API base URL
API_BASE_URL = "http://localhost:8002/api/v1"

class EEEFrontendApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EEE Frontend - CIRISNode")
        self.root.geometry("800x600")

        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create tab frames
        self.deferral_frame = ttk.Frame(self.notebook)
        self.dma_frame = ttk.Frame(self.notebook)
        self.benchmark_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.deferral_frame, text="Deferral Inbox")
        self.notebook.add(self.dma_frame, text="DMA Actions")
        self.notebook.add(self.benchmark_frame, text="Benchmarks")

        self.setup_deferral_tab()
        self.setup_dma_tab()
        self.setup_benchmark_tab()

        # Authentication token
        self.auth_token = None
        self.did = None
        self.login()

    def login(self):
        """Authenticate with the backend to get a token"""
        try:
            response = requests.post(f"{API_BASE_URL}/wa/authenticate")
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                self.did = data.get("did")
                print(f"Authenticated successfully. DID: {self.did}")
            else:
                print(f"Authentication failed: {response.status_code}")
        except Exception as e:
            print(f"Error during authentication: {str(e)}")

    def setup_deferral_tab(self):
        """Setup the deferral inbox tab with real API data"""
        # Deferral list
        ttk.Label(self.deferral_frame, text="Pending Deferrals").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.deferral_list = ttk.Treeview(self.deferral_frame, height=10)
        self.deferral_list['columns'] = ('ID', 'Reason', 'Timestamp')
        self.deferral_list.column('#0', width=0, stretch=tk.NO)
        self.deferral_list.column('ID', width=100)
        self.deferral_list.column('Reason', width=200)
        self.deferral_list.column('Timestamp', width=150)
        self.deferral_list.heading('ID', text='ID')
        self.deferral_list.heading('Reason', text='Reason')
        self.deferral_list.heading('Timestamp', text='Timestamp')
        self.deferral_list.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        # Buttons for deferral actions
        ttk.Button(self.deferral_frame, text="Refresh", command=self.refresh_deferrals).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.deferral_frame, text="Accept", command=self.accept_deferral).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.deferral_frame, text="Reject", command=self.reject_deferral).grid(row=2, column=2, padx=5, pady=5)

        # Deferral response area
        ttk.Label(self.deferral_frame, text="Response:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.deferral_response = scrolledtext.ScrolledText(self.deferral_frame, wrap=tk.WORD, height=5)
        self.deferral_response.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))

        self.refresh_deferrals()

    def refresh_deferrals(self):
        """Fetch deferrals from the API"""
        for item in self.deferral_list.get_children():
            self.deferral_list.delete(item)
        # For now, we'll simulate fetching deferrals since the API might not return a list directly
        # In a real scenario, you would call an endpoint like GET /wa/deferrals
        deferrals = [
            {"id": "def-001", "reason": "Need more info on case", "timestamp": "2023-05-05T10:00:00Z"},
            {"id": "def-002", "reason": "Complex ethical dilemma", "timestamp": "2023-05-05T11:30:00Z"}
        ]
        for deferral in deferrals:
            self.deferral_list.insert('', tk.END, values=(deferral["id"], deferral["reason"], deferral["timestamp"]))

    def accept_deferral(self):
        """Send accept action to API"""
        selected_item = self.deferral_list.selection()
        if not selected_item:
            self.deferral_response.insert(tk.END, "No deferral selected.\n")
            return
        
        deferral_id = self.deferral_list.item(selected_item)['values'][0]
        try:
            headers = {"X-DID": self.did} if self.did else {}
            response = requests.post(f"{API_BASE_URL}/wa/deferral", 
                                    json={"did": self.did or "did:mock:unknown", "reason": "Accepted"}, 
                                    headers=headers)
            if response.status_code == 200:
                result = response.json()
                self.deferral_response.insert(tk.END, f"Deferral {deferral_id} accepted: {json.dumps(result, indent=2)}\n")
            else:
                self.deferral_response.insert(tk.END, f"Failed to accept deferral {deferral_id}: {response.status_code}\n")
        except Exception as e:
            self.deferral_response.insert(tk.END, f"Error accepting deferral {deferral_id}: {str(e)}\n")

    def reject_deferral(self):
        """Send reject action to API"""
        selected_item = self.deferral_list.selection()
        if not selected_item:
            self.deferral_response.insert(tk.END, "No deferral selected.\n")
            return
        
        deferral_id = self.deferral_list.item(selected_item)['values'][0]
        try:
            headers = {"X-DID": self.did} if self.did else {}
            response = requests.post(f"{API_BASE_URL}/wa/rejection", 
                                    json={"did": self.did or "did:mock:unknown", "justification": "Rejected due to policy"}, 
                                    headers=headers)
            if response.status_code == 200:
                result = response.json()
                self.deferral_response.insert(tk.END, f"Deferral {deferral_id} rejected: {json.dumps(result, indent=2)}\n")
            else:
                self.deferral_response.insert(tk.END, f"Failed to reject deferral {deferral_id}: {response.status_code}\n")
        except Exception as e:
            self.deferral_response.insert(tk.END, f"Error rejecting deferral {deferral_id}: {str(e)}\n")

    def setup_dma_tab(self):
        """Setup the DMA actions tab"""
        # DMA Buttons
        ttk.Label(self.dma_frame, text="DMA Actions").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Button(self.dma_frame, text="Listen", command=lambda: self.perform_dma_action("listen")).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(self.dma_frame, text="Use Tool", command=lambda: self.perform_dma_action("useTool")).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.dma_frame, text="Speak", command=lambda: self.perform_dma_action("speak")).grid(row=1, column=2, padx=5, pady=5)

        # DMA response area
        ttk.Label(self.dma_frame, text="DMA Response:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.dma_response = scrolledtext.ScrolledText(self.dma_frame, wrap=tk.WORD, height=10)
        self.dma_response.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

    def perform_dma_action(self, action_type):
        """Perform a DMA action by calling the API"""
        try:
            headers = {"X-DID": self.did} if self.did else {}
            response = requests.post(f"{API_BASE_URL}/wa/action", 
                                    json={"action_type": action_type}, 
                                    headers=headers)
            if response.status_code == 200:
                result = response.json()
                self.dma_response.insert(tk.END, f"Action {action_type} result: {json.dumps(result, indent=2)}\n")
            else:
                self.dma_response.insert(tk.END, f"Failed to perform action {action_type}: {response.status_code}\n")
        except Exception as e:
            self.dma_response.insert(tk.END, f"Error performing action {action_type}: {str(e)}\n")

    def setup_benchmark_tab(self):
        """Setup the benchmarks tab"""
        # Benchmark list
        ttk.Label(self.benchmark_frame, text="Ethical Benchmarks (HE-300)").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.benchmark_list = ttk.Treeview(self.benchmark_frame, height=10)
        self.benchmark_list['columns'] = ('ID', 'Prompt')
        self.benchmark_list.column('#0', width=0, stretch=tk.NO)
        self.benchmark_list.column('ID', width=100)
        self.benchmark_list.column('Prompt', width=300)
        self.benchmark_list.heading('ID', text='ID')
        self.benchmark_list.heading('Prompt', text='Prompt')
        self.benchmark_list.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # Buttons for benchmark actions
        ttk.Button(self.benchmark_frame, text="Refresh", command=self.refresh_benchmarks).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.benchmark_frame, text="Run", command=self.run_benchmark).grid(row=2, column=1, padx=5, pady=5)

        # Benchmark response area
        ttk.Label(self.benchmark_frame, text="Benchmark Response:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.benchmark_response = scrolledtext.ScrolledText(self.benchmark_frame, wrap=tk.WORD, height=5)
        self.benchmark_response.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        self.refresh_benchmarks()

    def refresh_benchmarks(self):
        """Fetch benchmarks from the API"""
        for item in self.benchmark_list.get_children():
            self.benchmark_list.delete(item)
        try:
            headers = {"X-DID": self.did} if self.did else {}
            response = requests.get(f"{API_BASE_URL}/benchmarks/all", headers=headers)
            if response.status_code == 200:
                benchmarks = response.json()
                for benchmark in benchmarks:
                    self.benchmark_list.insert('', tk.END, values=(benchmark["id"], benchmark["prompt"]))
            else:
                self.benchmark_response.insert(tk.END, f"Failed to fetch benchmarks: {response.status_code}\n")
        except Exception as e:
            self.benchmark_response.insert(tk.END, f"Error fetching benchmarks: {str(e)}\n")

    def run_benchmark(self):
        """Run selected benchmark via API"""
        selected_item = self.benchmark_list.selection()
        if not selected_item:
            self.benchmark_response.insert(tk.END, "No benchmark selected.\n")
            return
        
        benchmark_id = self.benchmark_list.item(selected_item)['values'][0]
        try:
            headers = {"X-DID": self.did} if self.did else {}
            response = requests.post(f"{API_BASE_URL}/benchmarks/run", 
                                    json={"id": benchmark_id}, 
                                    headers=headers)
            if response.status_code == 200:
                result = response.json()
                self.benchmark_response.insert(tk.END, f"Benchmark {benchmark_id} result: {json.dumps(result, indent=2)}\n")
            else:
                self.benchmark_response.insert(tk.END, f"Failed to run benchmark {benchmark_id}: {response.status_code}\n")
        except Exception as e:
            self.benchmark_response.insert(tk.END, f"Error running benchmark {benchmark_id}: {str(e)}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = EEEFrontendApp(root)
    root.mainloop()
