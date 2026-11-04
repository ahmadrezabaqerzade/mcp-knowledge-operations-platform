# Model Context Protocol (MCP)

## 1. Overview

Model Context Protocol (MCP) is an open protocol designed to standardize how AI applications connect to external data sources, tools, and contextual capabilities.

It provides a common communication interface between MCP clients and MCP servers.

MCP helps AI applications discover and use external capabilities without requiring a separate custom integration for every service.

## 2. Architecture

MCP follows a client-server architecture.

The main components are:

### 2.1 Host

The Host is the AI application that manages the overall interaction with MCP servers.

It is responsible for managing client connections and integrating external capabilities into the application.

### 2.2 Client

An MCP Client is responsible for communicating with an MCP Server.

It manages protocol communication, capability negotiation, and requests.

A host application can manage multiple MCP clients, commonly with one client connection per server.

### 2.3 Server

An MCP Server exposes capabilities to connected clients.

These capabilities can include:

- Tools
- Resources
- Resource Templates
- Prompts

An MCP server can provide access to APIs, databases, files, search systems, and other external functionality.

## 3. Communication Lifecycle

A typical MCP connection follows these stages:

1. The client establishes a connection with the server.
2. The client and server exchange initialization information.
3. Protocol versions and capabilities are negotiated.
4. The client discovers available server capabilities.
5. The client sends requests to invoke tools or retrieve context.
6. The server returns results.
7. The connection remains available until it is closed or terminated.

MCP uses JSON-RPC 2.0 as its underlying message format.

## 4. MCP Primitives

### 4.1 Tools

Tools are executable functions exposed by an MCP server.

They allow clients and AI applications to perform operations.

Examples include:

- Searching documents
- Querying databases
- Performing calculations
- Processing data
- Calling external APIs

Tools are generally model-controlled capabilities, although the host application remains responsible for authorization and execution policies.

### 4.2 Resources

Resources expose contextual data through identifiable URIs.

They provide information that clients can retrieve and use as context.

Examples include:

- Documentation
- Configuration data
- Database records
- Project information
- Knowledge documents

Resources are generally application-controlled context.

### 4.3 Resource Templates

Resource Templates define URI patterns that allow clients to request parameterized resources.

For example:

`knowledge://topics/{topic}`

The client can use a topic parameter to retrieve a specific knowledge resource.

### 4.4 Prompts

Prompts are reusable prompt templates exposed by an MCP server.

They help clients construct structured interactions for common tasks.

Examples include:

- Research workflows
- Code review
- Document analysis
- Technical explanations

Prompts are generally user-controlled interaction templates.

## 5. Protocol Features

MCP supports additional capabilities beyond the basic primitives.

Important protocol features include:

- Initialization and capability negotiation
- Notifications
- Progress reporting
- Logging
- Cancellation
- Pagination
- Sampling
- Elicitation
- Roots
- Completions
- Tasks, where supported by the protocol version and implementation

Not every implementation needs to support every feature.

## 6. Transport Mechanisms

MCP supports different transport mechanisms.

### 6.1 Standard Input/Output (stdio)

The stdio transport communicates through standard input and standard output.

It is commonly used when an MCP client launches a local server as a subprocess.

Important considerations:

- Standard output is reserved for protocol messages.
- Diagnostic messages should be written to standard error.
- The client generally manages the server process lifecycle.

### 6.2 Streamable HTTP

Streamable HTTP is designed for communication with remotely accessible MCP servers.

It uses HTTP POST and GET requests and supports streaming responses.

Important considerations include:

- HTTP endpoint configuration
- Session management where applicable
- Authentication and authorization
- Secure network communication
- Origin validation and DNS rebinding protection

The older HTTP+SSE transport is deprecated in favor of Streamable HTTP for modern MCP implementations.

## 7. Security Considerations

MCP integrations introduce security risks because servers may access external systems or perform operations.

Important security practices include:

- Validate all tool inputs.
- Apply authorization checks.
- Restrict filesystem access.
- Avoid exposing secrets.
- Use secure authentication mechanisms.
- Apply least-privilege permissions.
- Validate external data.
- Prevent command injection.
- Avoid trusting tool outputs as instructions.
- Require confirmation for sensitive operations where appropriate.

MCP does not automatically make a server or tool secure. Security must be implemented by the host, client, server, and underlying systems.

## 8. MCP Client Responsibilities

An MCP client commonly performs the following operations:

- Connect to an MCP server
- Initialize a session
- Discover tools
- Discover resources
- Discover resource templates
- Discover prompts
- Invoke tools
- Retrieve resources
- Retrieve prompt templates
- Handle protocol errors
- Manage connection lifecycle

## 9. Applications

MCP can be used to connect AI applications to:

- Knowledge bases
- Databases
- Filesystems
- Developer tools
- Search engines
- Business applications
- External APIs
- Data processing systems
- Internal enterprise services
