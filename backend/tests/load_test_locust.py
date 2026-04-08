import time
import random
import uuid
from locust import HttpUser, task, between

class CITMSAgentUser(HttpUser):
    """Simulate 10,000 CITMS Agents sending inventory ingestion messages."""
    
    # Wait between 10 and 30 minutes (simulating real agent check-in frequency)
    # For load testing, we'll speed this up to 1-5 seconds to stress the system
    wait_time = between(1, 5)
    
    def on_start(self):
        """Setup: Get a unique device ID and auth token for this agent."""
        self.device_id = str(uuid.uuid4())
        self.hostname = f"PC-{self.device_id[:8]}"
        self.serial = f"SN-{self.device_id[:8]}"
        
        # In real app, we'd login first
        # self.token = self.login()
        self.headers = {
            "Authorization": "Bearer TEST_AGENT_TOKEN",
            "Content-Type": "application/json",
            "X-Trace-Id": str(uuid.uuid4())
        }

    @task(weight=10)
    def ingest_inventory(self):
        """Simulate sending hardware and software inventory (Ingestion)."""
        payload = {
            "hostname": self.hostname,
            "serial_number": self.serial,
            "os_info": {
                "name": "Windows 11 Pro",
                "version": "22H2",
                "build": "22621.1702"
            },
            "hardware": {
                "cpu": "Intel Core i7-12700K",
                "ram_gb": 32,
                "disk_gb": 1024,
                "mac_address": "00:1A:2B:3C:4D:5E"
            },
            "software_list": [
                {"name": "Google Chrome", "version": "114.0.5735.110"},
                {"name": "Microsoft Office 2021", "version": "16.0.14332.20204"},
                {"name": "Slack", "version": "4.32.122"},
                {"name": "Visual Studio Code", "version": "1.79.2"},
                {"name": "Zoom", "version": "5.14.10"}
            ],
            "mode": "FULL_REPLACE"
        }
        
        with self.client.post("/api/v1/inventory/ingest", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 202:
                response.success()
            else:
                response.failure(f"Ingestion failed with status {response.status_code}: {response.text}")

    @task(weight=1)
    def check_health(self):
        """Simulate health check (Monitoring)."""
        self.client.get("/api/v1/health")

    @task(weight=2)
    def get_notifications(self):
        """Simulate checking for pending notifications/actions."""
        self.client.get(f"/api/v1/notifications/user/{self.device_id}", headers=self.headers)

# --- How to run ---
# 1. Install locust: pip install locust
# 2. Run: locust -f backend/tests/load_test_locust.py --host http://localhost:8000
# 3. Open http://localhost:8089 to start the test with 10,000 users and 50 spawn rate.
