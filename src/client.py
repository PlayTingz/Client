import asyncio
import os
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack

from langchain_mcp_adapters.tools import load_mcp_tools

from config import UNITY_MCP_SERVER_DIR, DEFAULT_SYSTEM_PROMPT

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
load_dotenv()  # load environment variables from .env
# load_dotenv('src/.env')
# os.environ['OPENAI_API_KEY']

async def main(query):
    query = "Turn the player object orange"
    server_params = StdioServerParameters(
        command="uv",
        args=[
            "--directory",
            UNITY_MCP_SERVER_DIR,
            "run",
            "server.py"
        ],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            agent = create_react_agent(
                model="openai:o4-mini",
                tools=tools,
                checkpointer=InMemorySaver()
            )
            
            # Run the agent
            config = {"configurable": {"thread_id": "1"}}
            sf_response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": query}]},
                config
            )


if __name__ == "__main__":
    import sys

    print("Running Client")
    asyncio.run(main("Turn the player object yellow"))