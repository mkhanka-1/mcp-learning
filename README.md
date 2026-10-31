# mcp-learning

Small exercises while learning the Model Context Protocol (MCP) and building connectors for Claude.

## 01-mini-watchlist
A tiny remote MCP server with tools to add, remove and list stock symbols, plus a fake quote tool.
It started from a guided tutorial. Data is in memory and quotes are random.

Run it:
    cd 01-mini-watchlist
    python3 -m venv venv && source venv/bin/activate
    python -m pip install -r requirements.txt
    python mini_watchlist_server.py
Serves on http://localhost:8000/mcp

## What I learned
### What an MCP server is
- An MCP server is a small web server that exposes Python functions as "tools" that Claude can call.
- It is similar to an API, but it describes itself: the server tells the model what it can do, so no developer has to write the calling code.
- Claude is the caller. I type plain English and Claude turns it into a structured tool call.
- A server can also offer resources and prompts, but this exercise uses only tools.

### How tools are defined
- `@mcp.tool()` registers a normal Python function as a tool.
- The function name becomes the tool name, the docstring becomes the description, and the type hints become the input schema.
- Claude never sees my code, only the name, description and schema. The function body runs on my machine.
- The docstring at the top of the file is for human readers and is not sent to Claude. Server-level `instructions` are sent.
- Parameter names and type hints matter, because they tell Claude what to send.

### How a call flows
- When the connector connects, Claude asks the server for its tool list (`tools/list`) and receives every name, description and schema in advance.
- For each message, Claude decides whether a tool is needed, which one, and what inputs to send.
- The request is a small JSON message: method `tools/call`, with `params.name` and `params.arguments`, plus an `id` that matches the reply to the request.
- FastMCP looks up the tool, validates the arguments against the type hints, runs the function, and wraps the return value in a response.
- Claude reads the result and writes the final answer.

### How Claude chooses between tools and connectors
- There is no ranking or priority setting. Claude uses judgment based on my message and the tool descriptions.
- Naming the connector in the prompt is the most reliable way to control the choice.
- Near-identical descriptions in two tools or connectors cause ambiguity. The fix is to make each description say what is unique.
- Distinct tool names also help.

### Writing good docstrings
- State when to use the tool, what it returns, and what it cannot do.
- Add warnings Claude should pass on, such as "FAKE, demo only, not real data".
- Keep it to two to four sentences, with the key point first.
- Avoid vague text like "does stuff", and avoid describing code internals.
- Test by restarting the server, opening a new chat and trying differently worded requests.

### Connecting it to Claude
- Claude calls the server from Anthropic's cloud, so `localhost` is not reachable. A public HTTPS URL is needed, which I got with a Cloudflare tunnel.
- The connector URL must end in `/mcp`, because that is the only path the server answers on.
- The tunnel address changes every time the tunnel restarts.
- The name in Claude's connector settings is only a label. The name in the code is the server's own name. The URL is what actually connects them.
- Opening the server in a browser gives a 404 on `/`, which is normal, because it speaks MCP and not web pages.
- A Free plan allows one custom connector.

### Limits of this demo
- There is no authentication, so anyone with the URL can call it. This is acceptable only for throwaway fake data.
- The watchlist is stored in memory and resets when the server restarts.
- `get_fake_quote` returns random numbers and is not real data.
- The server only works while my Mac, the server window and the tunnel are all running.


### Hosting for real
- Real connectors run on an always-on host with a permanent HTTPS address, not on a laptop with a tunnel.
- Moving to a host means reading the port from the `PORT` environment variable, adding `requirements.txt`, and setting a start command.
- Before going public, a connector needs authentication, persistent storage, and secrets kept in environment variables and out of the code.