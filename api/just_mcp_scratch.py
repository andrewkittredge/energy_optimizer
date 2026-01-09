from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
import uvicorn

mcp = FastMCP("My MCP Server", stateless_http=True)


@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"


if __name__ == "__main__":
    # Get the Starlette app for streamable HTTP
    starlette_app = mcp.streamable_http_app()

    starlette_app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "*"
        ],  # Allow all origins for development; restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Run the server
    uvicorn.run(starlette_app, host="127.0.0.1", port=8000)
