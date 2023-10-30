import json
from os import listdir
from os.path import isfile, join
import pandas as pd

import datasets
import huggingface_hub
from fastchat.conversation import get_conv_template, Conversation

from config.app_config import ROOT_DIR
from service.dialog.format_chat_data import HF_TOKEN
from service.dialog.prompt_template import USER_S, SYSTEM_S, BOT_S
from data.prompt_config.digit_self_promot_config import SYS_MESSAGE

SYSTEM_MESSAGE = '''
'''

ROLE_ASS = "ASSISTANT"
ROLE_SYS = "SYSTEM"
ROLE_USER = "USER"


class FormatTextMessages():
	def __init__(self):
		self.conversations = []
		self.num_conv_round = 10

	def output_into_training_format(self, file_name: str, dataset_name: str, upload_to_hf: bool):
		output_conv_list = []
		for conv in self.conversations:
			output_conv_list.extend(self.format_conversations(conv))

		with open(file_name, 'w', encoding='utf-8') as f:
			for i in range(len(output_conv_list)):
				conv = output_conv_list[i]
				json.dump(conv, f, ensure_ascii=False)
				if i != len(output_conv_list) -1:
					f.write('\n')
		f.close()
		if upload_to_hf:
			data = datasets.Dataset.from_pandas(pd.DataFrame(data=output_conv_list))
			huggingface_hub.login(token=HF_TOKEN)

			data.push_to_hub(
				dataset_name
			)

	def format_conversations(self, conversation: Conversation):
		conv_list = []
		system_message = {
			 "from": SYSTEM_S,
			 "value": SYS_MESSAGE
		}
		length = len(conversation.messages)
		for i in range(0, length, self.num_conv_round):
			j = i
			current_conv = [system_message]
			while j < i + self.num_conv_round and j < length-1:
				user_message = conversation.messages[j]
				assistant_message = conversation.messages[j+1]
				j += 2
				if user_message[1] == "" or assistant_message[1] == "":
					continue
				new_conv = [
					  {
						  "from": USER_S,
						  "value": user_message[1]
					  },
					  {
						  "from": BOT_S,
						  "value": assistant_message[1]
					  }
				 ]
				current_conv.extend(new_conv)

			if len(current_conv) >= 6:
				conv_list.append({'conversations': current_conv})

		return conv_list

	def reduce_conv(self, conversation: Conversation) -> Conversation:
		new_messages = []
		conversation.messages.insert(0,
			['USER', "**waiting for Rick to initiate messages**"]
		)
		for message in conversation.messages:
			if new_messages == []:
				new_messages.append(message)
				continue

			old_role = new_messages[-1][0]
			if message[0] == old_role:
				new_messages[-1][1] += ". " + self.filter_message(message[1])
			else:
				message[1] = self.filter_message(message[1])
				new_messages.append(message)

		conversation.messages = new_messages
		return conversation

	def filter_message(self, message):
		message = message.replace("\n", "")
		message = message.replace("\t", "")
		message = message.replace("  ", "")
		return message

	def read_folder(self, folder_path: str, max_file: int):
		onlyfiles = [f for f in listdir(folder_path) if isfile(join(folder_path, f))][:max_file]

		for file in onlyfiles:
			file_name = folder_path + file
			self.read_text_file(file_name)

	def read_text_file(self, file_name: str):
		lines = open(file_name, 'r', encoding='utf-8')

		conv = get_conv_template("vicuna_v1.1")
		last_line = ""
		for line in lines:
			if last_line.startswith('Me'):
				conv.append_message(conv.roles[1], line)
			elif last_line.startswith('+'):
				conv.append_message(conv.roles[0], line)
			last_line = line
		conv.set_system_message(SYS_MESSAGE)
		new_conv = self.reduce_conv(conv)
		self.conversations.append(new_conv)

if __name__ == "__main__":
	agent = FormatTextMessages()
	folder_dir = str(ROOT_DIR) + "/data/text_messages/"
	hf_dataset_name = 'text_messages_v2'
	max_file = 100

	agent.read_folder(folder_dir, max_file)
	output_file = folder_dir + f'{hf_dataset_name}.jsonl'
	agent.output_into_training_format(file_name=output_file, dataset_name=hf_dataset_name, upload_to_hf=True)

