# Setup Guide

Complete guide to get the Omni Multi-Agent System running on your local machine.

## Prerequisites

### Required Software
- **Python**: 3.11 or higher (3.13 recommended)
- **pip**: Latest version (`python3 -m pip install --upgrade pip`)
- **Git**: For cloning the repository

### Required API Keys
1. **Anthropic API Key**: For Claude Sonnet 4.5
   - Sign up at: https://console.anthropic.com/
   - Create API key in Settings → API Keys
   
2. **OpenAI API Key**: For text embeddings
   - Sign up at: https://platform.openai.com/
   - Create API key in API Keys section

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/omni_multi_agent.git
cd omni_multi_agent
```

### 2. Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed letta-client-X.X.X anthropic-X.X.X openai-X.X.X ...
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
LETTA_SERVER_URL=http://localhost:8283
```

**Load environment variables:**

**macOS/Linux:**
```bash
export $(cat .env | xargs)
```

**Windows (PowerShell):**
```powershell
Get-Content .env | ForEach-Object {
    $name, $value = $_.split('=')
    Set-Content env:\$name $value
}
```

### 5. Install and Start Letta Server

```bash
# Install Letta
pip install letta

# Configure Letta (first time only)
letta configure
```

**Configuration prompts:**
```
? LLM provider (anthropic, openai, groq, etc.): anthropic
? Anthropic API key: sk-ant-xxxxxxxxxxxxxxxxxxxx
? Embedding provider: openai
? OpenAI API key: sk-xxxxxxxxxxxxxxxxxxxx
? Default preset: memgpt_chat
```

**Start Letta server:**
```bash
letta server
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8283
```

**Keep this terminal open** - the server must run for agents to work.

### 6. Verify Letta Installation

Open a new terminal and verify the server is running:

```bash
curl http://localhost:8283/v1/health
```

Expected response:
```json
{"status": "ok"}
```

## Creating Agents

### Order of Creation

Agents must be created in this specific order (due to inter-agent references):

1. Orchestrator Agent (no dependencies)
2. Specialized Agents (Tasks, Projects, Preferences)
3. Conversational Agent (depends on orchestrator)

### Step-by-Step Agent Creation

**Open a new terminal** (keep Letta server running in the first terminal).

#### 1. Create Orchestrator Agent

```bash
python orchestrator_agent/orchestrator_agent.py
```

**Expected output:**
```
Successfully registered tools with IDs:
- create_orchestrator_plan: tool-xxxx-xxxx-xxxx
- delegate_agent_request: tool-xxxx-xxxx-xxxx
- update_requests_changelog: tool-xxxx-xxxx-xxxx
- evaluate_progress: tool-xxxx-xxxx-xxxx
- send_status_update: tool-xxxx-xxxx-xxxx
Agent ID: agent-abc123def456
Registered tools: ['create_orchestrator_plan_tool', 'delegate_agent_request_tool', ...]
```

**Copy the Agent ID** (e.g., `agent-abc123def456`)

#### 2. Create Specialized Agents

**Tasks Agent:**
```bash
python tasks_agent/tasks_agent.py
```

**Copy the Agent ID** from output.

**Projects Agent:**
```bash
python projects_agent/projects_agent.py
```

**Copy the Agent ID** from output.

**Preferences Agent:**
```bash
python preferences_agent/preferences_agent.py
```

**Copy the Agent ID** from output.

#### 3. Update Agent ID References

Now update the hardcoded agent IDs in the code:

**File: `orchestrator_agent/orchestrator_agent.py`**

Find the `agent_ids` dictionary (around line 85) and update:
```python
agent_ids = {
    "Conversational": "your-conversational-agent-id",  # Will update after step 4
    "Tasks": "your-tasks-agent-id",                     # From step 2
    "Projects": "your-projects-agent-id",               # From step 2
    "Reminders": "reminders-agent-id",                  # Not implemented yet
    "Preferences": "your-preferences-agent-id"          # From step 2
}
```

**File: `tasks_agent/tasks_agent.py`**

Find `send_orchestrator_message` function (around line 120) and update:
```python
client.agents.messages.create_async(
    agent_id="your-orchestrator-agent-id",  # From step 1
    ...
)
```

