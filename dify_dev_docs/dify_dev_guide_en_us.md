# Dify Plugin Development Guide

## Table of Contents
1. [Overview](#overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Plugin Types Introduction](#plugin-types-introduction)
4. [Development Workflow](#development-workflow)
5. [Project Structure](#project-structure)
6. [Core Components Development](#core-components-development)
7. [Testing and Debugging](#testing-and-debugging)
8. [Packaging and Publishing](#packaging-and-publishing)
9. [Best Practices](#best-practices)
10. [Common Issues and Solutions](#common-issues-and-solutions)

## Overview

Dify is an open-source LLM application development platform that provides a powerful plugin system to extend its functionality. Through plugins, developers can add new tools, models, extensions, and agent strategies to Dify.

### Plugin System Features
- **Modular Design**: Supports multiple plugin types
- **Standardized Interface**: Unified development specifications and APIs
- **Permission Management**: Flexible permission configuration system
- **Easy Deployment**: Supports local development and remote deployment

## Development Environment Setup

### System Requirements
- Python 3.12+
- Operating System: Windows, macOS, Linux
- Network connection (for remote debugging)

### Install Dify CLI Tools

#### Windows Users
```bash
# Download the corresponding executable file
# Or install using package manager
```

#### macOS Users
```bash
# ARM64 architecture
./dify-plugin-darwin-arm64 plugin init

# Intel architecture
./dify-plugin-darwin-amd64 plugin init
```

#### Linux Users
```bash
./dify plugin init
```

### Install Python Dependencies
```bash
pip install werkzeug
pip install flask
pip install dify-plugin
```

## Plugin Types Introduction

Dify supports four main plugin types:

### 1. Tool Plugin
- **Purpose**: Provides various tool functionalities
- **Features**: Can call Dify internal tools and models
- **Use Cases**: API integration, data processing, external service calls

### 2. Model Plugin
- **Purpose**: Provides new model services
- **Features**: Limited to model-related functions only
- **Use Cases**: Custom LLM, text embedding, speech synthesis, etc.

### 3. Extension Plugin
- **Purpose**: Provides HTTP service extensions
- **Features**: Lightweight, focused on specific functionality
- **Use Cases**: Webhooks, API proxy, simple feature extensions

### 4. Agent Strategy Plugin
- **Purpose**: Implements custom AI agent logic
- **Features**: Focuses on agent behavior strategies
- **Use Cases**: Complex decision logic, multi-step task processing

## Development Workflow

### Step 1: Project Initialization
```bash
# Initialize project using Dify CLI
dify plugin init

# Follow prompts to fill in information:
# - Plugin name
# - Author information
# - Description
# - Development language (choose Python)
# - Plugin type
# - Permission configuration
```

### Step 2: Configure Permissions
Configure the following permissions based on plugin requirements:

#### Reverse Call Permissions
- **Tools**: Call Dify internal tools
- **Models**: Call Dify internal models
  - LLM: Large Language Models
  - Text Embedding: Text embedding
  - Rerank: Re-ranking
  - TTS: Text-to-Speech
  - Speech2Text: Speech recognition
  - Moderation: Content moderation

#### Other Permissions
- **Apps**: Call Dify applications
- **Storage**: Persistent storage
- **Endpoints**: Register endpoints

### Step 3: Develop Core Functionality
Implement corresponding functional modules based on plugin type.

### Step 4: Testing and Debugging
```bash
# Start plugin for debugging
python -m main
```

### Step 5: Package and Publish
```bash
# Package plugin
dify plugin package ./your_plugin_name
```

## Project Structure

### Standard Directory Structure
```
your_plugin/
├── _assets/             # Icons and visual resources
│   ├── icon.svg         # Plugin icon
│   └── icon-dark.svg    # Dark theme icon
├── provider/            # Provider definition and validation
│   ├── your_plugin.py   # Credential validation logic
│   └── your_plugin.yaml # Provider configuration
├── tools/               # Tool implementation (Tool plugins)
│   ├── your_tool.py     # Tool functionality implementation
│   └── your_tool.yaml   # Tool parameters and description
├── strategies/          # Strategy implementation (Agent plugins)
│   ├── your_strategy.py # Strategy implementation
│   └── your_strategy.yaml # Strategy configuration
├── endpoints/           # Endpoint implementation (Extension plugins)
│   ├── your_endpoint.py # Endpoint logic
│   └── your_endpoint.yaml # Endpoint configuration
├── utils/               # Helper functions (optional)
│   ├── __init__.py
│   └── helpers.py
├── working/             # Progress records and working files
├── .env.example         # Environment variable template
├── main.py              # Entry file
├── manifest.yaml        # Main plugin configuration
├── README.md            # Project documentation
├── GUIDE.md             # Development guide
├── PRIVACY.md           # Privacy policy
└── requirements.txt     # Dependency list
```

### Key File Descriptions

#### manifest.yaml
Core configuration file for the plugin, containing:
- Plugin basic information (name, version, author)
- Plugin type and permissions
- Dependencies
- Publishing configuration

#### main.py
Plugin entry file, responsible for:
- Initializing plugin
- Registering various components
- Starting services

#### requirements.txt
Python dependency management file, must include:
```
dify_plugin~=0.0.1b76
# Other project dependencies
```

## Core Components Development

### Tool Plugin Development

#### Tool Class Implementation
```python
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class YourTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # Get parameters
        param1 = tool_parameters.get("param1")
        param2 = tool_parameters.get("param2")
        
        # Implement tool logic
        result = self.process_parameters(param1, param2)
        
        # Return result
        yield self.create_text_message(result)
    
    def process_parameters(self, param1, param2):
        # Specific processing logic
        return f"Processing result: {param1} + {param2}"
```

#### Tool Configuration
```yaml
# tools/your_tool.yaml
name: "your_tool"
label: "Your Tool"
description: "This is a sample tool"
parameters:
  - name: "param1"
    type: "string"
    required: true
    label: "Parameter 1"
    description: "First input parameter"
  - name: "param2"
    type: "string"
    required: true
    label: "Parameter 2"
    description: "Second input parameter"
```

### Extension Plugin Development

#### Endpoint Implementation
```python
from typing import Mapping
from werkzeug import Request, Response
from dify_plugin import Endpoint

class YourEndpoint(Endpoint):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        # Handle request
        data = r.get_json()
        
        # Execute business logic
        result = self.process_request(data)
        
        # Return response
        return Response(
            result,
            status=200,
            content_type="application/json"
        )
    
    def process_request(self, data):
        # Specific processing logic
        return {"status": "success", "data": data}
```

#### Endpoint Configuration
```yaml
# endpoints/your_endpoint.yaml
path: "/api/endpoint"
method: "POST"
extra:
  python:
    source: "endpoints/your_endpoint.py"
```

### Agent Strategy Plugin Development

#### Strategy Implementation
```python
from dify_plugin import AgentStrategy

class YourStrategy(AgentStrategy):
    def _invoke(self, strategy_parameters: dict[str, Any]) -> Generator[StrategyInvokeMessage, None, None]:
        # Get strategy parameters
        context = strategy_parameters.get("context")
        
        # Implement strategy logic
        decision = self.make_decision(context)
        
        # Return decision result
        yield self.create_text_message(decision)
    
    def make_decision(self, context):
        # Specific decision logic
        return "Decision result based on context"
```

## Testing and Debugging

### Local Debugging
```bash
# Start plugin
python -m main

# Check log output
# Verify plugin starts correctly
```

### Remote Debugging
1. Configure environment variables
2. Start plugin
3. Test in Dify workspace

### Log Debugging
```python
import logging
from dify_plugin.config.logger_format import plugin_logger_handler

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)

# Use in code
logger.info("This is an info log")
logger.warning("This is a warning log")
logger.error("This is an error log")
```

## Packaging and Publishing

### Local Packaging
```bash
# Package plugin
dify plugin package ./your_plugin_name

# Generate .difypkg file
```

### Publishing Methods

#### 1. GitHub Repository Publishing
```bash
# Push code to GitHub
git add .
git commit -m "Initial commit"
git push origin main

# Share repository link
# Users can install directly via link
```

#### 2. Dify Plugin Marketplace Publishing
- Submit plugin package for review
- List on official marketplace after approval

### Version Management
- Use semantic versioning
- Update version in manifest.yaml
- Maintain update logs

## Best Practices

### Code Organization
1. **Modular Design**: Split complex functionality into multiple simple tools
2. **Code Reuse**: Extract common logic to utils directory
3. **Error Handling**: Comprehensive exception handling and user prompts

### Performance Optimization
1. **Asynchronous Processing**: Use generators for long-running tasks
2. **Resource Management**: Properly manage memory and connection resources
3. **Caching Strategy**: Use caching appropriately to improve response speed

### Security
1. **Input Validation**: Strictly validate user input
2. **Permission Control**: Principle of least privilege
3. **Data Protection**: Encrypt sensitive information storage

### User Experience
1. **Clear Documentation**: Detailed README and GUIDE
2. **Error Messages**: Friendly error information
3. **Example Code**: Provide usage examples

## Common Issues and Solutions

### Plugin Startup Failure
**Issue**: Plugin cannot start normally
**Solutions**:
- Check Python version (requires 3.12+)
- Verify complete dependency installation
- Check configuration file syntax

### Permission Configuration Error
**Issue**: Insufficient plugin permissions
**Solutions**:
- Reconfigure permissions in manifest.yaml
- Check Dify workspace permission settings
- Verify API key validity

### Packaging Failure
**Issue**: Cannot generate .difypkg file
**Solutions**:
- Check manifest.yaml configuration
- Ensure all referenced files exist
- Verify requirements.txt content

### Remote Connection Issues
**Issue**: Cannot connect to Dify platform
**Solutions**:
- Check network connection
- Verify environment variable configuration
- Confirm Dify service status

## Summary

Dify plugin development is a systematic process that requires developers to have:
- Solid Python programming foundation
- Understanding of Dify platform architecture
- Good code organization and testing habits
- Continuous learning and improvement attitude

By following this guide, you can:
1. Quickly set up development environment
2. Understand plugin development workflow
3. Master core component development methods
4. Learn best practices and debugging techniques
5. Successfully publish and maintain plugins

We hope this guide helps you succeed in your Dify plugin development journey!