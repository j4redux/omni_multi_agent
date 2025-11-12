"""
Health check script for deployment verification.
"""

import os
import sys
import requests
from letta_client import Letta

LETTA_SERVER_URL = os.getenv("LETTA_SERVER_URL", "http://localhost:8283")

def check_letta_server():
    """Check if Letta server is healthy."""
    try:
        response = requests.get(f"{LETTA_SERVER_URL}/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ Letta server: Healthy")
            return True
        else:
            print(f"❌ Letta server: Unhealthy (status {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Letta server: Unreachable ({e})")
        return False

def check_agents():
    """Check if agents are accessible."""
    try:
        client = Letta(base_url=LETTA_SERVER_URL)
        agents = client.agents.list()
        
        if len(agents) == 0:
            print("⚠️  Agents: None found (run initialization)")
            return False
        
        print(f"✅ Agents: {len(agents)} agents found")
        for agent in agents:
            print(f"   - {agent.name} ({agent.id})")
        return True
    except Exception as e:
        print(f"❌ Agents: Check failed ({e})")
        return False

def check_environment():
    """Check required environment variables."""
    required_vars = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "LETTA_SERVER_URL",
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    return all_set

def main():
    """Run all health checks."""
    print("=" * 60)
    print("Omni Multi-Agent System - Health Check")
    print("=" * 60)
    print()
    
    checks = [
        ("Environment Variables", check_environment),
        ("Letta Server", check_letta_server),
        ("Agents", check_agents),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 40)
        results.append(check_func())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All checks passed!")
        sys.exit(0)
    else:
        print("❌ Some checks failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
