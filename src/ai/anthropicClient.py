import os
import re
import anthropic


class AnthropicClient:
    def __init__(self):
        self.client = anthropic.Anthropic(
            # defaults to os.environ.get("ANTHROPIC_API_KEY")
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )
        self.unity_project_path=os.getenv("UNITY_PROJECT_PATH")
        
    def prompt(self, clientMsg):
        claude_prompt = f"""
        You are a Unity expert. For this user prompt: "{clientMsg}",
        generate the C# scripts needed to implement the game. Output ONLY C# code inside ```csharp``` blocks.
            """
        message = self.client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": claude_prompt}
            ]
        )
        return message.content
    
    def extract_and_write_files(self, claude_output):
        code_blocks = re.findall(r'```csharp\n(.*?)```', claude_output, re.DOTALL)
        for i, code in enumerate(code_blocks):
            file_path = os.path.join(self.unity_project_path, f"Assets/Scripts/Script{i}.cs")
            with open(file_path, 'w') as f:
                f.write(code.strip())
                
    def save_scripts_to_unity(self, code_blocks):
        script_dir = os.path.join(self.unity_path, "Assets", "Scripts")
        os.makedirs(script_dir, exist_ok=True)
        paths = []
        for i, code in enumerate(code_blocks):
            file_path = os.path.join(script_dir, f"GeneratedScript{i}.cs")
            with open(file_path, 'w') as f:
                f.write(code.strip())
            paths.append(file_path)
        return paths
