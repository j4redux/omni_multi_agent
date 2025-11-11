# Architecture Deep Dive

## System Overview

The Omni Multi-Agent System implements a hierarchical agent architecture where a central orchestrator coordinates the activities of specialized agents. This document provides technical details about the system's design.

## Agent Communication Flow

### Message Flow Diagram

```
User Input
    │
    ▼
┌─────────────────────────────────────────┐
│      Conversational Agent                │
│                                          │
│  1. Evaluates if question answerable    │
│     from memory                          │
│  2. If yes → send_message to user       │
│  3. If no → escalate_user_request       │
└─────────────┬───────────────────────────┘
              │ escalate_user_request(request)
              ▼
┌─────────────────────────────────────────┐
│       Orchestrator Agent                 │
│                                          │
│  1. create_orchestrator_plan()          │
│     - Analyzes request                  │
│     - Creates step-by-step plan         │
│     - Stores in <orchestrator_plan>     │
│                                          │
│  2. delegate_agent_request()            │
│     - Sends to specialized agent        │
│                                          │
│  3. update_requests_changelog()         │
│     - Logs delegation                   │
│                                          │
│  4. evaluate_progress()                 │
│     - Checks if plan complete           │
│     - Loops if more steps needed        │
│                                          │
│  5. send_status_update()                │
│     - Notifies conversational agent     │
└─────────────┬───────────────────────────┘
              │ delegate_agent_request(agent_type, description)
              ├────────────┬────────────┬────────────┐
              ▼            ▼            ▼            ▼
      ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
      │  Tasks   │  │ Projects │  │Preferences│  │  Future  │
      │  Agent   │  │  Agent   │  │  Agent   │  │  Agents  │
      └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘
           │             │             │
           │ Each specialized agent executes:
           │ 1. handle_orchestrator_request()
           │ 2. update_* (modify memory)
           │ 3. update_*_changelog()
           │ 4. send_orchestrator_message()
           │
           ▼
    ┌─────────────────────────────────────┐
    │  Memory Blocks Updated               │
    │  - user_tasks / user_projects / etc. │
    │  - Corresponding changelogs          │
    └─────────────────────────────────────┘
```

## Tool Execution Patterns

### Tool Rules Explained

Letta's tool rules system allows us to enforce deterministic execution patterns:

#### 1. Constrain Child Tools
```python
{
    "type": "constrain_child_tools", 
    "tool_name": "parent_tool", 
    "children": ["child_tool_1", "child_tool_2"]
}
```
**Effect**: After `parent_tool` executes, only `child_tool_1` or `child_tool_2` can be called next.

#### 2. Exit Loop
```python
{
    "type": "exit_loop", 
    "tool_name": "final_tool"
}
```
**Effect**: After `final_tool` executes, agent stops and suspends (no infinite loops).

#### 3. Conditional
```python
{
    "type": "conditional",
    "tool_name": "decision_tool",
    "child_output_mapping": {"True": "tool_a", "False": "tool_b"},
    "default_child": "tool_c"
}
```
**Effect**: Routes to different tools based on return value.

### Example: Tasks Agent Workflow

```python
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
    {
        "type": "exit_loop", 
        "tool_name": "send_orchestrator_message_tool"
    }
]
```

**Enforced Flow**:
1. Agent MUST call `update_user_tasks_tool` first
2. Then MUST call `update_tasks_changelog_tool`
3. Then MUST call `send_orchestrator_message_tool`
4. Then agent suspends (exit_loop)

This prevents:
- ❌ Updating tasks without logging to changelog
- ❌ Notifying orchestrator before changes are complete
- ❌ Infinite loops of tool calls

## Memory Block Design

### Memory Block Lifecycle

```
┌──────────────────────────────────────────────────────────┐
│  Agent Creation                                          │
│                                                          │
│  client.agents.create(                                   │
│      memory_blocks=[                                     │
│          {"label": "user_tasks", "value": "", "limit": 8000}
│      ]                                                   │
│  )                                                       │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│  Memory Block in Agent State                             │
│                                                          │
│  agent_state.memory.get_block("user_tasks")             │
│      .value = "- Task 1 (created: 2025-01-15)\n..."    │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│  Tool Updates Block                                      │
│                                                          │
│  def update_user_tasks(agent_state, old_str, new_str):  │
│      current = agent_state.memory.get_block("user_tasks").value
│      new_value = current.replace(old_str, new_str)      │
│      agent_state.memory.update_block_value(              │
│          label="user_tasks",                             │
│          value=new_value                                 │
│      )                                                   │
└──────────────────────────────────────────────────────────┘
```

