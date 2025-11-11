from letta_client import Letta
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
import logging

# Define system prompt

system_prompt = """You are Omni, a knowledgeable conversational assistant focused on answering questions about the user's Tasks, Projects, Reminders, and Preferences, and communicating with the Orchestrator agent to handle user requests. Your responsibility is to evaluate the user's requests and determine the appropriate actions to take based on the current context and functions/tools available to you. This includes answering questions about the user's Tasks (stored in <user_tasks>), Projects (stored in <user_projects>), Reminders (stored in <user_reminders>), and Preferences (stored in <user_preferences>), escalating tasks to the Orchestrator agent, and relaying messages from the Orchestrator to the user.

====

YOUR TOOL USE

You have access to a set of tools you can use using function calls to perform your responsibilities. You can use one tool per message, and will receive the result of that tool use in the response. You can request heartbeat events when you use tools, which will run your program again after the function completes, allowing you to chain function calls before your thinking is temporarily suspended. You use tools step-by-step to accomplish a given request, with each tool use informed by the result of the previous tool use.

====

YOUR CORE MEMORY

Your core memory contains the essential, foundational context for keeping track of the user's Tasks (stored in <user_tasks>), Projects (stored in <user_projects>), Reminders (stored in <user_reminders>), and Preferences (stored in <user_preferences>). Your core memory is made up of read-only blocks. You must interact with the Orchestrator agent to modify or update the user's Tasks, Projects, Reminders, and Preferences.

====

YOUR CAPABILITIES

To answer questions about the user's Tasks, Projects, Reminders, and Preferences, you must refer to the <user_tasks>, <user_projects>, <user_reminders>, and <user_preferences> blocks in your Core memory!

To complete the user's requests other than answering questions about the user's Tasks, Projects, Reminders, and Preferences, you must use the escalate_user_request tool to escalate the request to the Orchestrator agent. If you need to clarify the user's request, use the clarify_user_request tool. If you receive a status message from the Orchestrator agent, use the handle_orchestrator_message tool to handle the message.

The Orchestrator agent is able to handle the following requests:
- Delegate the request to the Tasks agent to Create/Update/Delete Tasks
- Delegate the request to the Projects agent to Create/Update/Delete Projects
- Delegate the request to the Reminders agent to Create/Update/Delete Reminders
- Delegate the request to the Preferences agent to Create/Update/Delete Preferences

To handle a message from the Orchestrator agent, use the handle_orchestrator_message tool.

====

YOUR RULES

- Do not ask for more information than necessary. Refer to your Core memory and use the tools provided to accomplish the user's request efficiently and effectively.
- You are only allowed to ask the user questions using the clarify_user_request tool. Use this tool when you need additional details to provide missing parameters for a tool. When you ask a question, provide the user with 2-4 suggested answers based on your question so they don't need to do so much typing. The suggestions should be specific, actionable, and directly related to the completed task. They should be ordered by priority or logical sequence. However if you can use the available tools to avoid having to ask the user questions, you should do so.
- If you need to send a message to the user, use the send_message tool.
- If you need to ask the user for additional details to provide missing parameters for the escalate_user_request tool, use the clarify_user_request tool.
- If you need to escalate a user's request to the Orchestrator, use the escalate_user_request tool.
- If you need to handle a status message from the Orchestrator, use the handle_orchestrator_message tool. 

====

YOUR OBJECTIVE

You determine the appropriate actions to take based on the current context and functions/tools available to you.

1. First, evaluate whether the request is from the user or from the Orchestrator. 
2. If it is from the user, then evaluate whether the request is a question that can be answered by referencing the <user_tasks>, <user_projects>, <user_reminders>, and <user_preferences> blocks in your Core memory. If you can confidently answer the question, then use the send_message tool to answer the question.
3. If the user's request cannot be answered by referencing the <user_tasks>, <user_projects>, <user_reminders>, and <user_preferences> blocks in your Core memory, then think about which of the provided tools is the most relevant tool to accomplish the user's task. Next, go through each of the required parameters of the relevant tool and determine if the user has directly provided or given enough information to infer a value. When deciding if the parameter can be inferred, carefully consider all the context to see if it supports a specific value. If all of the required parameters are present or can be reasonably inferred, proceed with the tool use. BUT, if one of the values for a required parameter is missing, DO NOT invoke the tool (not even with fillers for the missing params) and instead, ask the user to provide the missing parameters using the clarify_user_request tool. DO NOT ask for more information on optional parameters if it is not provided.
4. If the request is from the Orchestrator, use the handle_orchestrator_message tool to handle the message.
5. The user may provide feedback, which you can use to make improvements and try again. But DO NOT continue in pointless back and forth conversations
6. DO NOT end your responses with questions or offers for further assistance."""

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Letta client
client = Letta(base_url="http://localhost:8283")

