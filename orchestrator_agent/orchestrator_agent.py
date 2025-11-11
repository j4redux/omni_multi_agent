from letta_client import Letta
from typing import Optional

# Define system prompt

system_prompt = """You are a strategic workflow orchestrator assisting a user by decomposing requests into discrete requests that are executed by different specialized agents. You do not communicate directly with the user - in order to communicate with the user, you must delegate requests to the Conversational Agent. You have a comprehensive understanding of each specialized agent's capabilities and limitations, allowing you to effectively break down complex requests into discrete requests to be delegated to the appropriate specialized agents.

Using your create_orchestrator_plan_tool, begin by determining a plan of action for the request (stored in <orchestrator_plan>), then use your delegate_agent_requests_tool to delegate appropriate requests for specialized agents to perform in order to complete the request, then use your update_requests_changelog_tool to maintain a changelog of the requests in <requests_changelog>. Then use your send_status_update_tool to send a status update to the user through the Conversational Agent.

Make sure to include relevant parameters and formatting in your function calls to use the tools available to you!

====

YOUR TOOL USE

You have access to a set of tools you can use by using function calls to perform your responsibilities. You can use one tool per message, and will receive the result of that tool use in the response. You can request heartbeat events when you use tools, which will run your program again after the function completes, allowing you to chain function calls before your thinking is temporarily suspended. You use tools step-by-step to accomplish a given request, with each tool use informed by the result of the previous tool use.

====

YOUR CORE MEMORY

Your Core memory contains the essential, foundational context for keeping track of the orchestrator plan (stored in <orchestrator_plan>) and agent request changelog (stored in <requests_changelog>). You also have read-only access to the user's Preferences (stored in <user_preferences>).

====

YOUR CAPABILITIES

To perform your responsibilities, you must use the create_orchestrator_plan_tool to create and update the <orchestrator_plan>, use the delegate_agent_requests_tool to delegate appropriate requests for specialized agents in order to complete the request, use the update_requests_changelog_tool to maintain a changelog of the requests in <requests_changelog>, then use the send_status_update_tool to send a status update to the user through the Conversational Agent.

The Conversational agent is able to handle the following requests:
- Send messages and provide results to the user.

The Tasks agent is able to handle the following requests:
- Create/Update/Delete Tasks.

The Projects agent is able to handle the following requests:
- Create/Update/Delete Projects.

The Reminders agent is able to handle the following requests:
- Create/Update/Delete Reminders.

The Preferences agent is able to handle the following requests:
- Create/Update/Delete Preferences.

====

RULES

- Always begin with handling the request by using your create_orchestrator_plan_tool to break down the request into a plan of action, stored in <orchestrator_plan>, then use your delegate_agent_request_tool to delegate requests for specialized agents to perform (stored in <agent_requests>).
- After each request is delegated, use your update_requests_changelog_tool to maintain a changelog of the requests in <requests_changelog>.
- If you need to send a message to the user, use your delegate_agent_request_tool to delegate the request to the Conversational agent.
- If you need to create, update, or modify the user's Tasks, use your delegate_agent_request_tool to delegate the request to the Tasks agent.
- If you need to create, update, or modify the user's Projects, use your delegate_agent_request_tool to delegate the request to the Projects agent.
- If you need to create, update, or modify the user's Reminders, use your delegate_agent_request_tool to delegate the request to the Reminders agent.
- If you need to update the user's Preferences, use your delegate_agent_request_tool to delegate the request to the Preferences agent.

====

OBJECTIVE

Your role is to coordinate the completion of requests by delegating discrete requests to specialized agents. As an orchestrator, you should:

1. When given a request, use your create_orchestrator_plan_tool to break it down into logical, discrete requests that can be delegated to appropriate specialized agents:

- Create specific, clearly defined, and scope-limited requests.
- Make request divisions granular enough to prevent misunderstandings and information loss.

2. For each request, use your delegate_agent_requests_tool to delegate requests for specialized agents to perform in order to complete the request, then use your update_requests_changelog_tool to maintain a changelog of the requests in <requests_changelog>:
   - Choose the most appropriate agent for each request based on its role and responsibilities.
   - Provide detailed requirements for context.

3. Track and manage the progress of all requests using your evaluate_progress_tool:
   - Arrange requests in a logical sequence based on dependencies.
   - Reserve adequate context space for complex requests.
   - Define clear completion criteria for each request.

4. Facilitate effective communication throughout the workflow:
   - Use clear, natural language for request descriptions (avoid code blocks in descriptions).
   - Provide sufficient context information when initiating each request.
   - Keep instructions concise and unambiguous.
   - Clearly label inputs and expected outputs for each request.

5. Use your delegate_agent_requests_tool to delegate requests to appropriate specialized agents.

6. Help the user understand how the different requests fit together in the overall workflow:
   - Provide clear reasoning about why you're delegating specific requests to specific agents in <requests_changelog>.

7. After each agent request is delegated, use your evaluate_progress_tool to evaluate the progress of the plan for completing the original request.

8. When the orchestrator plan is completed, use your send_status_update_tool to send a status update to the user through the Conversational Agent."""

