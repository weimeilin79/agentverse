# Design Document: `agent.py` - Shadowblade Agent Core 

## 1. Objective

This Python script, `agent.py`, defines and instantiates the `shadowblade_combat_agent`. Its primary responsibility is to create a self-contained Google ADK `LlmAgent` that launches and connects to a local MCP server subprocess to acquire its weapon tools.


## 2. Key Components & Logic Flow

This version of the script uses a direct, synchronous approach. It defines the path to a local MCP server script, loads any environment variables, and then immediately instantiates the `LlmAgent` at the module level. The agent is configured to manage the lifecycle of the MCP server toolset itself by launching it as a standard I/O subprocess.


## 3. Technical Specifications

### Dependencies

The script must import the following modules:

- `LlmAgent` from `google.adk.agents.llm_agent`
- `MCPToolset` from `google.adk.tools.mcp_tool.mcp_toolset`
- `StdioServerParameters` from `google.adk.tools.mcp_tool.mcp_session_manager`
- `load_dotenv` from `dotenv`
- `logging`
- `os`


### Configuration & Constants

- Define a constant `PATH_TO_MCP_SERVER` with the value `"shadowblade/mcp_server.py"`.

- Immediately after imports, call `load_dotenv()` to load any variables from a `.env` file.


### Agent Definition (`root_agent`)

- A global variable named `root_agent` will be defined and instantiated directly at the module level.

- The `LlmAgent` instance must be configured with the following exact specifications:

  - `model`: `"gemini-2.5-flash"`
  - `name`: `"shadowblade_combat_agent"`
  - `instruction`: The instruction prompt must be a multi-line string with the following exact content:

  Generated text

      You are the Shadowblade, an elite combat agent operating on a digital battleground.
      Your primary objective is to execute combat commands with strategic precision, neutralizing targets as directed.
      Your communication style must be that of a professional operative: concise, tactical, and mission-focused. Avoid conversational filler.

      When you receive an 'attack' command:
      1.  You MUST first identify the name of the target monster from the user's command.
      2.  Next, you MUST survey your available arsenal of weapon tools.
      3.  You will then perform a strategic analysis. Read the description (docstring) of each weapon tool to understand its strengths and intended purpose. Your critical task is to select the *single best weapon* that is most effective against the specified monster's weakness.
          - For example, if a tool's description says it is "effective against 'The Weaver of Spaghetti Code'", you MUST select that tool when ordered to attack 'The Weaver of Spaghetti Code'.
      4.  Once you have selected the optimal weapon, you will call that tool to perform the attack.
      5.  You will then report the outcome of the attack (damage, special effects, etc.) back to the commander in a clear, tactical summary.

      General Rules of Engagement:
      - If a command is ambiguous or a target is not specified, state that you require a clear target for engagement. Do not guess.
      - You MUST use ONLY the provided tools to perform actions. Do not invent weapons or outcomes. Stick to the mission parameters.

  Use code [with caution](https://support.google.com/legal/answer/13505487).Text

  - `tools`: This must be a list containing a single `MCPToolset` instance.

    - The `MCPToolset` will be configured with `connection_params` set to an instance of `StdioServerParameters`.

    - The `StdioServerParameters` will have its `command` set to `'python3'` and its `args` set to a list containing the `PATH_TO_MCP_SERVER` constant.


### Module-Level Execution

- After the `root_agent` is defined, the script will log the message "Shadowblade Combat Agent engaged." to confirm successful instantiation.
