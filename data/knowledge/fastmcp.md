# FastMCP

## 1. Overview

FastMCP is a Python framework for building Model Context Protocol (MCP) servers and clients.

It provides a high-level interface for exposing Python functions, data, and reusable prompt templates through MCP.

FastMCP reduces the amount of low-level protocol code developers need to write.

The FastMCP ecosystem includes server development, client communication, transport configuration, and integration with external systems.

## 2. Creating an MCP Server

The `FastMCP` class is the main entry point for creating a server.

A basic server can be initialized as follows:

```python
from fastmcp import FastMCP

mcp = FastMCP(
    name="Knowledge Server",
)
```

The server instance acts as the registration point for tools, resources, resource templates, and prompts.

A server can be started using:

```python
mcp.run()
```

The transport and other runtime options can be configured according to the deployment requirements and FastMCP version.

## 3. Tools

Tools expose executable Python functions to MCP clients.

FastMCP provides the `@mcp.tool` decorator to register functions.

Example:

```python
from fastmcp import FastMCP

mcp = FastMCP("Operations Server")


@mcp.tool
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two integers."""
    return a + b
```

FastMCP uses Python function information, including names, parameters, type annotations, and docstrings, to construct tool metadata.

Good tool design should include:

- Clear function names
- Explicit parameter types
- Useful descriptions
- Input validation
- Predictable return values
- Appropriate error handling

Tools can also be asynchronous when operations involve asynchronous I/O.

## 4. Resources

Resources expose data through URI-addressable endpoints.

Example:

```python
from fastmcp import FastMCP

mcp = FastMCP("Knowledge Server")


@mcp.resource("knowledge://overview")
def knowledge_overview() -> str:
    """Return an overview of available knowledge topics."""
    return "Python, Machine Learning, MCP, and FastMCP"
```

Resources are useful for exposing documentation, configuration, and contextual information.

## 5. Resource Templates

Resource Templates support parameterized resource URIs.

Example:

```python
@mcp.resource("knowledge://topics/{topic}")
def get_topic(topic: str) -> str:
    """Retrieve information about a knowledge topic."""
    return f"Requested topic: {topic}"
```

The URI parameter is provided when the client requests the resource.

Resource templates are useful for building dynamic knowledge retrieval interfaces.

## 6. Prompts

Prompts expose reusable templates that clients can retrieve.

Example:

```python
@mcp.prompt
def research_topic(topic: str) -> str:
    """Generate a research prompt for a given topic."""
    return f"Research the topic '{topic}' in depth."
```

Prompt functions can accept arguments and return structured prompt messages, depending on their implementation.

## 7. MCP Client

FastMCP provides a client interface for connecting to MCP servers.

A client can be used to:

- Establish a connection
- Discover available tools
- Call tools
- List resources
- Read resources
- Discover resource templates
- Retrieve prompts
- Handle server responses

FastMCP supports multiple transports, including stdio and Streamable HTTP.

The exact connection setup depends on the server transport and FastMCP version.

## 8. In-Memory Testing

FastMCP supports in-memory communication patterns that are useful for testing servers without launching an external process or opening a network connection.

This allows developers to test server capabilities and client interactions in isolation.

Testing should cover:

- Tool registration
- Tool execution
- Input validation
- Resource retrieval
- Resource template behavior
- Prompt retrieval
- Error handling

## 9. Transport Configuration

FastMCP supports different ways to run and connect to MCP servers.

Common transports include:

### 9.1 stdio

Useful for local MCP servers launched by an MCP host.

### 9.2 Streamable HTTP

Useful for remotely accessible MCP servers and network-based deployments.

Transport selection should reflect the deployment architecture, security requirements, and client capabilities.

## 10. Error Handling and Validation

A robust FastMCP server should validate user input and handle expected failures.

Important practices include:

- Type annotations
- Pydantic-based validation where appropriate
- Explicit error messages
- Controlled filesystem access
- Safe handling of external services
- Logging through appropriate channels
- Avoiding sensitive information in errors

## 11. Project Organization

A maintainable FastMCP project can separate server capabilities into dedicated modules.

Example:

```text
src/
└── mcp_mastery/
    ├── knowledge_server/
    │   ├── server.py
    │   ├── tools/
    │   ├── resources/
    │   └── prompts/
    ├── operations_server/
    │   ├── server.py
    │   ├── tools/
    │   └── validation/
    └── client/
```

This separation improves modularity, testing, and maintainability.

## 12. Applications

FastMCP can be used to build:

- Knowledge servers
- Database integration servers
- Document search tools
- Data processing services
- Internal developer tools
- AI application integrations
- Multi-server MCP platforms
