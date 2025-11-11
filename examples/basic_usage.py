"""
Basic Usage Examples for Omni Multi-Agent System

This script demonstrates simple interactions with the conversational agent.
Make sure all agents are created and the Letta server is running before running this.
"""

from letta_client import Letta, MessageCreate, TextContent
import os

# Configuration
LETTA_SERVER_URL = os.getenv("LETTA_SERVER_URL", "http://localhost:8283")
CONVERSATIONAL_AGENT_ID = os.getenv("CONVERSATIONAL_AGENT_ID", "your-agent-id-here")

# Initialize client
client = Letta(base_url=LETTA_SERVER_URL)


def send_message(message: str) -> str:
    """Send a message to the conversational agent and get response."""
    response = client.agents.messages.create(
        agent_id=CONVERSATIONAL_AGENT_ID,
        messages=[MessageCreate(role="user", content=[TextContent(text=message)])],
    )

    # Extract agent's response
    for msg in response.messages:
        if msg.role == "agent":
            return msg.content[0].text if msg.content else "No response"

    return "No response received"


def example_1_simple_question():
    """Example 1: Ask about existing tasks"""
    print("\n=== Example 1: Simple Question ===")
    message = "What tasks do I have?"
    print(f"User: {message}")

    response = send_message(message)
    print(f"Agent: {response}")


def example_2_add_task():
    """Example 2: Add a new task"""
    print("\n=== Example 2: Add Task ===")
    message = "Add a task to review the quarterly report by end of week"
    print(f"User: {message}")

    response = send_message(message)
    print(f"Agent: {response}")


def example_3_create_project():
    """Example 3: Create a project"""
    print("\n=== Example 3: Create Project ===")
    message = "Create a new project for the website redesign initiative"
    print(f"User: {message}")

    response = send_message(message)
    print(f"Agent: {response}")


def example_4_update_preference():
    """Example 4: Update user preferences"""
    print("\n=== Example 4: Update Preference ===")
    message = "Set my preferred working hours to 9 AM - 5 PM EST"
    print(f"User: {message}")

    response = send_message(message)
    print(f"Agent: {response}")


def example_5_clarification():
    """Example 5: Trigger clarification flow"""
    print("\n=== Example 5: Clarification Flow ===")
    message = "Add a task"
    print(f"User: {message}")

    response = send_message(message)
    print(f"Agent: {response}")
    print("\n(Agent should ask for clarification about what task to add)")


if __name__ == "__main__":
    print("Omni Multi-Agent System - Basic Usage Examples")
    print("=" * 60)

    # Check if agent ID is configured
    if CONVERSATIONAL_AGENT_ID == "your-agent-id-here":
        print("\n❌ ERROR: Please set CONVERSATIONAL_AGENT_ID environment variable")
        print("   Example: export CONVERSATIONAL_AGENT_ID=agent-abc123")
        exit(1)

    # Run examples
    try:
        example_1_simple_question()
        example_2_add_task()
        example_3_create_project()
        example_4_update_preference()
        example_5_clarification()

        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Letta server is running (letta server)")
        print("2. All agents are created")
        print("3. CONVERSATIONAL_AGENT_ID is set correctly")
