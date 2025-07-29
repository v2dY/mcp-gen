from fastmcp import Client
import asyncio
import os

async def main():
    host = os.getenv("MCP_HOST", "localhost")
    port = os.getenv("MCP_PORT", "8000")
    client = Client(f"http://{host}:{port}/mcp/")
    async with client:
        await client.ping()
        
        # List available operations
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()
        
        print(tools, resources, prompts)

asyncio.run(main())
