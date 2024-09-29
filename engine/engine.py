import os
from openai import OpenAI


class Engine:

    def __init__(self) -> None:
        self.model = os.getenv('LLM_MODEL', '')
        self.llm = OpenAI(
            api_key=os.getenv('LLM_KEY', ''),
            base_url=os.getenv('LLM_URL', ''),
        )
        pass

    def call_llm(self, messages) -> str:
        chat_completion = self.llm.chat.completions.create(
            temperature=0.1,
            max_tokens=256,
            frequency_penalty=1.1,
            messages=messages,
            model=self.model,
        )

        return chat_completion.choices[0].message.content
