# OS-Copilot Prompt Topology

This document captures the prompt structure extracted from OS-Copilot, primarily referencing `oscopilot/prompts/friday_pt.py` and related files.

## Execute Prompt
The execute prompts are designed for code generation and task execution.

### Shell/AppleScript Generator
- **System Prompt:** Instructs the model to act as a world-class programmer generating only Shell or AppleScript code based on task requirements.
  - Expected output formats are strictly enclosed in code blocks:
    ```shell
    shell code
    ```
    or
    ```applescript
    applescript code
    ```
- **User Prompt:** Provides the execution environment context:
  - System Version
  - System Language (e.g., simplified chinese)
  - Working Directory
  - Task Name
  - Task Description
  - Information of Prerequisite Tasks (key: task name, value: description and return value)
  - Code Type

### Action Code Filter
- **System Prompt:** Designed to analyze a generated code string and match it against available tools. It returns the name of the tool if it's the most appropriate fit, or an empty string if no matching tool is suitable. Returns the tool name enclosed in `<action></action>` tags.
- **User Prompt:** Provides:
  - Tool Code Pair
  - Task Description

## Self Learning Prompt
These prompts are structured to design a step-by-step curriculum for learning a specific Python package's usage for a software application.

### Course Design
- **System Prompt:** Instructs the model to design a comprehensive JSON-formatted course, progressing from easy to complex.
  - Example output structure:
    ```json
    {
      "lesson_name": "Task: ... Input: ... Output: ... File Path: ..."
    }
    ```
  - Directives ensure versatility, clear input/output parameters, awareness of OS version, and logical progression built upon prior courses.
- **User Prompt:** Injects runtime specifics:
  - Software Name
  - Python Package Name
  - Demo File Path
  - File Content
  - Prior Course
  - System Version

## Text Extraction Prompt
A simplified prompt to extract file contents directly.
- Directives encourage organizing content dynamically, for example returning sheets in a spreadsheet as a dictionary of rows.
