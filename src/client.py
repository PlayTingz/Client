import asyncio
from contextlib import AsyncExitStack
from typing import List, Any, Optional

import httpx
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI, OpenAI
from pydantic import Field

from config import get_config

load_dotenv()
cfg = get_config()

def get_model(vendor=cfg.MODEL.vendor):
    match vendor:
        case "openai":
            return "openai:o4-mini"
        case "anthropic":
            return "anthropic:claude-sonnet-4-20250514"
        case "zerog":
            return ZeroGChat(model=cfg.ZEROG.model_name, base_url=cfg.ZEROG.model_endpoint)

    raise ValueError("Invalid model")


class ZGServiceClient:
    def __init__(self, url=None, provider_address=None):
        self.url = url or cfg.ZEROG.service_api_url
        self.provider_address = provider_address or cfg.ZEROG.provider_address
        self.default_headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json',
        }

    def _build_request_params(self, query: str):
        return {
            'url': self.url,
            'json': {
                'providerAddress': self.provider_address,
                'query': query
            },
            'headers': self.default_headers.copy()
        }


    def _process_response(self, response):
        if response.status_code == 200:
            return response.json()
        else:
            return {'success': False, 'response': response.content}


    def get_headers(self, query: str):
        params = self._build_request_params(query)
        with httpx.Client() as client:
            response = client.post(**params)
            return self._process_response(response)


    async def aget_headers(self, query: str):
        params = self._build_request_params(query)
        async with httpx.AsyncClient() as client:
            response = await client.post(**params)
            return self._process_response(response)


class ZeroGChat(ChatOpenAI):
    zg_client: Optional[ZGServiceClient] = Field(default=None, exclude=True)

    def __init__(self, zg_client: Optional[ZGServiceClient] = None, *args, **kwargs):
        kwargs.setdefault('model_name', cfg.ZEROG.model_name)
        kwargs.setdefault('base_url', cfg.ZEROG.model_endpoint)
        kwargs.setdefault('api_key', '')

        super().__init__(*args, **kwargs)

        self.zg_client = zg_client or ZGServiceClient()


    def _get_prompt_from_messages(self, messages: List[BaseMessage]) -> str:
        """Extract prompt string from messages."""
        return ' '.join([str(message.content) for message in messages])


    def _process_headers_response(self, response):
        """Process and validate headers response from ZeroG service."""
        if not response.get('success', False):
            error_msg = response.get('response', 'Unknown error')
            raise RuntimeError(f'Failed to get headers: {error_msg}')

        headers = response['response'].copy()  # Don't mutate original
        headers["Authorization"] = "Bearer dummy-token"
        return headers


    def _create_openai_client(self, headers: dict, is_async: bool = False):
        """Create OpenAI client with custom headers."""
        client_class = AsyncOpenAI if is_async else OpenAI
        return client_class(
            base_url=self.openai_api_base,
            api_key=self.openai_api_key,
            default_headers=headers
        )


    def _get_sync_client(self, prompt: str):
        """Get synchronous OpenAI client with ZG headers."""
        response = self.zg_client.get_headers(prompt)
        headers = self._process_headers_response(response)
        return self._create_openai_client(headers, is_async=False)


    async def _get_async_client(self, prompt: str):
        """Get asynchronous OpenAI client with ZG headers."""
        response = await self.zg_client.aget_headers(prompt)
        headers = self._process_headers_response(response)
        return self._create_openai_client(headers, is_async=True)


    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Any:
        prompt = self._get_prompt_from_messages(messages)
        client = self._get_sync_client(prompt)
        self.client = client.chat.completions
        return super()._generate(messages, stop=stop, **kwargs)


    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Any:
        prompt = self._get_prompt_from_messages(messages)
        client = await self._get_async_client(prompt)
        self.async_client = client.chat.completions
        return await super()._agenerate(messages, stop=stop, **kwargs)


class MCPClient:
    def __init__(self):
        self.session = None
        self.agent = None
        self.exit_stack = AsyncExitStack()
        self.model = get_model()

    async def initialize(self):
        server_params = StdioServerParameters(
            command="uv",
            args=["--directory", cfg.UNITY_MCP.server_dir, "run", "server.py"],
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