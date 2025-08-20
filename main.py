import os
import logging
import asyncio
from dataclasses import dataclass, field
from typing import Tuple, List, Union

import openai
from openai import OpenAIError
from tenacity import (
    retry, 
    wait_exponential_jitter, 
    stop_after_attempt, 
    retry_if_exception_type
)

# --- logging settings ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# --- model ---
@dataclass
class CoTConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 500
    system_prompt: str = "You are a powerful assistant."
    cot_prompt_template: str = (
        "Please think through the following user's prompt step by step, "
        "but do NOT provide the final answer:\n{user_prompt}"
    )
    answer_prompt_template: str = (
        "Using the following chain of thought, provide a complete and coherent "
        "answer to the user's prompt.\n\nUser Prompt: {user_prompt}\n\n"
        "Chain of Thought:\n{chain_of_thought}"
    )
    pause_seconds: float = 1.0
    retry_attempts: int = 3
    retry_backoff_max: int = 10


class ChainOfThoughtAssistant:
    def __init__(self, config: CoTConfig):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("Please set the OPENAI_API_KEY environment variable.")
        openai.api_key = api_key

        self.config = config

    @retry(
        retry=retry_if_exception_type(OpenAIError),
        wait=wait_exponential_jitter(multiplier=1, max=config.retry_backoff_max),
        stop=stop_after_attempt(config.retry_attempts),
        reraise=True
    )
    def _call_api(self, messages: List[dict]) -> str:
        logger.debug("Запрос к API: %s", messages)
        resp = openai.ChatCompletion.create(
            model=self.config.model,
            messages=messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )
        content = resp.choices[0].message.content.strip()
        if not content:
            raise ValueError("Получен пустой ответ от API")
        logger.debug("Ответ API: %s", content)
        return content

    async def _acall_api(self, messages: List[dict]) -> str:
        """
        Асинхронный вариант вызова (для openai>=0.27.0).
        """
        logger.debug("Асинхронный запрос к API: %s", messages)
        resp = await openai.ChatCompletion.acreate(
            model=self.config.model,
            messages=messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )
        content = resp.choices[0].message.content.strip()
        if not content:
            raise ValueError("Получен пустой ответ от API (async)")
        logger.debug("Асинхронный ответ API: %s", content)
        return content

    def generate_chain_of_thought(self, user_prompt: str) -> str:
        prompt = self.config.cot_prompt_template.format(user_prompt=user_prompt)
        messages = [
            {"role": "system", "content": self.config.system_prompt},
            {"role": "user", "content": prompt},
        ]
        logger.info("Генерируем цепочку рассуждений...")
        cot = self._call_api(messages)
        logger.info("Цепочка рассуждений получена.")
        return cot

    def generate_answer(self, user_prompt: str, chain_of_thought: str) -> str:
        prompt = self.config.answer_prompt_template.format(
            user_prompt=user_prompt,
            chain_of_thought=chain_of_thought
        )
        messages = [
            {"role": "system", "content": self.config.system_prompt},
            {"role": "user", "content": prompt},
        ]
        logger.info("Генерируем итоговый ответ...")
        answer = self._call_api(messages)
        logger.info("Итоговый ответ получен.")
        return answer

    def answer(self, user_prompt: str) -> Tuple[str, str]:
        cot = self.generate_chain_of_thought(user_prompt)
        # Пауза для читабельности в логе
        if self.config.pause_seconds:
            time_to_sleep = self.config.pause_seconds
            logger.debug(f"Sleeping for {time_to_sleep}s before final answer")
            asyncio.run(asyncio.sleep(time_to_sleep))  # блокирует только текущий поток
        answer = self.generate_answer(user_prompt, cot)
        return cot, answer

    async def aanswer(self, user_prompt: str) -> Tuple[str, str]:
        """
        Асинхронная версия всей цепочки.
        """
        # 1) Chain of Thought
        cot_prompt = self.config.cot_prompt_template.format(user_prompt=user_prompt)
        cot = await self._acall_api([
            {"role": "system", "content": self.config.system_prompt},
            {"role": "user", "content": cot_prompt},
        ])
        # 2) Пауза
        if self.config.pause_seconds:
            await asyncio.sleep(self.config.pause_seconds)
        # 3) Ответ
        ans_prompt = self.config.answer_prompt_template.format(
            user_prompt=user_prompt,
            chain_of_thought=cot
        )
        answer = await self._acall_api([
            {"role": "system", "content": self.config.system_prompt},
            {"role": "user", "content": ans_prompt},
        ])
        return cot, answer


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Chain-of-Thought Assistant")
    parser.add_argument("--async", action="store_true", help="Run in async mode")
    args = parser.parse_args()

    cfg = CoTConfig()
    assistant = ChainOfThoughtAssistant(cfg)

    if args.async:
        user_input = input("Enter your prompt: ")
        cot, ans = asyncio.run(assistant.aanswer(user_input))
    else:
        user_input = input("Enter your prompt: ")
        cot, ans = assistant.answer(user_input)

    print("\n--- Chain of Thought ---\n")
    print(cot)
    print("\n--- Final Answer ---\n")
    print(ans)
