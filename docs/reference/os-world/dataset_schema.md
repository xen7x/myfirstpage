# OS-World Dataset Schema

This document outlines the core metadata structure used to evaluate UI action trajectories within the OS-World dataset.

## Core Evaluation Example Structure

Each task in OS-World is represented as a JSON object with the following schema:

- **`id`** (`string`): Unique identifier for the evaluation task (e.g., UUID).
- **`snapshot`** (`string`): The identifier of the environment snapshot (e.g., "chrome", "desktop") representing the initial state, populated with necessary data or opened apps.
- **`instruction`** (`string`): The natural language instruction dictating the task the agent needs to perform.
- **`source`** (`string`): A reference URL (e.g., forum, documentation, paper) from which the task originated.
- **`config`** (`list` of `object`): Scripts and parameters to set up the initial state.
  - Contains actions like downloading files, launching applications (e.g., `google-chrome --remote-debugging-port`), or updating browse history with specific timestamps (`visit_time_from_now_in_seconds`).
- **`trajectory`** (`string`): Directory path pointing to the annotated trajectory data (actions, screenshots, recordings).
- **`related_apps`** (`list` of `string`): Applications involved or opened during the task execution.
- **`evaluator`** (`object`): Definitions for automated task verification.
  - **`postconfig`** (`list`): Operations to perform *after* the agent finishes the task but *before* evaluation (e.g., restarting an app, sleeping).
  - **`func`** (`string`): The specific evaluation function to execute (e.g., `check_history_deleted`).
  - **`result`** (`object`): Defines what state or file to inspect (e.g., extracting an SQLite history database).
  - **`expected`** (`object`): The criteria for success (e.g., rule-based keyword matching ensuring specific entries are deleted or present).
- **`proxy`** (`boolean`): Indicates if a proxy is required for the environment.
- **`fixed_ip`** (`boolean`): Indicates if a fixed IP address is utilized.
- **`possibility_of_env_change`** (`string`): An indicator (e.g., "low") of how likely the external environment might change during evaluation, affecting reproducibility.
