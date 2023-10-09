

import pandas as pd
import tiktoken
import transformers

from service.dialog.prompt_config import DEFAULT_MAX_TOKEN

tokenizer = transformers.AutoTokenizer.from_pretrained("bert-base-uncased")
encoding = tiktoken.get_encoding("cl100k_base")
from config.app_config import ROOT_DIR



def check_token_length():

	sample_data = str(ROOT_DIR) + '/data_processing/training_data/role_play_chat_llama2_format_v25_100k.jsonl'

	df = pd.read_json(sample_data, lines=True)
	print(f'size {len(df)}')

	for conv in df['conversations']:
		l = 0
		for single_conv in conv:
			# tokens = tokenizer.tokenize(str(single_conv))
			# token_length = len(tokens)
			token_length = len(encoding.encode(str(single_conv)))
			l += token_length
		if l > 4000 or l < 100:
			print(f'tolen length {l}')

	pass



if __name__ == "__main__":
	check_token_length()
	pass