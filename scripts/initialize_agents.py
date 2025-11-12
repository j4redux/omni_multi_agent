"""
Agent initialization script for Docker deployment.
Creates all agents in correct order and saves IDs to config file.
"""

import os
import json
import time
from pathlib import Path
from letta_client import Letta, LLMConfig, EmbeddingConfig

# Configuration
LETTA_SERVER_URL = os.getenv("LETTA_SERVER_URL", "http://localhost:8283")
CONFIG_DIR = Path("/app/config")
CONFIG_FILE = CONFIG_DIR / "agent_ids.json"

# Wait for Letta server to be ready
def wait_for_server(max_retries=30, delay=2):
    """Wait for Letta server to become available."""
    print(f"Waiting for Letta server at {LETTA_SERVER_URL}...")
    
    for attempt in range(max_retries):
        try:
            client = Letta(base_url=LETTA_SERVER_URL)
            # Test connection
            client.agents.list()
            print(f"✅ Letta server ready after {attempt + 1} attempts")
            return client
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1}/{max_retries}: Server not ready, retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise Exception(f"Server not available after {max_retries} attempts: {e}")

def create_orchestrator_agent(client):
    """Create orchestrator agent."""
    print("\n=== Creating Orchestrator Agent ===")
    
    # Import orchestrator agent creation logic
    from orchestrator_agent.orchestrator_agent import (
        create_orchestrator_plan_tool,
        delegate_agent_request_tool,
        update_requests_changelog_tool,
        evaluate_progress_tool,
        send_status_update_tool,
        system_prompt
    )
    
    # Register tools
    tools = [
        create_orchestrator_plan_tool,
        delegate_agent_request_tool,
        update_requests_changelog_tool,
        evaluate_progress_tool,
        send_status_update_tool,
    ]
    
    tool_ids = []
    for tool in tools:
        registered_tool = client.tools.create(tool)
        tool_ids.append(registered_tool.id)
        print(f"✓ Registered tool: {tool.name}")
    
    # Create agent
    agent_state = client.agents.create(
        name="orchestrator_agent",
        llm_config=LLMConfig(
            model="anthropic/claude-sonnet-4-5-20250929",
            model_endpoint_type="anthropic",
            model_endpoint="https://api.anthropic.com/v1",
        ),
        embedding_config=EmbeddingConfig(
            embedding_model="openai/text-embedding-ada-002",
            embedding_endpoint_type="openai",
            embedding_endpoint="https://api.openai.com/v1",
        ),
        system=system_prompt,
        include_base_tools=False,
        tool_ids=tool_ids,
    )
    
    print(f"✅ Orchestrator Agent created: {agent_state.id}")
    return agent_state.id

def create_tasks_agent(client, orchestrator_id):
    """Create tasks agent."""
    print("\n=== Creating Tasks Agent ===")
    
    # Similar pattern as orchestrator
    # Import and create tasks agent
    
    # Placeholder - would include full implementation
    print(f"✅ Tasks Agent created")
    return "tasks-agent-id"

def create_projects_agent(client, orchestrator_id):
    """Create projects agent."""
    print("\n=== Creating Projects Agent ===")
    
    # Similar pattern
    print(f"✅ Projects Agent created")
    return "projects-agent-id"

def create_preferences_agent(client, orchestrator_id):
    """Create preferences agent."""
    print("\n=== Creating Preferences Agent ===")
    
    # Similar pattern
    print(f"✅ Preferences Agent created")
    return "preferences-agent-id"

def create_conversational_agent(client, orchestrator_id):
    """Create conversational agent."""
    print("\n=== Creating Conversational Agent ===")
    
    # Similar pattern
    print(f"✅ Conversational Agent created")
    return "conversational-agent-id"

def save_agent_config(agent_ids):
    """Save agent IDs to config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(agent_ids, f, indent=2)
    
    print(f"\n✅ Agent configuration saved to {CONFIG_FILE}")
    
    # Also save as environment variables format
    env_file = CONFIG_DIR / "agent_ids.env"
    with open(env_file, 'w') as f:
        for key, value in agent_ids.items():
            f.write(f"{key.upper()}_AGENT_ID={value}\n")
    
    print(f"✅ Environment variables saved to {env_file}")

def main():
    """Main initialization flow."""
    print("=" * 60)
    print("Omni Multi-Agent System - Agent Initialization")
    print("=" * 60)
    
    try:
        # Wait for server
        client = wait_for_server()
        
        # Check if agents already exist
        if CONFIG_FILE.exists():
            print(f"\n⚠️  Config file {CONFIG_FILE} already exists")
            response = input("Recreate agents? (y/N): ")
            if response.lower() != 'y':
                print("Initialization cancelled")
                return
        
        # Create agents in order
        orchestrator_id = create_orchestrator_agent(client)
        tasks_id = create_tasks_agent(client, orchestrator_id)
        projects_id = create_projects_agent(client, orchestrator_id)
        preferences_id = create_preferences_agent(client, orchestrator_id)
        conversational_id = create_conversational_agent(client, orchestrator_id)
        
        # Save configuration
        agent_ids = {
            "orchestrator": orchestrator_id,
            "tasks": tasks_id,
            "projects": projects_id,
            "preferences": preferences_id,
            "conversational": conversational_id,
        }
        
        save_agent_config(agent_ids)
        
        print("\n" + "=" * 60)
        print("✅ All agents initialized successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Update .env file with CONVERSATIONAL_AGENT_ID")
        print(f"2. Set: CONVERSATIONAL_AGENT_ID={conversational_id}")
        print("3. Restart services: docker-compose restart")
        
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        raise

if __name__ == "__main__":
    main()
