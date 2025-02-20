import openai
import os 
import time

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

prompt = "hello"

# first step of thinking 
def first_step(prompt):
    firstprompt = f"make a chain of thoughts on the user's prompt before answering, but do not write a ready-made response: {prompt}"

    firstrep = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a powerful assistant."},
            {"role": "user", "content": firstprompt}
        ],
        max_tokens=500,  
        temperature=0.1  
    )
    
    return firstrep['choices'][0]['message']['content'].strip()

# second step of thinking 
def second_step(prompt, firstresponse): 
    secondprompt = f"Based on the chain of thoughts, write a response to the user's answer. \n User Prompt: {prompt}\n chain of thoughts: {firstresponse}"

    secondrep = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a powerful assistant."},
            {"role": "user", "content": secondprompt}
        ],
        max_tokens=500,  
        temperature=0.1  
    )
    
    return secondrep['choices'][0]['message']['content'].strip()

def main(prompt):
    first_step_response = first_step(prompt)
    second_step_response = second_step(prompt, first_step_response)

    print(f"First Step Response: {first_step_response}")
    time.sleep(1)
    print(f"Second Step Response: {second_step_response}")

main(prompt)