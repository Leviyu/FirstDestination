import json
from typing import List
import datetime as dt
from datasets import load_dataset
import datasets
import pandas as pd
import huggingface_hub

from dateutil.parser import parse
from config.app_config import ROOT_DIR
from service.dialog.prompt_config import BREAKER_PROMPT
from service.dialog.prompt_template import PromptTemplate


DEFAULT_USER_FIRST_MESSAGE = "{{user}} waiting for {{char}} to initiate the conversation."
CHAT_MESSAGES_LOWER_LIMIT = 20

class ChatFormatter:
	def __int__(self):
		self._chat_with_messages = None
		self._chat_with_characters = None
		self.training_prompt_list = None

	def format_chats(
			self,
	        df_chat_with_messages: pd.DataFrame,
			df_chat_with_characeters: pd.DataFrame,
			df_user_profile: pd.DataFrame
	) -> List[str]:
		training_prompt_list = []

		chat_sessions = list(df_chat_with_messages['id'].unique())
		sample_index = 0
		index = 0
		for chat_session in chat_sessions:
			chat_messages = df_chat_with_messages.loc[df_chat_with_messages['id'] == chat_session]
			index +=1

			chat_message_date = parse(chat_messages['created_at.1'].values[0])
			utc_cut_off = dt.datetime(2023,8,28).replace(tzinfo=dt.timezone.utc)
			if len(chat_messages) <= CHAT_MESSAGES_LOWER_LIMIT or chat_message_date < utc_cut_off:
				continue

			print(f"--> working on chat session {index} / {len(chat_sessions)}")
			training_prompts_from_session = self.process_single_chat_session(
				chat_messages,
				df_chat_with_characeters,
				df_user_profile,
			)
			if training_prompts_from_session:
				training_prompt_list.extend(training_prompts_from_session)
		self.training_prompt_list = training_prompt_list
		return training_prompt_list

	def process_single_chat_session(self, df_chat_messages, df_chat_with_characeters, df_user_profile):
		try:
			chat_messages = df_chat_messages.copy()
			chat_messages['chat_message_datatime'] = chat_messages['created_at.1'].apply(lambda x: parse(x))
			chat_messages = chat_messages.sort_values('chat_message_datatime')

			character_id = chat_messages['character_id'].values[0]
			user_id = chat_messages['user_id'].values[0]
			characters_dict = df_chat_with_characeters.loc[df_chat_with_characeters['character_id'] == character_id].head(1).to_dict(orient='records')[0]
			user_profile_dict = df_user_profile.loc[df_user_profile['id'] == user_id].head(1).to_dict(orient='records')[0]
			training_prompts = self.build_prompt_give_chat_messages_for_a_session(chat_messages, characters_dict, user_profile_dict)
		except:
			training_prompts = None

		return training_prompts

	def build_system_prompt(self, character_dict, user_profile_dict: dict):
		"""
		Background context for character defination and setting up the scenario on where the story happens.
		"""
		personality = character_dict['personality']
		scenario = character_dict['scenario']
		example_dialogs = character_dict['example_dialogs']
		char_name = character_dict['name']
		user_profile = user_profile_dict['profile']
		user_name = user_profile_dict['name']

		personality_prompt = f"You have the following personality {personality}. \n"
		char_symbol = "{{char}}"
		user_symbol = "{{user}}"
		intro_prompt = f"{char_symbol}'s name: {char_name}. {char_symbol} calls {user_symbol} by {user_name} or any name introduced by {user_symbol}."
		scenario_prompt = f"Interact with the {{user}} assuming the following scenario {scenario}.\n" if scenario else ""
		example_prompt = f"Some example diaglos includes: {example_dialogs}" if example_dialogs else ""
		user_profile_prompt = f"About {user_symbol}: {user_profile}." if user_profile else ""

		system_prompt = BREAKER_PROMPT + intro_prompt + user_profile_prompt + personality_prompt + scenario_prompt + example_prompt
		return system_prompt

	def build_prompt_give_chat_messages_for_a_session(
			self, df_chat_messages: pd.DataFrame,
			character_dict: dict,
			user_profile_dict: dict
	) -> List[str]:
		"""
		To account for different scenarios of messages pattern,
		we define a more uniform message pattern and format the chat messages accordingly

		* we always require the user to initiate the first message, if not exist, we add a default user message
		* if there is multiple messages from either the user or char, we combine them together into a single message
		* the chat session always ends with char answering, if the last message is from user, ignore it
		"""

		is_bad_conversation = self.is_bad_conv(character_dict, user_profile_dict)
		df_chat_messages.reset_index(inplace=True)
		system_prompt = self.build_system_prompt(character_dict, user_profile_dict)
		pt = PromptTemplate(system_prompt=system_prompt)

		user_conv = []
		char_conv = []
		is_char = False
		for i, row in df_chat_messages.iterrows():
			message = row['message']
			is_char = row['is_bot']

			if i == 0 and is_char is True:
				user_conv.append(DEFAULT_USER_FIRST_MESSAGE)

			# if we have content in both user and char conv and the current conv is user, then we decide to add prompt
			if user_conv and char_conv and is_char is False:
				pt.add_user_message(" ".join(user_conv))
				pt.add_model_reply(" ".join(char_conv))
				user_conv = []
				char_conv = []

			if is_char:
				char_conv.append(message)
			else:
				user_conv.append(message)

		if is_char is True and user_conv and char_conv:
			pt.add_user_message(" ".join(user_conv))
			pt.add_model_reply(" ".join(char_conv))

		# final_prompts = pt.gather_training_data_for_all_message()
		final_prompts = pt.gather_message_with_different_conversation_length_with_conv_format()

		return final_prompts

	def is_bad_conv(self, character_dict: dict, user_dict: dict):
		if not character_dict['name'] or not user_dict['name']:
			return True

		return False

	def write_to_file(self, file_name: str, dataset_name: str, upload_to_hf: bool = False):
		with open(file_name, 'w') as f:
			for i in range(len(self.training_prompt_list)):
				conv = self.training_prompt_list[i]
				json.dump(conv, f)
				if i != len(self.training_prompt_list) -1:
					f.write('\n')
		f.close()
		if upload_to_hf:
			data = datasets.Dataset.from_pandas(pd.DataFrame(data=self.training_prompt_list))
			huggingface_hub.login(token='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')

			data.push_to_hub(
				dataset_name
			)