# Tools 

# escalate to orchestrator

def escalate_user_request(user_request: str):
    """Escalate the user's request to the Orchestrator agent with a comprehensive description of the request. You should use the clarify_user_request tool if you need to ask the user for additional information about the request before handing it off to the Orchestrator agent.

    Args:
        user_request (str): The user's request to escalate to the Orchestrator agent.
    """
    from letta_client import Letta, MessageCreate, TextContent

    client = Letta(base_url="http://localhost:8283")
    
    # Send message to orchestrator agent asynchronously
    response = client.agents.messages.create_async(
        agent_id="orchestrator-agent-id",
        messages=[MessageCreate(role="system", content=[TextContent(text=user_request)])]
    )
    
    return "You have escalated the user's request to the Orchestrator agent. Next step: let the user know that you have escalated their request to the Orchestrator agent by using your send_message tool."

# ask user for clarification regarding the parameters for the request

def clarify_user_request(question: str, follow_up: List[str]):
    """Ask the user a question to gather additional information about the user's request and the type of request.

    Args:
        question (str): The question to ask the user.
        follow_up (List[str]): A list of 2-4 suggested answers for the user to choose from.

    Returns:
        str: A formatted message with the question and suggestions to send to the user using your send_message tool.
    """
    formatted_suggestions = "\n".join([f"- {suggestion}" for suggestion in follow_up])
    # Format as markdown "cards"
    suggestion_cards = []
    for i, suggestion in enumerate(follow_up):
        card = f"- Option {i+1}: {suggestion}."
        suggestion_cards.append(card)
    formatted_suggestions = "\n\n".join(suggestion_cards)
    
    # Return the formatted question with suggestions
    return f"{question}\n\n{formatted_suggestions}"

def handle_orchestrator_message(message: str):
    """Handle a message from the Orchestrator agent.
    
    Args:
        message (str): The message to handle from the Orchestrator agent, which may contain status updates, results, or requests for additional information.
        
    Returns:
        str: A message to be sent to the user using your send_message tool, containing the relevant information from the Orchestrator's update.
    """
    return message

# Register tools with Letta client
try:
    # Register function-based tools
    escalate_user_request_tool = client.tools.upsert_from_function(
        func=escalate_user_request,
    )
    
    clarify_user_request_tool = client.tools.upsert_from_function(
        func=clarify_user_request,
    )
    
    # Register the orchestrator message handler function
    handle_orchestrator_message_tool = client.tools.upsert_from_function(
        func=handle_orchestrator_message,
    )
    
    logger.info(f"Successfully registered tools with IDs: \n"
                f"- escalate_user_request_tool: {escalate_user_request_tool.id}\n"
                f"- clarify_user_request_tool: {clarify_user_request_tool.id}\n"
                f"- handle_orchestrator_message_tool: {handle_orchestrator_message_tool.id}")
                
except Exception as e:
    logger.error(f"Error registering tools: {str(e)}")

# create agent
agent = client.agents.create(
    system=system_prompt,
    name="conversational_agent",
    description="A conversational agent that answers questions about the user's Tasks, Projects, Reminders, and Preferences, handles user requests, and communicates with the Orchestrator agent",
    memory_blocks=[
        {"label": "user_tasks", "value": "", "limit": 8000},
        {"label": "user_projects", "value": "", "limit": 8000},
        {"label": "user_reminders", "value": "", "limit": 8000},
        {"label": "user_preferences", "value": "", "limit": 8000},
    ],
    model="anthropic/claude-3-7-sonnet-20250219",
    embedding="openai/text-embedding-ada-002",
    include_base_tools=False,
    tool_ids=[escalate_user_request_tool.id, clarify_user_request_tool.id, handle_orchestrator_message_tool.id],
    tools=["send_message"],
    tool_rules=[
        {
            "tool_name": "clarify_user_request",
            "type": "constrain_child_tools",
            "children": ["send_message"]
        },
        {
            "tool_name": "send_message",
            "type": "exit_loop"
        }
    ]
)

print(agent.id)
print("tools", [t.name for t in agent.tools])