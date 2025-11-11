# Examples

This directory contains example scripts demonstrating how to use the Omni Multi-Agent System.

## Prerequisites

1. Letta server must be running: `letta server`
2. All agents must be created (see `docs/SETUP.md`)
3. Set environment variables:
   ```bash
   export CONVERSATIONAL_AGENT_ID="your-agent-id"
   export LETTA_SERVER_URL="http://localhost:8283"
   ```

## Running Examples

### Basic Usage

Simple interactions showing core functionality:

```bash
python examples/basic_usage.py
```

**Demonstrates:**
- Asking questions about tasks/projects
- Adding tasks
- Creating projects
- Updating preferences
- Clarification flow

### Advanced Workflows

Complex multi-agent interactions:

```bash
python examples/advanced_workflows.py
```

**Demonstrates:**
- Creating projects with multiple tasks in one request
- Bulk task operations
- Context-aware requests using preferences
- Multi-agent coordination
- Memory inspection

## Example Output

### Basic Usage
```
=== Example 1: Simple Question ===
User: What tasks do I have?
Agent: You currently have no tasks. Would you like to add some?

=== Example 2: Add Task ===
User: Add a task to review the quarterly report by end of week
Agent: I've added the task "Review the quarterly report by end of week" to your task list.
```

### Advanced Workflows
```
=== Workflow 1: Project with Tasks ===
User: Create a new project called "Mobile App Development" and add these tasks:
    1. Design user interface mockups
    2. Set up development environment  
    3. Implement authentication flow
Agent: I've created the project "Mobile App Development" and added 3 tasks.
```

## Customization

Modify the examples to test your specific use cases:

```python
# Add your own example
def my_custom_workflow():
    message = "Your custom request here"
    response = send_message(message)
    print(response)
```

## Troubleshooting

**Error: "Connection refused"**
- Make sure Letta server is running: `letta server`

**Error: "Agent not found"**
- Set correct agent ID: `export CONVERSATIONAL_AGENT_ID=your-id`

**No response from agent**
- Check Letta server logs for errors
- Verify all agents are created correctly

## Next Steps

After running examples:
1. Review `docs/ARCHITECTURE.md` to understand what's happening under the hood
2. Modify examples to test edge cases
3. Create your own workflows
