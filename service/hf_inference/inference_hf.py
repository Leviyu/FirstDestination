import requests

from data.auth.auth_config import HF_INFERENCE_BEARER_TOKEN, HF_INFERENCE_ENDPOINT
from data.inference_eg.example_conv import conv2


API_URL = HF_INFERENCE_ENDPOINT
headers = {
	"Authorization": HF_INFERENCE_BEARER_TOKEN,
	"Content-Type": "application/json"
}


def hf_inference():
	def query(payload):
		response = requests.post(API_URL, headers=headers, json=payload)
		return response.json()

	conv = conv2
	input = conv.get_prompt()

	parameters = {
		# 'repetition_penalty': 4,
		'length_penalty': 0.5,
		'temperature': 0.86,
		# 'max_gen_len': 2048,
		# 'min_length': 500,
		# 'max_length': 2048,
		'top_p': 0.86,
		'return_full_text': False,
		'max_new_tokens': 5596,
		# 'max_new_length': 4096,
		# 'do_sample': True
	}

	output = query({
		"inputs": input,
		"parameters": parameters
	})
	return output


if __name__ == '__main__':
	conv = hf_inference()
	print(conv)
	pass
