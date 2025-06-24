import asyncio
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config import UNITY_MCP_SERVER_DIR, get_model

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        self.session = None
        self.agent = None
        self.exit_stack = AsyncExitStack()


    async def initialize(self):
        server_params = StdioServerParameters(
            command="uv",
            args=["--directory", UNITY_MCP_SERVER_DIR, "run", "server.py"],
            env=None
        )

        read, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()

        tools = await load_mcp_tools(self.session)

        self.agent = create_react_agent(
            model=get_model(),
            tools=tools,
            checkpointer=InMemorySaver()
        )

    async def process_query(self, query: str):
        config = {"configurable": {"thread_id": "1"}}  # TODO: Thread Management

        result = await self.agent.ainvoke(
            {"messages": [HumanMessage(content=query)]},
            config
        )
        return result

    async def cleanup(self):
        await self.exit_stack.aclose()

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                for message in response['messages']:
                    print(message.content)

            except Exception as e:
                print(f"\nError: {str(e)}")

async def main():
    client = MCPClient()
    try:
        await client.initialize()
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    print("Running Client")
    asyncio.run(main())