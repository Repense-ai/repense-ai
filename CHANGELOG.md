# Changelog

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
