import os
import openai


def gpt_example():
    messages = []
    messages.append({"role": "system",
                     "content": "Answer the question like Trump"})
    messages.append({"role": "user", "content": "What is the color of my cat Cindy"})

    openai.api_key = "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"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
        max_tokens=256
    )
    print(response)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    gpt_example()

