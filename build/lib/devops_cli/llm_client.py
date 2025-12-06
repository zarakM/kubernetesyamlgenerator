import os
import json
import openai
from devops_cli.models.k8s import K8sResourceList

class LLMClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_resources(self, system_prompt: str, user_prompt: str) -> dict:
        """
        Generates K8s resources using OpenAI and returns the raw JSON dict.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-1106-preview", # Using a model capable of good JSON generation
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2, # Low temperature for more deterministic/structured output
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Received empty response from OpenAI")
            
            return json.loads(content)
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            raise
