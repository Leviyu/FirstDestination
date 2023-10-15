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
HF_TOKEN = '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'
UTC_CUTOFF = dt.datetime(2023,8,28).replace(tzinfo=dt.timezone.utc)

class ChatFormatter:
	def __int__(self):
		self._chat_with_messages = None
		self._chat_with_characters = None
		self.training_prompt_list = None

	def format_chats(
			self,
			df_sessions: pd.DataFrame,
			df_messages: pd.DataFrame,
	) -> List[str]:
		training_prompt_list = []

		chat_sessions = list(df_sessions['id.2'].unique())
		sample_index = 0
		index = 0
		for chat_session in chat_sessions:
			index +=1
			if chat_session not in df_messages['chat_id'].unique():
				continue
			df_single_session_messages = df_messages.loc[df_messages['chat_id'] == chat_session]
			df_session = df_sessions.loc[df_sessions['id.2'] == chat_session]
			if len(df_single_session_messages) < CHAT_MESSAGES_LOWER_LIMIT:
				continue

			print(f"--> working on chat session {index} / {len(chat_sessions)}")
			training_prompts_from_session = self.process_single_chat_session(
				df_single_session_messages,
				df_session
			)
			if training_prompts_from_session:
				training_prompt_list.extend(training_prompts_from_session)
		self.training_prompt_list = training_prompt_list
		return training_prompt_list

	def process_single_chat_session(
			self,
			df_single_session_messages,
			df_session
	):
		try:
			chat_messages = df_single_session_messages
			chat_messages['chat_message_datatime'] = chat_messages['created_at'].apply(lambda x: parse(x))
			chat_messages = chat_messages.sort_values('chat_message_datatime')

			session_dict = df_session.to_dict(orient='records')[0]
			training_prompts = self.build_prompt_give_chat_messages_for_a_session(chat_messages, session_dict)
		except:
			training_prompts = []

		return training_prompts

	def build_system_prompt(self, session_dict):
		"""
		Background context for character defination and setting up the scenario on where the story happens.
		"""
		personality = session_dict['personality']
		scenario = session_dict['scenario']
		example_dialogs = session_dict['example_dialogs']
		char_name = session_dict['name.2']
		user_profile = session_dict['profile']
		user_name = session_dict['user_name']

		if personality != personality:
			personality = None
		if scenario != scenario:
			scenario = None
		if example_dialogs != example_dialogs:
			example_dialogs = None
		if user_profile != user_profile:
			user_profile = None

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
			session_dict: dict
	) -> List[str]:
		"""
		To account for different scenarios of messages pattern,
		we define a more uniform message pattern and format the chat messages accordingly

		* we always require the user to initiate the first message, if not exist, we add a default user message
		* if there is multiple messages from either the user or char, we combine them together into a single message
		* the chat session always ends with char answering, if the last message is from user, ignore it
		"""

		if session_dict['name.2'] != session_dict['name.2'] or session_dict['user_name'] != session_dict['user_name']:
			return []

		df_chat_messages.reset_index(inplace=True)
		system_prompt = self.build_system_prompt(session_dict)
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
			huggingface_hub.login(token=HF_TOKEN)

			data.push_to_hub(
				dataset_name
			)


if __name__ == '__main__':
	chat_sessions = str(ROOT_DIR) + '/data_processing/training_data/chats_2000_sessions.csv'
	df_sessions = pd.read_csv(chat_sessions)

	file_names = [
		'p_10_04_07',
		'p_10_01_03',
		'p_10_08_09'
	]
	df_messages = pd.DataFrame()
	for file_name in file_names:
		file_path = str(ROOT_DIR) + f'/data_processing/training_data/{file_name}.csv'
		df_temp = pd.read_csv(file_path)
		df_messages = pd.concat([df_messages, df_temp])

	formatter = ChatFormatter()
	formatter.format_chats(
		df_messages=df_messages,
		df_sessions=df_sessions
	)
	dataset_name = f'role_play_chat_v30'
	# dataset_name = f'role_play_chat_llama2_format_v25_100k_repeat_3_5'
	# dataset_name = f'test_sample'
	upload_to_hf = True

	save_to_file_name = str(ROOT_DIR) + '/data_processing/training_data/' + dataset_name + ".jsonl"
	formatter.write_to_file(save_to_file_name, upload_to_hf=upload_to_hf, dataset_name=dataset_name)