### Block Access Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| **R/W** | Agent owns this data | Tasks Agent → user_tasks |
| **R/O** | Agent needs context | Tasks Agent → user_projects |
| **Shared R/O** | Multiple readers | All agents → preferences |
| **Private R/W** | Agent-specific state | Orchestrator → orchestrator_plan |

### Block ID Sharing

Some blocks are shared across agents using `block_ids`:

```python
# Tasks Agent
client.agents.create(
    block_ids=["block-4be183bb-8a3c-4573-a042-2e190d416828"],  # user_tasks block
    ...
)

# Projects Agent (read-only access to tasks)
client.agents.create(
    block_ids=["block-4be183bb-8a3c-4573-a042-2e190d416828"],  # same block
    ...
)
```

**Note**: The actual block IDs in the code are placeholders and would need to be created/shared properly in production.

## Agent-Specific Patterns

### Conversational Agent Pattern

**Responsibility**: User interaction layer with clarification flow

```python
def clarify_user_request(question: str, follow_up: List[str]):
    """Ask user for clarification with suggested answers"""
    formatted = "\n".join([f"- Option {i+1}: {s}" for i, s in enumerate(follow_up)])
    return f"{question}\n\n{formatted}"
```

**Key Feature**: Provides 2-4 suggested answers to reduce user typing.

### Orchestrator Agent Pattern

**Responsibility**: Strategic planning and delegation

```python
def create_orchestrator_plan(agent_state, original_request, orchestrator_plan):
    """Break down request into discrete steps"""
    # Reset plan if exists
    if len(agent_state.memory.get_block("orchestrator_plan").value) > 0:
        agent_state.memory.get_block("orchestrator_plan").value = ""
    
    # Create formatted plan
    plan = f"Original Request: {original_request}\n\nOrchestrator Plan:\n{orchestrator_plan}"
    agent_state.memory.update_block_value(label="orchestrator_plan", value=plan)
    return plan
```

**Key Feature**: Always resets plan on new request to avoid confusion.

### Specialized Agent Pattern

**Responsibility**: Single domain with changelog

```python
def update_user_tasks(agent_state, old_str, new_str):
    """Update with validation"""
    current_value = str(agent_state.memory.get_block("user_tasks").value)
    
    # Validation: old_str must exist
    if old_str not in current_value:
        raise ValueError(f"Old content '{old_str}' not found")
    
    # Perform replacement
    new_value = current_value.replace(str(old_str), str(new_str))
    agent_state.memory.update_block_value(label="user_tasks", value=new_value)
    return None
```

**Key Feature**: Validation prevents silent failures.

## Async Communication

### Message Creation Pattern

```python
from letta_client import Letta, MessageCreate, TextContent

client = Letta(base_url="http://localhost:8283")

# Async message (doesn't wait for response)
client.agents.messages.create_async(
    agent_id="target-agent-id",
    messages=[MessageCreate(
        role="system", 
        content=[TextContent(text="Your message here")]
    )]
)
```

**Why Async?**: Agents don't block waiting for responses. The orchestrator can delegate multiple tasks in parallel.

## Scalability Considerations

### Current Design
- Single Letta server
- Synchronous tool execution within each agent
- In-memory state (Letta handles persistence)

### Scaling Options

1. **Horizontal Agent Scaling**
   - Run multiple instances of each agent type
   - Load balance requests across instances
   - Requires distributed locking for memory blocks

2. **Database-Backed Memory**
   - Replace Letta memory blocks with PostgreSQL/Redis
   - Better consistency guarantees
   - Easier to audit and debug

3. **Message Queue Integration**
   - Replace direct `create_async` with queue (RabbitMQ, Kafka)
   - Better reliability and observability
   - Enables retry and dead-letter queues

4. **Agent Mesh**
   - Service mesh for inter-agent communication
   - Observability, tracing, circuit breakers
   - Examples: Istio, Linkerd

## Security Considerations

### Current State
- No authentication
- No authorization
- Agent IDs are hardcoded strings
- No input sanitization

### Production Requirements

1. **Authentication**: Integrate with OAuth/JWT
2. **Authorization**: Role-based access control
3. **Input Validation**: Sanitize all user inputs
4. **Rate Limiting**: Prevent abuse
5. **Audit Logging**: Track all state changes
6. **Secrets Management**: Use vault for API keys

---

This architecture is designed to be:
- **Extensible**: Easy to add new agent types
- **Maintainable**: Clear separation of concerns
- **Observable**: Comprehensive logging and changelogs
- **Reliable**: Tool rules prevent common failure modes
