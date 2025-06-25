import asyncio
from contextlib import AsyncExitStack
from typing import List, Any, Optional

import requests
import httpx

from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI, OpenAI

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config import UNITY_MCP_SERVER_DIR, get_model
load_dotenv('src/.env')
load_dotenv()  # load environment variables from .env


def get_headers(query: str):
    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json',
    }
    url = 'http://localhost:4000/api/services/headers'
    payload = {
        'providerAddress': '0xf07240Efa67755B5311bc75784a061eDB47165Dd',
        'query': query
    }
    res = requests.post(url, json=payload, headers=headers)

    if res.status_code == 200:
        return res.json()
    else:
        return {'success': False, 'response': res.content}


async def aget_headers(query: str):
    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json',
    }
    url = 'http://localhost:4000/api/services/headers'
    payload = {
        'providerAddress': '0xf07240Efa67755B5311bc75784a061eDB47165Dd',
        'query': query
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {'success': False, 'response': response.content}


class DynamicHeaderChatOpenAI(ChatOpenAI):
    def _get_prompt_from_messages(self, messages: List[BaseMessage]) -> str:
        last_message = next(message for message in reversed(messages) if isinstance(message, HumanMessage))
        return str(last_message.content)

    def _get_client(self, prompt):
        res = get_headers(prompt)
        if not res['success']:
            raise RuntimeError(f'Failed to get headers: {res["response"]}')

        headers = res['response']
        headers["Authorization"] = f"Bearer dummy-token"

        return OpenAI(
            base_url="http://50.145.48.68:30081/v1/proxy",
            api_key="",
            default_headers=headers
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Any:
        prompt = self._get_prompt_from_messages(messages)
        self.client = self._get_client(prompt).chat.completions
        return super()._generate(messages, stop=stop, **kwargs)

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Any:
        prompt = self._get_prompt_from_messages(messages)
        self.client = self._get_client(prompt)
        return await super()._agenerate(messages, stop=stop, **kwargs)


model = DynamicHeaderChatOpenAI(
    model_name='phala/llama-3.3-70b-instruct'
)

prompt = 'this is a test'
client = model._get_client(prompt)
res = client.chat.completions.create(
    messages=[{'role': 'user', 'content': prompt}],
    model='phala/llama-3.3-70b-instruct',
)

model.invoke('This is a test')




class MCPClient:
    def __init__(self, model):
        self.session = None
        self.agent = None
        self.exit_stack = AsyncExitStack()
        self.model = model

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
            model=self.model,#get_model(),
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


async def test():
    c = MCPClient(model=model)
    await c.initialize()
    res = await c.process_query('This is a test')
    print(res)

asyncio.run(test())

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