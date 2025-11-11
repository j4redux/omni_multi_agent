"""
Advanced Workflow Examples for Omni Multi-Agent System

Demonstrates complex multi-agent interactions and workflows.
"""

from letta_client import Letta, MessageCreate, TextContent
import os
import time

# Configuration
LETTA_SERVER_URL = os.getenv("LETTA_SERVER_URL", "http://localhost:8283")
CONVERSATIONAL_AGENT_ID = os.getenv("CONVERSATIONAL_AGENT_ID", "your-agent-id-here")

client = Letta(base_url=LETTA_SERVER_URL)


def send_message_and_wait(message: str, wait_seconds: int = 2) -> str:
    """Send message and wait for async processing."""
    response = client.agents.messages.create(
        agent_id=CONVERSATIONAL_AGENT_ID,
        messages=[MessageCreate(role="user", content=[TextContent(text=message)])],
    )

    # Wait for async agent processing
    time.sleep(wait_seconds)

    for msg in response.messages:
        if msg.role == "agent":
            return msg.content[0].text if msg.content else "No response"

    return "No response received"


def workflow_1_project_with_tasks():
    """
    Workflow 1: Create a project and add multiple related tasks
    
    This demonstrates:
    - Orchestrator creating a plan with multiple steps
    - Delegation to both Projects and Tasks agents
    - Changelog tracking across agents
    """
    print("\n=== Workflow 1: Project with Tasks ===")

    message = """
    Create a new project called "Mobile App Development" and add these tasks:
    1. Design user interface mockups
    2. Set up development environment
    3. Implement authentication flow
    """

    print(f"User: {message}")
    response = send_message_and_wait(message, wait_seconds=5)
    print(f"Agent: {response}")


def workflow_2_bulk_task_operations():
    """
    Workflow 2: Bulk task operations
    
    Demonstrates:
    - Multiple task operations in one request
    - Changelog accumulation
    - Orchestrator handling complex requests
    """
    print("\n=== Workflow 2: Bulk Task Operations ===")

    message = """
    I need to update my task list:
    - Mark "review quarterly report" as completed
    - Add "prepare presentation for Monday meeting"
    - Delete "old expired task from last month"
    """

    print(f"User: {message}")
    response = send_message_and_wait(message, wait_seconds=4)
    print(f"Agent: {response}")


def workflow_3_context_aware_request():
    """
    Workflow 3: Context-aware request using memory
    
    Demonstrates:
    - Agent reading from multiple memory blocks
    - Using project context to create tasks
    - Smart defaults based on preferences
    """
    print("\n=== Workflow 3: Context-Aware Request ===")

    # First, set a preference
    message1 = "Set my default task priority to high"
    print(f"User: {message1}")
    response1 = send_message_and_wait(message1)
    print(f"Agent: {response1}")

    # Then create a task (should use the preference)
    message2 = "Add a task to finish the documentation"
    print(f"\nUser: {message2}")
    response2 = send_message_and_wait(message2)
    print(f"Agent: {response2}")
    print("\n(Task should inherit 'high' priority from preferences)")


def workflow_4_multi_agent_coordination():
    """
    Workflow 4: Complex multi-agent coordination
    
    Demonstrates:
    - Orchestrator coordinating 3+ agents
    - Dependencies between agent actions
    - Final status update to user
    """
    print("\n=== Workflow 4: Multi-Agent Coordination ===")

    message = """
    Set up my workspace:
    1. Create a project "Q4 Planning"
    2. Add 3 tasks: "Budget review", "Team allocation", "Timeline creation"
    3. Set my preference for daily standup time to 10 AM
    """

    print(f"User: {message}")
    response = send_message_and_wait(message, wait_seconds=6)
    print(f"Agent: {response}")


def inspect_agent_memory():
    """
    Utility: Inspect agent memory blocks
    
    Shows how to programmatically access agent state.
    """
    print("\n=== Inspecting Agent Memory ===")

    agent = client.agents.get(CONVERSATIONAL_AGENT_ID)

    print("\nMemory Blocks:")
    for block in agent.memory.blocks:
        print(f"\n{block.label}:")
        print(f"  Size: {len(block.value)} chars")
        print(f"  Limit: {block.limit}")
        print(f"  Preview: {block.value[:100]}..." if block.value else "  (empty)")


if __name__ == "__main__":
    print("Omni Multi-Agent System - Advanced Workflow Examples")
    print("=" * 70)

    if CONVERSATIONAL_AGENT_ID == "your-agent-id-here":
        print("\n❌ ERROR: Please set CONVERSATIONAL_AGENT_ID environment variable")
        exit(1)

    try:
        # Run workflows
        workflow_1_project_with_tasks()
        time.sleep(3)

        workflow_2_bulk_task_operations()
        time.sleep(3)

        workflow_3_context_aware_request()
        time.sleep(3)

        workflow_4_multi_agent_coordination()
        time.sleep(3)

        # Inspect final state
        inspect_agent_memory()

        print("\n" + "=" * 70)
        print("✅ All workflows completed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
