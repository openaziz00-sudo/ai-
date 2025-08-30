# dr.x-workflows Repository

## Overview
This repository contains a collection of dr.x workflow automation files. dr.x is a workflow automation tool that allows creating complex automations through a visual node-based interface. Each workflow is stored as a JSON file containing node definitions, connections, and configurations.

## Repository Structure
```
dr.x-workflows/
├── workflows/           # Main directory containing all dr.x workflow JSON files
│   ├── *.json          # Individual workflow files
├── README.md           # Repository documentation
├── claude.md           # This file - AI assistant context
└── [other files]       # Additional configuration or documentation files
```

## Workflow File Format
Each workflow JSON file contains:
- **name**: Workflow identifier
- **nodes**: Array of node objects defining operations
- **connections**: Object defining how nodes are connected
- **settings**: Workflow-level configuration
- **staticData**: Persistent data across executions
- **tags**: Categorization tags
- **createdAt/updatedAt**: Timestamps

## Common Node Types
- **Trigger Nodes**: webhook, cron, manual
- **Integration Nodes**: HTTP Request, database connectors, API integrations
- **Logic Nodes**: IF, Switch, Merge, Loop
- **Data Nodes**: Function, Set, Transform Data
- **Communication**: Email, Slack, Discord, etc.

## Working with This Repository

### For Analysis Tasks
When analyzing workflows in this repository:
1. Parse JSON files to understand workflow structure
2. Examine node chains to determine functionality
3. Identify external integrations and dependencies
4. Consider the business logic implemented by node connections

### For Documentation Tasks
When documenting workflows:
1. Verify existing descriptions against actual implementation
2. Identify trigger mechanisms and schedules
3. List all external services and APIs used
4. Note data transformations and business logic
5. Highlight any error handling or retry mechanisms

### For Modification Tasks
When modifying workflows:
1. Preserve the JSON structure and required fields
2. Maintain node ID uniqueness
3. Update connections when adding/removing nodes
4. Test compatibility with dr.x version requirements

## Key Considerations

### Security
- Workflow files may contain sensitive information in webhook URLs or API configurations
- Credentials are typically stored separately in dr.x, not in the workflow files
- Be cautious with any hardcoded values or endpoints

### Best Practices
- Workflows should have clear, descriptive names
- Complex workflows benefit from documentation nodes or comments
- Error handling nodes improve reliability
- Modular workflows (calling sub-workflows) improve maintainability

### Common Patterns
- **Data Pipeline**: Trigger → Fetch Data → Transform → Store/Send
- **Integration Sync**: Cron → API Call → Compare → Update Systems
- **Automation**: Webhook → Process → Conditional Logic → Actions
- **Monitoring**: Schedule → Check Status → Alert if Issues

## Helpful Context for AI Assistants

When assisting with this repository:

1. **Workflow Analysis**: Focus on understanding the business purpose by examining the node flow, not just individual nodes.

2. **Documentation Generation**: Create descriptions that explain what the workflow accomplishes, not just what nodes it contains.

3. **Troubleshooting**: Common issues include:
   - Incorrect node connections
   - Missing error handling
   - Inefficient data processing in loops
   - Hardcoded values that should be parameters

4. **Optimization Suggestions**:
   - Identify redundant operations
   - Suggest batch processing where applicable
   - Recommend error handling additions
   - Propose splitting complex workflows

5. **Code Generation**: When creating tools to analyze these workflows:
   - Handle various dr.x format versions
   - Account for custom nodes
   - Parse expressions in node parameters
   - Consider node execution order

## Repository-Specific Information
[Add any specific information about your workflows, naming conventions, or special considerations here]

## Version Compatibility
- dr.x version: [Specify the dr.x version these workflows are compatible with]
- Last updated: [Date of last major update]
- Migration notes: [Any version-specific considerations]
