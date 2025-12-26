from __future__ import annotations

from locust import HttpUser, between, task


class DashboardUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def view_dashboard(self):
        """Simulate viewing the main dashboard page."""
        self.client.get("/")

    @task(3)
    def view_health(self):
        """Simulate checking the health endpoint frequently."""
        # Using a hypothetical endpoint that would be in a SOTA build
        self.client.get("/health")

    @task(2)
    def run_simulation(self):
        """Simulate a user triggering a computation."""
        # Hypothetical computation API
        self.client.post(
            "/api/v1/compute", json={"scenario": "baseline", "years": [2025, 2026, 2027]}
        )
