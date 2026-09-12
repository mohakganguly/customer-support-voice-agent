import json
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

@dataclass
class ExtractedMemory:
    key: str
    value: str
    category: str


class MemoryExtractor:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )

    async def extract(
        self,
        conversation: str,
    ) -> list[ExtractedMemory]:
        """
        Extract useful long-term customer memories
        from a conversation.
        """

        prompt = f"""
You are a memory extraction system for a customer-support AI.

Analyze the conversation below and identify information that
is useful to remember across future customer-support conversations.

Only extract information that is:

- explicitly stated by the customer
- likely to remain useful in future conversations
- relevant to customer support
- non-sensitive

Do NOT extract:

- passwords
- authentication codes
- payment credentials
- temporary circumstances
- arbitrary small talk
- information already represented by backend business data
- information about other people

Allowed categories:

- preference
- context
- communication

Return ONLY valid JSON.

The JSON must have this structure:

{{
    "memories": [
        {{
            "key": "string",
            "value": "string",
            "category": "preference | context | communication"
        }}
    ]
}}

If there are no useful memories, return:

{{
    "memories": []
}}

Conversation:

{conversation}
"""

        response = await self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You extract structured customer memories. "
                        "Return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
        )

        content = response.choices[0].message.content

        if not content:
            return []

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return []

        memories = []

        for item in data.get("memories", []):
            key = item.get("key")
            value = item.get("value")
            category = item.get("category")

            if not key or not value or not category:
                continue

            if category not in {
                "preference",
                "context",
                "communication",
            }:
                continue

            memories.append(
                ExtractedMemory(
                    key=key,
                    value=value,
                    category=category,
                )
            )

        return memories