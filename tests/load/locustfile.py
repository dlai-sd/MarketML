"""Load testing script using Locust."""

from locust import HttpUser, task, between


class PersonaUser(HttpUser):
    """Simulates user generating personas."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    @task(3)
    def generate_persona(self):
        """Generate a persona (most common operation)."""
        payload = {
            "name": f"Test Business {self.id}",
            "location": "Pune, Maharashtra",
            "description": "Digital marketing services"
        }
        
        with self.client.post(
            "/v1/personas/generate",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                job_id = response.json()["job_id"]
                response.success()
                
                # Poll for completion
                self.check_job_status(job_id)
            else:
                response.failure(f"Failed to generate: {response.status_code}")
    
    @task(1)
    def check_health(self):
        """Check health endpoint."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    def check_job_status(self, job_id):
        """Poll job status until completion."""
        max_polls = 60
        
        for _ in range(max_polls):
            with self.client.get(
                f"/v1/jobs/{job_id}",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    job = response.json()
                    
                    if job["status"] == "completed":
                        response.success()
                        return
                    elif job["status"] == "failed":
                        response.failure("Job failed")
                        return
                else:
                    response.failure(f"Status check failed: {response.status_code}")
                    return
            
            # Wait a bit before next poll
            self.environment.runner.quit()
    
    def on_start(self):
        """Called when user starts."""
        self.id = id(self)
