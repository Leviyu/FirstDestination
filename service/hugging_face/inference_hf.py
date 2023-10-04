import requests

from service.hugging_face.data_eg import eg4

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf"
headers = {"Authorization": "Bearer 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"}



eg_simple =  """
Imagine you are a cat, how is your morning!
"""


def hf_inference():
	def query(payload):
		response = requests.post(API_URL, headers=headers, json=payload)
		return response.json()

	parameters = {
		# 'repetition_penalty': 4,
		# 'length_penalty': 0.5,
		'temperature': 0.9,
		# 'max_gen_len': 4096,
		# 'min_length': 100,
		# 'max_length': 4096,
		'top_p': 0.85,
		'max_length': 1000,
		'return_full_text': False,
		'max_new_length': 1000
		# 'do_sample': True
	}

	output = query({
		"inputs": eg4,
		"parameters": parameters

	})
	print(output)
	return output


if __name__ == '__main__':
	hf_inference()