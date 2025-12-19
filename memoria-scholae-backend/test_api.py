"""
Simple API testing script for MemoriaScholae backend.
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_root():
    """Test root endpoint."""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_create_researcher():
    """Test creating a researcher."""
    print("Testing create researcher...")
    data = {
        "researcher_id": "test_researcher",
        "name": "Test Researcher",
        "interests": ["machine learning", "graph databases"]
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/researcher/create",
        params=data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_query():
    """Test query endpoint."""
    print("Testing query endpoint...")
    data = {
        "researcher_id": "test_researcher",
        "query": "What are the latest trends in AI?"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/query",
        json=data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Answer: {result.get('answer', 'N/A')}")
        print(f"Confidence: {result.get('confidence', 'N/A')}\n")
    else:
        print(f"Error: {response.text}\n")


def test_recall_memories():
    """Test memory recall."""
    print("Testing memory recall...")
    data = {
        "researcher_id": "test_researcher"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/memories/recall",
        json=data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Total memories: {result.get('total_count', 0)}\n")
    else:
        print(f"Error: {response.text}\n")


def test_generate_hypotheses():
    """Test hypothesis generation."""
    print("Testing hypothesis generation...")
    data = {
        "researcher_id": "test_researcher",
        "topic": "graph neural networks",
        "num_hypotheses": 2
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/hypotheses/generate",
        json=data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Generated {len(result.get('hypotheses', []))} hypotheses")
        for i, h in enumerate(result.get('hypotheses', []), 1):
            print(f"\nHypothesis {i}:")
            print(f"  Text: {h.get('hypothesis_text', 'N/A')}")
            print(f"  Novelty: {h.get('novelty_score', 'N/A')}")
            print(f"  Confidence: {h.get('confidence_score', 'N/A')}")
    else:
        print(f"Error: {response.text}\n")


def test_find_connections():
    """Test graph connections."""
    print("Testing graph connections...")
    data = {
        "researcher_id": "test_researcher",
        "source_concept": "transformers",
        "target_concept": "graph neural networks",
        "max_hops": 5
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/graph/connections",
        json=data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Found {len(result.get('paths', []))} paths")
        print(f"Bridge concepts: {result.get('bridge_concepts', [])}")
        print(f"Explanation: {result.get('explanation', 'N/A')}\n")
    else:
        print(f"Error: {response.text}\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("MemoriaScholae Backend API Tests")
    print("=" * 60 + "\n")
    
    try:
        test_health()
        test_root()
        test_create_researcher()
        test_query()
        test_recall_memories()
        test_generate_hypotheses()
        test_find_connections()
        
        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to backend.")
        print("Make sure the backend is running at", BASE_URL)
    except Exception as e:
        print(f"\nError during testing: {e}")


if __name__ == "__main__":
    main()
