# Omni Multi-Agent System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Letta](https://img.shields.io/badge/Framework-Letta-purple.svg)](https://github.com/letta-ai/letta)
[![Claude 3.7 Sonnet](https://img.shields.io/badge/LLM-Claude%203.7%20Sonnet-orange.svg)](https://www.anthropic.com/claude)

A sophisticated multi-agent orchestration system built with the [Letta framework](https://github.com/letta-ai/letta), demonstrating advanced agent engineering patterns and hierarchical task delegation.

## 🎯 Overview

This project showcases a production-ready multi-agent architecture where specialized agents collaborate to handle complex user requests. The system features:

- **Hierarchical Orchestration**: Central orchestrator delegates tasks to specialized agents
- **Persistent Memory**: Each agent maintains stateful memory blocks for context
- **Tool-Based Workflows**: Custom tools with enforced execution patterns
- **Agent Specialization**: Dedicated agents for conversations, tasks, projects, and preferences

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Input                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Conversational Agent                        │
│  • Handles user interaction                                  │
│  • Routes requests to orchestrator                           │
│  • Provides read-only access to all memory blocks           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Orchestrator Agent                         │
│  • Plans multi-step workflows                               │
│  • Delegates to specialized agents                          │
│  • Tracks request changelog                                 │
└─────────────┬───────────┬───────────┬─────────────┬─────────┘
              │           │           │             │
              ▼           ▼           ▼             ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
       │  Tasks   │ │ Projects │ │Preferences│ │(Future)  │
       │  Agent   │ │  Agent   │ │  Agent   │ │ Agents   │
       └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

### Agent Responsibilities

#### 1. Conversational Agent
- **Purpose**: User-facing interface
- **Memory**: Read-only access to tasks, projects, preferences
- **Tools**: 
  - `escalate_user_request`: Forward complex requests to orchestrator
  - `clarify_user_request`: Ask follow-up questions with suggestions
  - `handle_orchestrator_message`: Receive status updates

#### 2. Orchestrator Agent
- **Purpose**: Strategic workflow coordinator
- **Memory**: Orchestrator plan, requests changelog
- **Tools**:
  - `create_orchestrator_plan`: Break down complex requests
  - `delegate_agent_request`: Route to specialized agents
  - `update_requests_changelog`: Track all delegations
  - `evaluate_progress`: Monitor workflow completion

#### 3. Tasks Agent
- **Purpose**: Manage user's task list
- **Memory**: User tasks (R/W), tasks changelog (R/W), projects (R/O)
- **Tools**:
  - `update_user_tasks`: Modify task list
  - `update_tasks_changelog`: Log task changes
  - `send_orchestrator_message`: Report completion

#### 4. Projects Agent
- **Purpose**: Manage user's projects
- **Memory**: User projects (R/W), projects changelog (R/W), tasks (R/O)
- **Tools**:
  - `update_user_projects`: Modify project list
  - `update_projects_changelog`: Log project changes
  - `send_orchestrator_message`: Report completion

#### 5. Preferences Agent
- **Purpose**: Manage user preferences
- **Memory**: User preferences (R/W), preferences changelog (R/W)
- **Tools**:
  - `update_user_preferences`: Update preferences
  - `update_preferences_changelog`: Log preference changes
  - `send_orchestrator_message`: Report completion

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- [Letta](https://github.com/letta-ai/letta) server running locally
- Anthropic API key (for Claude 3.7 Sonnet)
- OpenAI API key (for embeddings)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/omni_multi_agent.git
   cd omni_multi_agent
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Letta server**
   ```bash
   letta server
   ```
   The server will start on `http://localhost:8283`

5. **Configure API keys**
   
   Set your API keys as environment variables:
   ```bash
   export ANTHROPIC_API_KEY="your-anthropic-key"
   export OPENAI_API_KEY="your-openai-key"
   ```

### Usage

Each agent can be initialized independently:

```bash
# Create the orchestrator (must be first)
python orchestrator_agent/orchestrator_agent.py

# Create specialized agents
python tasks_agent/tasks_agent.py
python projects_agent/projects_agent.py
python preferences_agent/preferences_agent.py

# Create the conversational agent (must be last)
python conversational_agent/conversational_agent.py
```

**Important**: Note the agent IDs printed during creation and update them in the respective files where agents reference each other.

## 🎓 Key Design Patterns

### 1. Tool Rules for Workflow Enforcement

Each agent uses tool rules to enforce specific execution patterns:

```python
tool_rules=[
    {
        "type": "constrain_child_tools", 
        "tool_name": "parent_tool", 
        "children": ["child_tool"]
    },
    {
        "type": "exit_loop", 
        "tool_name": "final_tool"
    }
]
```

This ensures tools are called in the correct order and prevents infinite loops.

### 2. Memory Block Architecture

Agents have different access levels to memory blocks:
- **Read-Write**: Agent can modify (e.g., Tasks Agent → user_tasks)
- **Read-Only**: Agent can reference but not modify (e.g., Tasks Agent → user_projects)

### 3. Async Message Passing

Agents communicate via async message passing:

```python
client.agents.messages.create_async(
    agent_id="target-agent-id",
    messages=[MessageCreate(role="system", content=[TextContent(text=message)])]
)
```

### 4. Changelog Pattern

All state-modifying agents maintain changelogs for auditability and debugging.

## 🧪 Example Workflows

### Simple Task Creation
```
User: "Add a task to review the quarterly report"
  → Conversational Agent
  → Escalate to Orchestrator
  → Delegate to Tasks Agent
  → Update tasks + changelog
  → Report back to user
```

### Complex Multi-Agent Request
```
User: "Create a new project for the website redesign and add 3 initial tasks"
  → Conversational Agent
  → Escalate to Orchestrator
  → Create orchestration plan (2 steps)
  → Delegate to Projects Agent (create project)
  → Delegate to Tasks Agent (create 3 tasks)
  → Report completion to user
```

## 📊 Memory Block Reference

| Agent           | Block Name           | Access | Size  | Purpose                    |
|-----------------|---------------------|--------|-------|----------------------------|
| Conversational  | user_tasks          | R/O    | 8000  | View user's tasks          |
| Conversational  | user_projects       | R/O    | 8000  | View user's projects       |
| Conversational  | user_preferences    | R/O    | 8000  | View user's preferences    |
| Orchestrator    | orchestrator_plan   | R/W    | 15000 | Current workflow plan      |
| Orchestrator    | requests_changelog  | R/W    | 15000 | History of delegations     |
| Tasks           | user_tasks          | R/W    | 8000  | Task list management       |
| Tasks           | tasks_changelog     | R/W    | 8000  | Task modification history  |
| Projects        | user_projects       | R/W    | 8000  | Project list management    |
| Projects        | projects_changelog  | R/W    | 8000  | Project change history     |
| Preferences     | user_preferences    | R/W    | 8000  | User preferences storage   |
| Preferences     | preferences_changelog| R/W   | 8000  | Preference change history  |

## 🔧 Configuration

### Model Configuration

All agents use:
- **LLM**: `anthropic/claude-3-7-sonnet-20250219`
- **Embeddings**: `openai/text-embedding-ada-002`
- **Base Tools**: Disabled (custom tools only)
- **Message Buffer**: Auto-clear enabled

### Agent ID Configuration

After creating agents, update these references:

1. In `conversational_agent/conversational_agent.py`:
   - Line ~125: Replace `"orchestrator-agent-id"` with actual orchestrator ID

2. In `tasks_agent/tasks_agent.py`, `projects_agent/projects_agent.py`, `preferences_agent/preferences_agent.py`:
   - In `send_orchestrator_message` function: Replace `"orchestrator-agent-id"`

3. In `orchestrator_agent/orchestrator_agent.py`:
   - In `delegate_agent_request` function: Update the `agent_ids` dictionary

## 🎯 Design Decisions

### Why Letta?
Letta provides:
- Persistent agent memory out of the box
- Flexible tool system with execution rules
- Multi-agent message passing
- Memory block management

### Why This Architecture?
- **Separation of Concerns**: Each agent has a single, well-defined responsibility
- **Scalability**: Easy to add new specialized agents
- **Auditability**: Changelogs track all state changes
- **Flexibility**: Orchestrator can adapt workflows based on user needs

### Why Tool Rules?
Tool rules enforce deterministic workflows and prevent common pitfalls:
- Ensures proper sequencing (e.g., update before notify)
- Prevents infinite loops
- Makes agent behavior predictable and testable

## 📝 Future Enhancements

- [ ] Add Reminders Agent for time-based tasks
- [ ] Implement Calendar Agent for scheduling
- [ ] Add authentication and user management
- [ ] Create web UI for agent interaction
- [ ] Add comprehensive test suite
- [ ] Implement agent performance monitoring
- [ ] Add vector search for semantic task/project lookup
- [ ] Create deployment guide (Docker, K8s)

## 🤝 Contributing

This is a portfolio project demonstrating agent engineering skills. Feedback and suggestions are welcome!

## 📄 License

MIT License - feel free to use this as a reference for your own agent systems.

## 👤 Author

**Johnny Heo**
- Portfolio: [Your Portfolio URL]
- LinkedIn: [Your LinkedIn URL]
- Email: [Your Email]

---

**Built with**: [Letta](https://github.com/letta-ai/letta) | [Claude 3.7 Sonnet](https://www.anthropic.com/claude) | Python 3.13
