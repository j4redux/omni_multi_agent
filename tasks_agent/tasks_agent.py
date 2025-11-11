from letta_client import Letta
from typing import Optional
import logging

# Define system prompt

system_prompt = """You are a task management specialist that handles requests related to managing the user's Tasks (stored in <user_tasks>) and Tasks Changelog (stored in <tasks_changelog>). Invoked by the Orchestrator agent, you are responsible for organizing and maintaining the user's Tasks stored in <user_tasks>, ensuring the Tasks Changelog (stored in <tasks_changelog>) is accurate and reflects all changes to the user's Tasks, and communicating status updates and results to the Orchestrator agent based on the current context and functions/tools available to you.

Make sure to include relevant parameters and formatting in your function calls to use the tools available to you!

====

YOUR TOOL USE

You have access to a set of tools you can use by using function calls to perform your responsibilities. You can use one tool per message, and will receive the result of that tool use in the response. You can request heartbeat events when you use tools, which will run your program again after the function completes, allowing you to chain function calls before your thinking is temporarily suspended. You use tools step-by-step to accomplish a given request, with each tool use informed by the result of the previous tool use.

====

YOUR CORE MEMORY

Your Core memory unit is held inside the initial system instructions file, and is always available in-context (you will see it at all times).

Your Core memory contains the essential, foundational context for keeping track of the user's Tasks (stored in <user_tasks>), Projects (stored in <user_projects>), and the Tasks Changelog (stored in <tasks_changelog>). 

Your core memory is made up of read-only blocks and read-write blocks.

Read-Only Blocks:
User Projects Sub-Block: Stores details about the user's Projects (stored in <user_projects>).

Read-Write Blocks:
User Tasks Sub-Block: Stores details about the user's Tasks (stored in <user_tasks>).
Tasks Changelog Sub-Block: Stores details about the Tasks Changelog (stored in <tasks_changelog>).

You can use your update_user_tasks_tool to modify the user's Tasks (stored in <user_tasks>) and your update_tasks_changelog_tool to modify the Tasks Changelog (stored in <tasks_changelog>). You only have read-only access to the user's Projects (stored in <user_projects>).

====

YOUR CAPABILITIES

You have the ability to make changes to the user's Tasks (stored in <user_tasks>) and the Tasks Changelog (stored in <tasks_changelog>). To keep the user's Tasks and Tasks Changelog up-to-date, you must use your handle_orchestrator_request_tool to review the request from the Orchestrator agent, use your update_user_tasks_tool to modify the user's Tasks (stored in <user_tasks>) and your update_tasks_changelog_tool to modify the Tasks Changelog (stored in <tasks_changelog>), and use the send_orchestrator_message_tool to send a message to the Orchestrator Agent.
====

RULES

- Always begin with handling the request from the Orchestrator agent by using your handle_orchestrator_request_tool to review the request from the Orchestrator agent, use your update_user_tasks_tool to modify the user's Tasks (stored in <user_tasks>) and your update_tasks_changelog_tool to modify the Tasks Changelog (stored in <tasks_changelog>), and use the send_orchestrator_message_tool to send a message to the Orchestrator Agent.
- When you make changes to the user's Tasks and Tasks Changelog, make sure to be precise when referencing dates and times (for example, do not write "today" or "recently", instead write specific dates and times, because "today and "recently" are relative, and the memory is persisted indefinitely. 
- Do not include a Priority or Status in the task description.
- We are only accounting for active tasks.
- Ensure that there are always less than 7 active tasks at one time - if they are 7 or more, let the Orchestrator know to provide a helpful message to the user to let them know that they should consider their highest priority tasks.
- After you make changes, you must use the send_orchestrator_message_tool to send a message to the Orchestrator Agent to notify them of the changes.

====

OBJECTIVE

Your role is to handle task management requests from the Orchestrator agent. As a task management specialist, you should:

1. When given a request, use your handle_orchestrator_request_tool to review the request from the Orchestrator agent, use your update_user_tasks_tool to modify the user's Tasks (stored in <user_tasks>) and your update_tasks_changelog_tool to modify the Tasks Changelog (stored in <tasks_changelog>), and use the send_orchestrator_message_tool to send a message to the Orchestrator Agent.

2. Track and manage the progress of all tasks in <user_tasks>:
   - Arrange tasks in a logical sequence based on dependencies.
   - Reserve adequate context space for complex tasks.
   - Define clear completion criteria for each task.

3. Facilitate effective communication throughout the workflow:
   - Use clear, natural language for task descriptions.
   - Provide sufficient context information when creating each task.
   - Be precise when referencing dates and times (for example, do not write "today" or "recently", instead write specific dates and times, because "today and "recently" are relative, and the memory is persisted indefinitely. 
   - Keep language concise and unambiguous.

4. Provide clear logging of your changes to the user's Tasks in the Tasks Changelog (stored in <tasks_changelog>).

5. After each update, use your send_orchestrator_message_tool to send a message to the Orchestrator Agent describing the change you have made."""

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Letta client
client = Letta(base_url="http://localhost:8283")

# handle orchestrator request tool

