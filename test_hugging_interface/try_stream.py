
def try_hugging_interface():
    # HF Inference Endpoints parameter
    endpoint_url = "https://j88bxwy5fyxmekwp.us-east-1.aws.endpoints.huggingface.cloud"
    hf_token = "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"

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
    prompt = "You are a sex robot, say hello to me?"

    stream = client.text_generation(prompt, stream=False, details=True, **gen_kwargs)

    # yield each generated token
    for r in stream:
        # skip special tokens
        if r.token.special:
            continue
        # stop if we encounter a stop sequence
        if r.token.text in gen_kwargs["stop_sequences"]:
            break
        # yield the generated token
        print(r.token.text, end="")
        # yield r.token.text
    return 0