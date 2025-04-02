# Changelog

## Version 4.0.8

### New Features

#### Parallel Task Execution
- Added `ParallelTask` class for concurrent task execution in workflows
- Implemented thread pool-based parallel processing using `concurrent.futures`
- Added support for both single and list-based context handling
- Introduced flexible task execution with automatic task replication for list contexts

### Changes

#### Architecture
- Enhanced workflow engine with parallel execution capabilities
- Added thread-safe context handling for parallel tasks
- Improved error handling and logging for parallel task execution

### Bug Fixes
- No specific bug fixes in this release

### Removals
- No features or methods were removed

## Version 4.0.7

#### Multiple MCP Server Support
- Added support for running multiple MCP servers for OpenAI and Anthropic APIs
- Enhanced server configuration for multi-server environments

### Changes

#### Architecture
- Updated server management to handle multiple instances

### Bug Fixes
- No specific bug fixes in this release

### Removals
- No features or methods were removed

## Version 4.0.6

### New Features

#### Model Updates
- Added support for 'gemini-2.5-pro-exp-03-25' model
- Enhanced Google API with JSON schema support
- Enhanced Google API with Tool Usage

### Changes

#### Dependencies
- Updated dependencies

### Bug Fixes
- Fixed Anthropic chat loop issue

## Version 4.0.5

### New Features

#### Async Workflow Capabilities
- Added async workflow engine for task orchestration
- Implemented conditional branching in async workflows

#### MCP Server Integration
- Enhanced MCP server with workflow support
- Added async task handlers for MCP operations

### Changes

#### Architecture
- Refactored workflow engine to support async patterns

### Bug Fixes
- No specific bug fixes in this release

### Removals
- No features or methods were removed

## Version 4.0.4

### New Features

#### MCP Integration
- Added Server class for MCP integration
- Implemented async support for MCP tools
- Added tests for MCP server functionality

#### Model Updates
- Added grok-2-image model to supported models list

#### API Enhancements
- Added async classes for improved performance
- Enhanced server connection handling in AsyncChatAPI
- Added MCP tool support in chat APIs

### Changes

#### Architecture
- Refactored API classes to support async operations
- Updated server integration patterns
- Enhanced test coverage for async functionality

### Bug Fixes
- No specific bug fixes in this release

### Removals
- No features or methods were removed

## Version 4.0.3

### New Features

#### API Enhancements
- Added JSON schema support for Anthropic and OpenAI chat APIs
- Improved JSON mode handling in chat and vision APIs
- Added support for gpt-4.5-preview model to OpenAI provider

### Changes

#### Dependencies
- Updated dependency management to separate development dependencies from production dependencies

#### Provider Updates
- Enhanced mode priority hierarchy implementation:
  1. JSON mode (highest priority)
  2. TOOLS mode
  3. STREAM mode (lowest priority)
- Added JSON mode support to Anthropic provider
- Updated test configurations to validate JSON mode and model support

### Bug Fixes
- No specific bug fixes in this release

### Removals
- No features or methods were removed

## Version 4.0.2

### New Features

#### ChatAPI
- Added `thinking` parameter to the `__init__` method
- Updated `call_api` method to handle thinking parameter:
  - When thinking is enabled, sets `json_data['thinking']` with 75% of max_tokens budget
  - Adjusts temperature to 1.0 when thinking is enabled
- Updated `get_output` method to handle thinking responses:
  - Returns both thinking and output if thinking is enabled

### Changes

#### ChatAPI
- Added `thinking` attribute initialization in `__init__` method
- Modified `call_api` method to include thinking logic
- Modified `get_output` method to include thinking logic

### Bug Fixes
- No specific bug fixes in this release

### Removals
- No features or methods were removed