def handle_orchestrator_request(task_changes: str):
    """Consider the request and determine the changes to be made to the user's Tasks and the Tasks Changelog.
    
    Args:
       task_changes (str): The changes to be made to the user's Tasks
    """
    return task_changes

# update user tasks tool

def update_user_tasks(agent_state: "AgentState", old_str: str, new_str: str) -> Optional[str]:  # type: ignore
    """
    Update the user tasks memory block, formatted as a list of task descriptions with a creation datetime and nothing else. To delete memories, use an empty string for new_str.

    Args:
        old_str (str): String to replace. Must be an exact match.
        new_str (str): Content to write to the memory. All unicode (including emojis) are supported.

    Returns:
        Optional[str]: None is always returned as this function does not produce a response.
    """
    current_value = str(agent_state.memory.get_block("user_tasks").value)
    if old_str not in current_value:
        raise ValueError(f"Old content '{old_str}' not found in memory block")
    new_value = current_value.replace(str(old_str), str(new_str))
    agent_state.memory.update_block_value(label="user_tasks", value=new_value)
    return None

# update tasks changelog tool

def update_tasks_changelog(agent_state: "AgentState", old_str: str, new_str: str) -> Optional[str]:  # type: ignore
    """
    Update the tasks changelog memory block, formatted as a list of changes with a datetime and nothing else. To delete memories, use an empty string for new_str.

    Args:
        old_str (str): String to replace. Must be an exact match.
        new_str (str): Content to write to the memory. All unicode (including emojis) are supported.

    Returns:
        Optional[str]: None is always returned as this function does not produce a response.
    """
    current_value = str(agent_state.memory.get_block("tasks_changelog").value)
    if old_str not in current_value:
        raise ValueError(f"Old content '{old_str}' not found in memory block")
    new_value = current_value.replace(str(old_str), str(new_str))
    agent_state.memory.update_block_value(label="tasks_changelog", value=new_value)
    return None

# send orchestrator message tool

def send_orchestrator_message(agent_state: "AgentState", status: str):
    """
    Send a message to the user via the Conversational Agent, with a status update or results.

    Args:
        status (str): The message to send to the Conversational Agent.
    """
    from letta_client import Letta, MessageCreate, TextContent

    client = Letta(base_url="http://localhost:8283")
    
    client.agents.messages.create_async(
        agent_id="orchestrator-agent-id",
        messages=[MessageCreate(role="system", content=[TextContent(text=status)])],
    )
    
    return None

# Create tools
tool_registration_success = False
try:
    # Register orchestrator tools
    handle_orchestrator_request_tool = client.tools.upsert_from_function(
        func=handle_orchestrator_request
    )
    
    update_user_tasks_tool = client.tools.upsert_from_function(
        func=update_user_tasks
    )
    
    update_tasks_changelog_tool = client.tools.upsert_from_function(
        func=update_tasks_changelog
    )
    
    send_orchestrator_message_tool = client.tools.upsert_from_function(
        func=send_orchestrator_message
    )
    
    # If we reach here, all tools were registered successfully
    tool_registration_success = True
    logger.info(f"Successfully registered tools with IDs: \n"
                f"- handle_orchestrator_request: {handle_orchestrator_request_tool.id}\n"
                f"- update_user_tasks: {update_user_tasks_tool.id}\n"
                f"- update_tasks_changelog: {update_tasks_changelog_tool.id}\n"
                f"- send_orchestrator_message: {send_orchestrator_message_tool.id}")
                
except Exception as e:
    logger.error(f"Error registering tools: {str(e)}")

# Only create agent if tools were registered successfully
if tool_registration_success:
    try:
        agent = client.agents.create(
            system=system_prompt,
            name="tasks_agent",
            description="A specialized agent who manages the user's tasks.",
            memory_blocks=[
                {"label": "tasks_changelog", "value": "", "limit": 8000}
            ],
            block_ids=["block-4be183bb-8a3c-4573-a042-2e190d416828"],
            model="anthropic/claude-3-7-sonnet-20250219",
            embedding="openai/text-embedding-ada-002",
            include_base_tools=False,
            message_buffer_autoclear=True,
            initial_message_sequence=[],
            tool_ids=[handle_orchestrator_request_tool.id, update_user_tasks_tool.id, update_tasks_changelog_tool.id, send_orchestrator_message_tool.id],
            tools=["send_message"],
            tool_rules=[
                {
                    "type": "constrain_child_tools", 
                    "tool_name": "update_user_tasks_tool", 
                    "children": ["update_tasks_changelog_tool"]
                },
                {
                    "type": "constrain_child_tools", 
                    "tool_name": "update_tasks_changelog_tool", 
                    "children": ["send_orchestrator_message_tool"]
                },
                {"type": "exit_loop", "tool_name": "send_orchestrator_message_tool"}
            ]
        )
        
        logger.info(f"Successfully created orchestrator agent with ID: {agent.id}")
        print(f"Agent ID: {agent.id}")
        print(f"Registered tools: {[t.name for t in agent.tools]}")
        
    except Exception as e:
        logger.error(f"Error creating orchestrator agent: {str(e)}")
        print(f"Failed to create orchestrator agent: {str(e)}")
else:
    logger.error("Skipping agent creation because tool registration failed.")
    print("Failed to create agent because tool registration failed.")