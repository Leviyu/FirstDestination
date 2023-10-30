from text_generation import InferenceAPIClient
from text_generation import Client
from huggingface_hub import InferenceClient

from data.auth.auth_config import HF_TOKEN


def try_hugging_interface_direct():
    # HF Inference Endpoints parameter
    endpoint_url = "https://j88bxwy5fyxmekwp.us-east-1.aws.endpoints.huggingface.cloud"
    hf_token = HF_TOKEN

    # Streaming Client
    client = InferenceClient(endpoint_url, token=hf_token)

    # generation parameter
    gen_kwargs = dict(
        max_new_tokens=400,
        top_k=30,
        top_p=0.9,
        temperature=0.2,
        repetition_penalty=1.02,
        stop_sequences=["\nUser:", "<|endoftext|>", "</s>"],
    )
    # prompt
    prompt = "What is the first principle of physics!"

    print(client.text_generation(prompt, **gen_kwargs))


if __name__ == '__main__':
    try_hugging_interface_direct()