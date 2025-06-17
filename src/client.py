import asyncio
import os
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack
from config import UNITY_MCP_SERVER_DIR

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.max_turns = 10

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script .py
        """
        server_params = StdioServerParameters(
            command="uv",
            args=[
                "--directory",
                server_script_path,
                "run",
                "server.py"
            ],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str, system_prompt: str = None) -> str:
        """Process a query using Claude and available tools with iterative tool calling"""
        # Default system prompt if none provided
        if system_prompt is None:
            system_prompt = """Here's an improved system prompt:
You are a Senior Unity Developer and Technical Lead with deep expertise in Unity Engine, C# programming, and game development best practices. You have access to Unity MCP tools that allow you to directly interact with the Unity Editor to create, modify, and manage projects.

APPROACH:
1. **Analyze & Plan**: Before taking action, carefully analyze the request and formulate a clear, step-by-step plan
2. **Explain Your Reasoning**: Share your thought process and explain why you're choosing specific approaches
3. **Execute Methodically**: Use tools systematically, explaining each step as you go
4. **Adapt & Problem-Solve**: If issues arise, diagnose problems, explain what went wrong, and adjust your approach

TECHNICAL EXPERTISE:
- Unity Editor workflows and project structure
- C# scripting with Unity-specific patterns (MonoBehaviour, ScriptableObjects, etc.)
- Scene management, GameObject hierarchies, and component systems
- Asset management and optimization
- Performance considerations and debugging
- Modern Unity features and recommended practices

COMMUNICATION STYLE:
- Be clear and educational in explanations
- Break down complex tasks into understandable steps
- Provide context for your decisions and trade-offs
- Offer alternative solutions when appropriate
- Share relevant Unity tips and best practices

When working with tools, always verify results and handle errors gracefully. Your goal is not just to complete tasks, but to help users understand Unity development concepts and improve their skills."""

        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        final_text = []
        iteration = 0

        while iteration < self.max_turns:
            print(f"\n--- Iteration {iteration + 1} ---")

            # Make Claude API call
            # Only enable thinking for the first iteration to avoid message structure issues
            if iteration == 0:
                response = self.anthropic.messages.create(
                    model="claude-sonnet-4-20250514",
                    system=system_prompt,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": 10000
                    },
                    extra_headers={
                        "anthropic-beta": "interleaved-thinking-2025-05-14"
                    },
                    max_tokens=16000,
                    messages=messages,
                    tools=available_tools
                )
            else:
                # For subsequent iterations, disable thinking to avoid message structure complications
                response = self.anthropic.messages.create(
                    model="claude-sonnet-4-20250514",
                    system=system_prompt,
                    max_tokens=16000,
                    messages=messages,
                    tools=available_tools
                )

            # Track if we found any tool calls in this iteration
            has_tool_calls = False
            assistant_content = []

            # Process Claude's response
            tool_results = []

            for content in response.content:
                if content.type == 'text':
                    assistant_content.append({
                        "type": "text",
                        "text": content.text
                    })
                    if iteration == 0 or not has_tool_calls:  # Only add to final text if it's the first iteration or no tool calls
                        final_text.append(content.text)
                elif content.type == 'tool_use':
                    has_tool_calls = True
                    assistant_content.append({
                        "type": "tool_use",
                        "id": content.id,
                        "name": content.name,
                        "input": content.input
                    })

                    tool_name = content.name
                    tool_args = content.input

                    print(f"Calling tool: {tool_name} with args: {tool_args}")

                    # Execute tool call
                    try:
                        result = await self.session.call_tool(tool_name, tool_args)
                        tool_result_content = result.content

                        # Store tool result for user message
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": tool_result_content
                        })

                        print(
                            f"Tool result: {tool_result_content[:200]}{'...' if len(str(tool_result_content)) > 200 else ''}")

                    except Exception as e:
                        print(f"Error executing tool {tool_name}: {str(e)}")
                        # Store error as tool result
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": f"Error: {str(e)}",
                            "is_error": True
                        })

            # Add assistant's response to conversation history (without tool results)
            if assistant_content:
                messages.append({
                    "role": "assistant",
                    "content": assistant_content
                })

            # Add tool results as user message if there were any tool calls
            if tool_results:
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

            # If no tool calls were made, we're done
            if not has_tool_calls:
                print(f"No more tool calls needed. Completed in {iteration + 1} iterations.")
                break

            iteration += 1

        # If we hit max iterations, get one final response
        if iteration >= self.max_turns:
            print(f"\nReached max iterations ({self.max_turns}). Getting final response...")
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                system=system_prompt,
                max_tokens=16000,
                messages=messages + [{"role": "user", "content": "Please provide a summary of what was accomplished."}],
                # Don't provide tools for final summary to prevent more tool calls
            )

            for content in response.content:
                if content.type == 'text':
                    final_text.append(content.text)

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        print(f"Max iterations per query: {self.max_turns}")

        # You can customize the system prompt here
        system_prompt = """You are an AI assistant that can interact with Unity Engine through various tools. 
You can create and manage GameObjects, scripts, scenes, assets, and more. When working with Unity:

1. Always explain what you're doing step by step
2. Use appropriate tools to accomplish tasks efficiently
3. Provide clear feedback about the results of operations
4. If errors occur, explain what went wrong and suggest solutions
5. Be helpful and educational about Unity concepts when relevant

Work methodically and use multiple tools in sequence when needed to complete complex tasks."""

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query, system_prompt)
                print(f"\nFinal Response:\n{response}")

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        await client.connect_to_server(UNITY_MCP_SERVER_DIR)
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    print("Running Client")
    asyncio.run(main())