**File: `projects_agent/projects_agent.py`**

Same as tasks_agent - update orchestrator agent ID in `send_orchestrator_message`.

**File: `preferences_agent/preferences_agent.py`**

Same as tasks_agent - update orchestrator agent ID in `send_orchestrator_message`.

#### 4. Create Conversational Agent

**File: `conversational_agent/conversational_agent.py`**

Update the orchestrator agent ID in `escalate_user_request` function (around line 85):
```python
response = client.agents.messages.create_async(
    agent_id="your-orchestrator-agent-id",  # From step 1
    ...
)
```

Then create the agent:
```bash
python conversational_agent/conversational_agent.py
```

**Copy the Agent ID** and update it in `orchestrator_agent/orchestrator_agent.py` (the "Conversational" entry in `agent_ids`).

#### 5. Recreate Orchestrator Agent

Since we updated agent IDs, recreate the orchestrator:

```bash
python orchestrator_agent/orchestrator_agent.py
```

## Testing the System

### Using Letta CLI

```bash
# Chat with the conversational agent
letta run --agent your-conversational-agent-id
```

**Test interactions:**

```
> What are my tasks?
[Agent should respond about tasks, reading from memory]

> Add a task to review the code
[Should escalate to orchestrator, create task, and confirm]

> Create a project called "Website Redesign"
[Should create project and confirm]
```

### Using Python Client

Create a test script `test_agents.py`:

```python
from letta_client import Letta, MessageCreate, TextContent

client = Letta(base_url="http://localhost:8283")

# Replace with your conversational agent ID
AGENT_ID = "your-conversational-agent-id"

# Send a message
response = client.agents.messages.create(
    agent_id=AGENT_ID,
    messages=[MessageCreate(
        role="user",
        content=[TextContent(text="Add a task to review pull request #42")]
    )]
)

# Print response
for message in response.messages:
    print(f"{message.role}: {message.content}")
```

Run it:
```bash
python test_agents.py
```

## Troubleshooting

### Issue: "Connection refused" when creating agents

**Solution**: Make sure Letta server is running
```bash
# Check if server is running
curl http://localhost:8283/v1/health

# If not, start it
letta server
```

### Issue: "API key not found"

**Solution**: Export environment variables
```bash
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# Verify
echo $ANTHROPIC_API_KEY
```

### Issue: "Tool not found"

**Solution**: Tools are created dynamically. If you get this error:
1. Delete all agents: `letta delete --all-agents`
2. Recreate in correct order (Orchestrator → Specialized → Conversational)

### Issue: Agent creation fails with "Block not found"

**Solution**: The hardcoded `block_ids` in the code are placeholders. Either:
1. Create shared blocks first, or
2. Remove `block_ids` parameter and use separate blocks per agent

**Create shared blocks:**
```python
# In orchestrator_agent.py or a setup script
user_tasks_block = client.blocks.create(
    label="user_tasks",
    value="",
    limit=8000
)
print(f"user_tasks block ID: {user_tasks_block.id}")
# Use this ID in block_ids parameter
```

### Issue: Import errors

**Solution**: Make sure virtual environment is activated
```bash
which python
# Should show: /path/to/omni_multi_agent/venv/bin/python

# If not:
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

## Development Tips

### View All Agents
```bash
letta list agents
```

### Delete an Agent
```bash
letta delete agent your-agent-id
```

### View Agent Memory
```python
from letta_client import Letta

client = Letta(base_url="http://localhost:8283")
agent = client.agents.get("your-agent-id")

# View memory blocks
for block in agent.memory.blocks:
    print(f"{block.label}: {block.value}")
```

### Reset Agent Memory
```python
client.agents.update_memory_block(
    agent_id="your-agent-id",
    block_label="user_tasks",
    value=""
)
```

## Next Steps

After setup is complete:
1. Read `docs/ARCHITECTURE.md` to understand the system design
2. Review `README.md` for usage examples
3. Try `examples/basic_usage.py` for hands-on learning
4. Experiment with different requests

## Additional Resources

- [Letta Documentation](https://docs.letta.ai/)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [OpenAI API Docs](https://platform.openai.com/docs/)

---

**Need help?** Open an issue on GitHub or contact the maintainer.
