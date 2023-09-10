from typing import List

import pandas as pd

from dateutil.parser import parse
from config.app_config import ROOT_DIR
from service.dialog.prompt_template import PromptTemplate
import transformers

tokenizer = transformers.AutoTokenizer.from_pretrained("bert-base-uncased")


DEFAULT_USER_FIRST_MESSAGE = "{{user}} waiting for {{char}} to initiate the conversation."
DEFAULT_MAX_TOKEN = 20000

class ChatFormatter:
	def __int__(self):
		self._chat_with_messages = None
		self._chat_with_characters = None
		self.training_prompt_list = None

	def format_chats(self, df_chat_with_messages: pd.DataFrame, df_chat_with_characeters: pd.DataFrame) -> List[str]:
		training_prompt_list = []

		df_chat_with_messages['chat_message_datatime'] = df_chat_with_messages['created_at.1'].apply(lambda x: parse(x))

		chat_sessions = list(df_chat_with_messages['id'].unique())
		skipped_chat_sessions = 0
		for chat_session in chat_sessions:
			chat_messages = df_chat_with_messages.loc[df_chat_with_messages['id'] == chat_session]
			if len(chat_messages) <= 10:
				skipped_chat_sessions += 1
				continue
			character_id = chat_messages['character_id'].values[0]
			characters_dict = df_chat_with_characeters.loc[df_chat_with_characeters['character_id'] == character_id].head(1).to_dict(orient='records')[0]
			chat_messages.sort_values('chat_message_datatime', inplace=True)
			training_prompt = self.build_prompt_give_chat_messages_for_a_session(chat_messages, characters_dict)
			training_prompt_list.append(training_prompt)
		self.training_prompt_list = training_prompt_list
		return training_prompt_list


	def build_system_prompt(self, personality: str, scenario: str, fts: str, example_dialogs: str):
		"""
		Background context for character defination and setting up the scenario on where the story happens.
		"""
		personality_prompt = f"You have the following personality {personality}. \n"
		scenario_prompt = f"Interact with the {{user}} assuming the following scenario {scenario}.\n" if scenario else ""
		example_prompt = f"Some example diaglos includes: {example_dialogs}" if example_dialogs else ""
		fts_prompt = f"Your character have the following fts: {fts}. \n" if fts else ""

		system_prompt = f"System Notes:\n" + personality_prompt + fts_prompt + scenario_prompt + example_prompt
		return system_prompt

	def build_prompt_give_chat_messages_for_a_session(self, df_chat_messages: pd.DataFrame, character_dict: dict):
		"""
		To account for different scenarios of messages pattern,
		we define a more uniform message pattern and format the chat messages accordingly

		* we always require the user to initiate the first message, if not exist, we add a default user message
		* if there is multiple messages from either the user or char, we combine them together into a single message
		* the chat session always ends with char answering, if the last message is from user, ignore it
		"""
		df_chat_messages.reset_index(inplace=True)
		# for message in df_chat_messages.to_dict():
		system_prompt = self.build_system_prompt(character_dict['personality'], character_dict['scenario'], character_dict['fts'], character_dict['example_dialogs'])
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

		finale_prompt = pt.gather_training_date()
		num_tokens = len(tokenizer.tokenize(finale_prompt))
		if num_tokens > DEFAULT_MAX_TOKEN:
			finale_prompt = ""
		return finale_prompt

	def write_to_file(self, file_name: str):
		raise NotImplementedError



if __name__ == '__main__':
	chats_with_messages_file = str(ROOT_DIR) + '/data_processing/training_data/chats_with_messages.csv'
	chats_with_characters_file = str(ROOT_DIR) + '/data_processing/training_data/chats_with_characters.csv'
	df_chat_with_messages = pd.read_csv(chats_with_messages_file, nrows=1000)
	df_chat_with_characters = pd.read_csv(chats_with_characters_file)

	formatter = ChatFormatter()
	formatter.format_chats(
		df_chat_with_messages=df_chat_with_messages,
		df_chat_with_characeters=df_chat_with_characters
	)