if __name__ == '__main__':
	chats_with_messages_file = str(ROOT_DIR) + '/data_processing/training_data/chats_with_messages.csv'
	chats_with_characters_file = str(ROOT_DIR) + '/data_processing/training_data/chats_with_characters.csv'
	user_profile_file = str(ROOT_DIR) + '/data_processing/training_data/user_profile.csv'
	df_chat_with_messages = pd.read_csv(chats_with_messages_file, nrows=20000)

	df_chat_with_characters = pd.read_csv(chats_with_characters_file)
	df_user_profile = pd.read_csv(user_profile_file)
	formatter = ChatFormatter()
	formatter.format_chats(
		 df_chat_with_messages=df_chat_with_messages,
		 df_chat_with_characeters=df_chat_with_characters,
		 df_user_profile=df_user_profile
	)
	# dataset_name = f'role_play_chat_llama2_format_v20_20k'
	#
	# save_to_file_name = str(ROOT_DIR) + '/data_processing/training_data/' + dataset_name + ".jsonl"
	# formatter.write_to_file(save_to_file_name, upload_to_hf=True, dataset_name=dataset_name)
	# df_data = pd.read_csv(save_to_file_name)
	# file2 = str(ROOT_DIR) + '/data_processing/training_data/formatted_chat_messages_llama2_stype_v2_20k.csv'
	# df_data = pd.read_json(save_to_file_name)
	# df_data.head(20000).to_csv(file2, index=False)
	pass