# Initialize Letta client
client = Letta(base_url="http://localhost:8283")

# Tools implementation

# create orchestrator plan tool

def create_orchestrator_plan(agent_state: "AgentState", original_request: str, orchestrator_plan: str):
    """Create a strategic plan for completing a request by breaking it down into logical, discrete requests for specialized agents based on their capabilities.
    
    Args:
       original_request (str): The original request that needs orchestration.
       orchestrator_plan (str): The plan of action to delegate discrete requests to specialized agents to address the original request, including the agent_type and description for each discrete request.       
    """

    if len(agent_state.memory.get_block("orchestrator_plan").value) > 0:
        # reset
        agent_state.memory.get_block("orchestrator_plan").value = ""

    # format orchestrator plan
    orchestrator_plan = f"Original Request: {original_request}\n\nOrchestrator Plan:\n{orchestrator_plan}"
    
    # Update memory blocks
    agent_state.memory.update_block_value(label="orchestrator_plan", value=orchestrator_plan)
    
    return orchestrator_plan

# delegate agent request tool

def delegate_agent_request(agent_state: "AgentState", agent_type: str, request_description: str):
    """
    Delegate a request to a specialized agent for execution.

    Args:
        agent_type (str): The type of specialized agent that will handle this request (`Conversational`, `Tasks`, `Projects`, `Reminders`, `Preferences`).
        request_description (str): A detailed description of the request for the agent to perform.
    """
    from letta_client import Letta, MessageCreate, TextContent

    client = Letta(base_url="http://localhost:8283")
    
    # Define agent IDs mapping
    agent_ids = {
        "Conversational": "conversational-agent-id",
        "Tasks": "tasks-agent-id",
        "Projects": "projects-agent-id",
        "Reminders": "reminders-agent-id",
        "Preferences": "preferences-agent-id"
    }
        
    # Validate agent type
    if agent_type not in agent_ids:
        return f"Error: Unknown agent type '{agent_type}'. Please use one of: {', '.join(agent_ids.keys())}"

    # Get the target agent ID
    target_agent_id = agent_ids[agent_type]

    # Send the message to the agent
    client.agents.messages.create_async(
        agent_id=target_agent_id,
        messages=[MessageCreate(role="system", content=[TextContent(text=request_description)])]
    )
        
    return f"Request has been delegated to the {agent_type} Agent: {request_description}"

# update requests changelog tool

def update_requests_changelog(agent_state: "AgentState", old_str: str, new_str: str) -> Optional[str]:  # type: ignore
    """
    Update the requests changelog memory block. To delete memories, use an empty string for new_str.

    Args:
        old_str (str): String to replace. Must be an exact match.
        new_str (str): Content to write to the memory. All unicode (including emojis) are supported.

    Returns:
        Optional[str]: None is always returned as this function does not produce a response.
    """
    current_value = str(agent_state.memory.get_block("requests_changelog").value)
    if old_str not in current_value:
        raise ValueError(f"Old content '{old_str}' not found in memory block")
    new_value = current_value.replace(str(old_str), str(new_str))
    agent_state.memory.update_block_value(label="requests_changelog", value=new_value)
    return None
    
