# cotPrototype
simple COT (chain of thoughts) logic in LLM gpt-4o mini 

# ChainOfThoughtAssistant Documentation

## Overview

The **ChainOfThoughtAssistant** is a Python module designed to simplify and standardize a two-step reasoning process when interacting with OpenAI's ChatCompletion API:

1. **Chain-of-Thought Generation**: Generate a step-by-step reasoning outline without revealing the final answer.
2. **Final Answer Generation**: Produce a coherent and complete response based on the previously generated chain of thought.

This approach improves transparency and traceability of the model's reasoning process, and enables better error handling through retries and logging.

---

## Table of Contents

* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)

  * [Command Line Interface](#command-line-interface)
  * [Programmatic API](#programmatic-api)
* [API Reference](#api-reference)

  * [Class: ChainOfThoughtAssistant](#class-chainofthoughtassistant)

    * [`__init__`](#init)
    * [`answer`](#answer)
    * [`generate_chain_of_thought`](#generate_chain_of_thought)
    * [`generate_answer`](#generate_answer)
    * [Internal: `_chat_completion`](#internal-_chat_completion)
* [Error Handling and Retries](#error-handling-and-retries)
* [Logging](#logging)
* [Customization](#customization)
* [Example](#example)
* [License](#license)

---

## Installation

1. **Clone the repository** (or copy the module file into your project):

   ```bash
   git clone https://github.com/your-org/chain-of-thought-assistant.git
   cd chain-of-thought-assistant
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` should include:

   ```text
   openai>=0.27.0
   tenacity>=8.2.0
   ```

3. **Set your API key**:

   ```bash
   export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
   ```

---

## Configuration

The behavior of the assistant can be customized via constructor arguments:

| Parameter     | Type    | Default         | Description                                             |
| ------------- | ------- | --------------- | ------------------------------------------------------- |
| `model`       | `str`   | `"gpt-4o-mini"` | OpenAI model name to use for prompts.                   |
| `temperature` | `float` | `0.1`           | Sampling temperature (low values = more deterministic). |
| `max_tokens`  | `int`   | `500`           | Maximum tokens in the API response.                     |

---

## Usage

### Command Line Interface

Run the module directly to prompt via standard input:

```bash
python chain_of_thought_assistant.py
```

You will be prompted to enter your question. The assistant prints both the chain-of-thought and final answer.

### Programmatic API

Import and use in your own scripts:

```python
from chain_of_thought_assistant import ChainOfThoughtAssistant

assistant = ChainOfThoughtAssistant(
    model="gpt-4o-mini",
    temperature=0.2,
    max_tokens=600
)

cot, answer = assistant.answer("Explain quantum entanglement in simple terms.")
print("Chain of Thought:\n", cot)
print("Answer:\n", answer)
```

---

## API Reference

### Class: `ChainOfThoughtAssistant`

A class encapsulating the full two-step reasoning workflow.

#### `__init__(self, model: str = "gpt-4o-mini", temperature: float = 0.1, max_tokens: int = 500)`

* **model** (`str`): OpenAI model to use.
* **temperature** (`float`): Sampling temperature.
* **max\_tokens** (`int`): Max tokens per completion.

Initializes internal settings and system prompt.

---

#### `answer(self, user_prompt: str, pause: float = 1.0) -> Tuple[str, str]`

Executes the full workflow:

1. Calls `generate_chain_of_thought` to produce reasoning steps.
2. Waits for `pause` seconds (for readability/log separation).
3. Calls `generate_answer` with the chain-of-thought.

**Parameters:**

* `user_prompt` (`str`): The user’s query.
* `pause` (`float`): Delay between steps in seconds.

**Returns:**

* Tuple of `(chain_of_thought: str, final_answer: str)`.

---

#### `generate_chain_of_thought(self, user_prompt: str) -> str`

Generates the intermediate reasoning without revealing the final answer.

**Parameters:**

* `user_prompt` (`str`): The original user prompt.

**Returns:**

* `str`: The generated chain-of-thought text.

---

#### `generate_answer(self, user_prompt: str, chain_of_thought: str) -> str`

Produces the final answer using the provided chain-of-thought.

**Parameters:**

* `user_prompt` (`str`): The original user prompt.
* `chain_of_thought` (`str`): Previously generated reasoning.

**Returns:**

* `str`: The final assistant response.

---

#### Internal Method: `_chat_completion(self, messages: list) -> str`

A private helper to call `openai.ChatCompletion.create` with built-in retry logic.

* Decorated with `@retry` from `tenacity` to handle `OpenAIError`.
* Exponential backoff: up to 3 attempts, delays between 1s and 10s.

**Parameters:**

* `messages` (`list`): List of message dicts as per OpenAI API.

**Returns:**

* `str`: The raw text content of the API response.

---

## Error Handling and Retries

* Utilizes the `tenacity` library to retry on `openai.error.OpenAIError`.
* Configured to attempt up to **3** times with exponential backoff (1s, 2s, 4s...).

## Logging

* Uses Python's built-in `logging` module.
* INFO-level logs for start/end of each generation phase.
* Configure logging level or handlers as needed.

---

## Customization

* You may extend the class to override prompts, add additional steps, or integrate with other services.
* Example: subclass to inject a pre-processing step or to hook metrics collection.

---

## Example

```python
if __name__ == "__main__":
    from chain_of_thought_assistant import ChainOfThoughtAssistant

    assistant = ChainOfThoughtAssistant(
        model="gpt-4o-mini",
        temperature=0.05,
        max_tokens=700
    )
    cot, answer = assistant.answer("How does a two-stroke engine work?")

    print("--- Chain of Thought ---")
    print(cot)
    print("--- Final Answer ---")
    print(answer)
```

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) file for details.
