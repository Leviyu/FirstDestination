import tiktoken
import transformers

tokenizer = transformers.AutoTokenizer.from_pretrained("bert-base-uncased")
encoding = tiktoken.get_encoding("cl100k_base")




def check_token_length(single_conv: str):
	# tokens = tokenizer.tokenize(str(single_conv))
	# token_length = len(tokens)
	token_length = len(encoding.encode(str(single_conv)))
	return token_length



if __name__ == "__main__":
	single_conv = "Hello, how is your cat!"
	token_len = check_token_length(single_conv)
	print(f'token_len {token_len}')
	pass