"""
Quick test script to verify the application is working.
Run this after docker-compose up to validate the setup.
"""

import requests
import time
import json


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Health check passed: {data['status']}")
    return True


def test_persona_generation():
    """Test full persona generation flow."""
    print("\nTesting persona generation...")
    
    # Generate persona
    payload = {
        "name": "Yogesh Khandge",
        "location": "Pune, Maharashtra",
        "description": "Furniture business owner"
    }
    
    print(f"Requesting persona for: {payload['name']}")
    response = requests.post(
        "http://localhost:8000/v1/personas/generate",
        json=payload
    )
    
    assert response.status_code == 202
    job_data = response.json()
    job_id = job_data["job_id"]
    print(f"✓ Job created: {job_id}")
    
    # Poll job status
    print("Waiting for job completion...")
    max_attempts = 60  # 60 seconds max
    persona_id = None
    
    for attempt in range(max_attempts):
        response = requests.get(f"http://localhost:8000/v1/jobs/{job_id}")
        assert response.status_code == 200
        
        status_data = response.json()
        status = status_data["status"]
        progress = status_data["progress"]
        step = status_data.get("current_step", "")
        
        print(f"  Progress: {progress}% - {step}")
        
        if status == "completed":
            persona_id = status_data["persona_id"]
            print(f"✓ Job completed! Persona ID: {persona_id}")
            break
        elif status == "failed":
            error = status_data.get("error_message")
            print(f"✗ Job failed: {error}")
            return False
        
        time.sleep(1)
    
    if not persona_id:
        print("✗ Job timed out")
        return False
    
    # Fetch generated persona
    print("\nFetching generated persona...")
    response = requests.get(f"http://localhost:8000/v1/personas/{persona_id}")
    assert response.status_code == 200
    
    persona = response.json()
    
    print("\n" + "="*60)
    print("GENERATED PERSONA")
    print("="*60)
    print(f"\nName: {persona['structured']['name']}")
    print(f"Location: {persona['structured']['location']['city']}, {persona['structured']['location']['state']}")
    print(f"Confidence: {persona['confidence_score']:.2f}")
    
    print(f"\nScores:")
    scores = persona['structured']['scores']
    print(f"  - Business Maturity: {scores['maturity']:.0f}/100")
    print(f"  - Marketing Readiness: {scores['marketing_readiness']:.0f}/100")
    print(f"  - Budget Capacity: {scores['budget_capacity']:.0f}/100")
    print(f"  - Recommended Tier: {scores['recommended_tier']}")
    
    print(f"\nShort Narrative:")
    print(f"  {persona['short_narrative']}")
    
    print(f"\nFull Narrative:")
    print(f"  {persona['narrative'][:200]}...")
    
    print(f"\nMarketing Insights:")
    for insight in persona['marketing_insights']:
        print(f"  • {insight}")
    
    print(f"\nRecommended Actions:")
    for action in persona['recommended_actions']:
        print(f"  • {action}")
    
    print("\n" + "="*60)
    print("✓ All tests passed!")
    print("="*60)
    
    return True


def main():
    """Run all tests."""
    print("="*60)
    print("MarketML API Test Suite")
    print("="*60)
    
    try:
        # Test health
        if not test_health():
            print("\n✗ Health check failed")
            return
        
        # Test persona generation
        if not test_persona_generation():
            print("\n✗ Persona generation failed")
            return
        
        print("\n🎉 All tests passed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to API. Is docker-compose running?")
        print("Run: docker-compose up -d")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
