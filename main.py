import os
import time
import logging
from typing import Tuple

import openai
from openai.error import OpenAIError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChainOfThoughtAssistant:
    """
    A class to manage chain-of-thought generation and answer responses using OpenAI's API.
    """

    def __init__(self,
                 model: str = "gpt-4o-mini",
                 temperature: float = 0.1,
                 max_tokens: int = 500):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = "You are a powerful assistant."

    @retry(
        retry=retry_if_exception_type(OpenAIError),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3)
    )
    def _chat_completion(self, messages: list) -> str:
        """Internal helper that calls the ChatCompletion endpoint with retries."""
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response.choices[0].message.content.strip()

    def generate_chain_of_thought(self, user_prompt: str) -> str:
        """
        Generate a chain of thought for the given user prompt without giving the final answer.

        :param user_prompt: The original prompt from the user
        :return: The generated chain of thought
        """
        cot_prompt = (
            f"Please think through the following user's prompt step by step, but do NOT provide the final answer:\n"
            f"{user_prompt}"
        )
        return self._chat_completion([
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": cot_prompt}
        ])

    def generate_answer(self, user_prompt: str, chain_of_thought: str) -> str:
        """
        Generate the final answer based on the provided chain of thought.

        :param user_prompt: The original prompt from the user
        :param chain_of_thought: The chain of thought previously generated
        :return: The final response string
        """
        answer_prompt = (
            f"Using the following chain of thought, provide a complete and coherent answer to the user's prompt.\n"
            f"User Prompt: {user_prompt}\n"
            f"Chain of Thought:\n{chain_of_thought}"
        )
        return self._chat_completion([
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": answer_prompt}
        ])

    def answer(self, user_prompt: str, pause: float = 1.0) -> Tuple[str, str]:
        """
        Orchestrate the two-step process of generating a chain of thought and then the final answer.

        :param user_prompt: The input prompt from the user
        :param pause: Seconds to wait between steps for readability
        :return: A tuple (chain_of_thought, final_answer)
        """
        logger.info("Starting chain-of-thought generation...")
        cot = self.generate_chain_of_thought(user_prompt)
        logger.info("Chain-of-thought generated.")

        time.sleep(pause)

        logger.info("Generating final answer...")
        answer = self.generate_answer(user_prompt, cot)
        logger.info("Final answer generated.")

        return cot, answer


def main():
    user_prompt = input("Enter your prompt: ")
    assistant = ChainOfThoughtAssistant()
    chain_of_thought, final_answer = assistant.answer(user_prompt)

    print("\n--- Chain of Thought ---")
    print(chain_of_thought)
    print("\n--- Final Answer ---")
    print(final_answer)

if __name__ == "__main__":
    main()
