import os
import anthropic


class AnthropicClient:
    def __init__(self):
        self.client = anthropic.Anthropic(
            # defaults to os.environ.get("ANTHROPIC_API_KEY")
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )
        
    def prompt(self, clientMsg):
        message = self.client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": f"Hello, Claude : {clientMsg}"}
            ]
        )
        return message.content
