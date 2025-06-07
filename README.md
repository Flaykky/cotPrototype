
# Chain of Thought prototype (CoT) – Documentation

Overview

The Chain of Thought Assistant is a prototype built on top of the OpenAI API that leverages structured prompt engineering to produce more thoughtful and accurate responses. It does so by splitting the response process into two distinct steps:
	1.	Chain of Thought (CoT) Generation – Think step-by-step through the user prompt.
	2.	Final Answer Generation – Use the reasoning generated in step 1 to craft a complete and coherent final answer.

This separation encourages deeper reasoning and often leads to higher-quality responses.

⸻
## 📦 Features
	•	Synchronous and asynchronous operation
	•	Configurable via CoTConfig dataclass
	•	Built-in retry mechanism using tenacity
	•	Logging support for tracing and debugging
	•	Structured prompts to guide reasoning and response generation

⸻

## How It Works

Step 1: Chain of Thought Generation

Given a user prompt, the assistant first requests the model to think step by step, but not to provide the final answer. This allows the model to lay out logical reasoning or sub-steps that clarify the thought process.

Template:

Please think through the following user's prompt step by step, but do NOT provide the final answer:
{user_prompt}

This output is stored as the Chain of Thought.

⸻

Step 2: Final Answer Generation

Next, the assistant uses the generated chain of thought and combines it with the original user prompt to request a final, polished answer from the model.

Template:

Using the following chain of thought, provide a complete and coherent answer to the user's prompt.

User Prompt: {user_prompt}

Chain of Thought:
{chain_of_thought}


⸻

## ⚙️ Configuration – CoTConfig

You can fine-tune the assistant’s behavior via the CoTConfig dataclass:

Field	Type	Description
model	str	OpenAI model to use (e.g., gpt-4o-mini)
temperature	float	Sampling temperature (controls randomness)
max_tokens	int	Max tokens for each API call
system_prompt	str	System-level instructions to guide the assistant
cot_prompt_template	str	Template for generating the chain of thought
answer_prompt_template	str	Template for generating the final answer
pause_seconds	float	Optional pause between steps
retry_attempts	int	Retry attempts for failed API calls
retry_backoff_max	int	Max backoff duration in retry logic


⸻

## Usage

Prerequisites
	•	Python 3.8+
	•	Set the OPENAI_API_KEY environment variable

export OPENAI_API_KEY="your-openai-api-key"

Running the Assistant

Sync mode:

python assistant.py

Async mode:

python assistant.py --async

Sample Interaction

Enter your prompt: Why is the sky blue?

Output:

--- Chain of Thought ---
1. Sunlight contains all colors of visible light.
2. As sunlight passes through the atmosphere, it scatters.
3. Blue light scatters more than red due to its shorter wavelength.
4. Hence, we see a blue sky most of the time.

--- Final Answer ---
The sky appears blue because molecules in the Earth's atmosphere scatter blue light from the sun more than they scatter red light. This scattering causes the sky to look blue to our eyes.


⸻

## Internals

Retry Logic

The assistant uses the tenacity library to automatically retry failed OpenAI API requests (e.g., rate limits or transient issues). It retries on OpenAIError exceptions using exponential backoff with jitter.

Logging

Logs are written to the console with timestamps and log levels to aid in debugging.

⸻

## 📘 Notes and Best Practices
	•	The chain of thought should not contain the final answer, only reasoning.
	•	The final answer must rely on and reflect the reasoning provided earlier.
	•	This approach works especially well for complex, multi-step problems (e.g., math, logic, analysis).
	•	Adjust temperature to control creativity vs. accuracy.

⸻

## 🔄 Async Support

The aanswer() method and --async CLI flag allow the assistant to be used in asynchronous workflows, which is useful for integration into web apps or concurrent systems.

⸻

## 📤 API Support

The assistant uses:
	•	openai.ChatCompletion.create() for sync calls
	•	openai.ChatCompletion.acreate() for async calls

Make sure you are using openai SDK version >=0.27.0 to access async features.

⸻

## 📎 License & Attribution

This prototype is built for educational and experimental purposes using the OpenAI API. Respect OpenAI’s Usage Guidelines.

