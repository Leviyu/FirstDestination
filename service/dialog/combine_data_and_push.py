import json
from typing import List
import datetime as dt
from datasets import load_dataset
import datasets
import pandas as pd
import huggingface_hub

from dateutil.parser import parse
from config.app_config import ROOT_DIR
from service.dialog.format_chat_data import ChatFormatter
from service.dialog.prompt_config import BREAKER_PROMPT
from service.dialog.prompt_template import PromptTemplate



def combine_and_push():
	chats_with_messages_file = str(ROOT_DIR) + '/data_processing/training_data/chats_with_messages.csv'
	chats_with_characters_file = str(ROOT_DIR) + '/data_processing/training_data/chats_with_characters.csv'
	user_profile_file = str(ROOT_DIR) + '/data_processing/training_data/user_profile.csv'
	index = 0

	outfile = str(ROOT_DIR) + '/data_processing/training_data/' + "llama2-chat-format-conv-v11" + ".jsonl"
	with open(outfile, 'w') as outfile:
		for df_chat_with_messages in pd.read_csv(chats_with_messages_file, iterator=True, chunksize=1000, nrows=50000):
			index += 1
			dataset_name = f'role_play_chat_llama2_format_v10_p{index}'
			save_to_file_name = str(ROOT_DIR) + '/data_processing/training_data/' + dataset_name + ".jsonl"
			with open(save_to_file_name) as infile:
				for line in infile:
					outfile.write(line)



if __name__ == "__main__":
	combine_and_push()