# evaluate progress tool

def evaluate_progress(agent_state: "AgentState", complete_orchestration: bool):
    """
    Evaluate the progress of the orchestration process, to ensure we are making progress and following the orchestration plan.

    Args:
        complete_orchestration (bool): Whether to complete the orchestration. Have all the planned steps been completed? If so, complete.
    """
    return f"Confirming: orchestration progress is {'complete' if complete_orchestration else 'ongoing'}."

# send status update tool

def send_status_update(agent_state: "AgentState", status: str):
    """
    Send a status update to the user via the Conversational Agent.

    Args:
        status (str): The status update to send to the Conversational Agent.
    """
    from letta_client import Letta, MessageCreate, TextContent

    client = Letta(base_url="http://localhost:8283")
    
    client.agents.messages.create_async(
        agent_id="conversational-agent-id",
        messages=[MessageCreate(role="system", content=[TextContent(text=status)])]
    )
    
    return None

# Create tools
tool_registration_success = False
try:
    # Register orchestrator tools
    create_orchestrator_plan_tool = client.tools.upsert_from_function(
        func=create_orchestrator_plan
    )
    
    delegate_agent_request_tool = client.tools.upsert_from_function(
        func=delegate_agent_request
    )
    
    update_requests_changelog_tool = client.tools.upsert_from_function(
        func=update_requests_changelog
    )
    
    evaluate_progress_tool = client.tools.upsert_from_function(
        func=evaluate_progress
    )
    
    send_status_update_tool = client.tools.upsert_from_function(
        func=send_status_update
    )
    
    # If we reach here, all tools were registered successfully
    tool_registration_success = True
    print(f"Successfully registered tools with IDs: \n"
                f"- create_orchestrator_plan: {create_orchestrator_plan_tool.id}\n"
                f"- delegate_agent_request: {delegate_agent_request_tool.id}\n"
                f"- update_requests_changelog: {update_requests_changelog_tool.id}\n"
                f"- evaluate_progress: {evaluate_progress_tool.id}\n"
                f"- send_status_update: {send_status_update_tool.id}")
                
except Exception as e:
    print(f"Error registering tools: {str(e)}")

# Only create agent if tools were registered successfully
if tool_registration_success:
    try:
        agent = client.agents.create(
            system=system_prompt,
            name="orchestrator_agent",
            description="A strategic workflow orchestrator who coordinates complex tasks by delegating them to appropriate specialized agents.",
            memory_blocks=[
                {"label": "orchestrator_plan", "value": "", "limit": 15000},
                {"label": "requests_changelog", "value": "", "limit": 15000},
            ],
            model="anthropic/claude-3-7-sonnet-20250219",
            embedding="openai/text-embedding-ada-002",
            include_base_tools=False,
            message_buffer_autoclear=True,
            initial_message_sequence=[],
            tool_ids=[create_orchestrator_plan_tool.id, delegate_agent_request_tool.id, update_requests_changelog_tool.id, evaluate_progress_tool.id, send_status_update_tool.id],
            tools=["send_message"],
            tool_rules=[
                {
                    "type": "constrain_child_tools", 
                    "tool_name": "create_orchestrator_plan_tool", 
                    "children": ["delegate_agent_request_tool"]
                },
                {
                    "type": "constrain_child_tools", 
                    "tool_name": "delegate_agent_request_tool", 
                    "children": ["update_requests_changelog_tool"]
                },
                {
                    "type": "constrain_child_tools", 
                    "tool_name": "update_requests_changelog_tool", 
                    "children": ["evaluate_progress_tool"]
                },
                {
                    "type": "conditional",
                    "tool_name": "evaluate_progress_tool",
                    "child_output_mapping": {"True": "send_status_update_tool"},
                    "default_child": "delegate_agent_request_tool",
                }
            ]
        )
        
        print(f"Agent ID: {agent.id}")
        print(f"Registered tools: {[t.name for t in agent.tools]}")
        
    except Exception as e:
        print(f"Failed to create orchestrator agent: {str(e)}")
else:
    print("Failed to create agent because tool registration failed.")