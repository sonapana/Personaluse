from mcp.server.fastmcp import FastMCP
#pip install langchain-mcp-adapters langchain-openai mcp
# Create an MCP server instance
mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two integers and returns the result."""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiplies two integers and returns the result."""
    return a * b

if __name__ == "__main__":
    # Run the server using the standard I/O (stdio) transport
    mcp.run(transport="stdio")