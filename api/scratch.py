import asyncio
from fastmcp import Client

client = Client("http://127.0.0.1:8000/solar/mcp")


async def call_tool(name: str):
    async with client:
        tools = await client.list_tools()
        print("Available tools:", tools)
        result = await client.call_tool("greet", {"name": name})
        print(result)


asyncio.run(call_tool("Ford"))
