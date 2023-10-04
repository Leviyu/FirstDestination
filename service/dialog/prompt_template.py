
"""
Llama2 Format Guide
https://huggingface.co/blog/llama2#how-to-prompt-llama-2

<s>[INST] <<SYS>>
{{ system_prompt }}
<</SYS>>
{{ user_msg_1 }} [/INST] {{ model_answer_1 }} </s><s>[INST] {{ user_msg_2 }} [/INST]


The training data format should follow:
```
{'conversations':[
    {"from": "human", "value": "Who are you?"},
    {"from": "gpt", "value": "I am Vicuna"},
    ...
]}
```
As  defined in here: https://github.com/OpenAccess-AI-Collective/axolotl/blob/main/src/axolotl/prompt_strategies/llama2_chat.py



"""
from typing import List
import tiktoken
from service.dialog.prompt_config import DEFAULT_MAX_TOKEN

# tokenizer = transformers.AutoTokenizer.from_pretrained("bert-base-uncased")
encoding = tiktoken.get_encoding("cl100k_base")

B_S, E_S = "<s>", "</s>"
B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"

CURREENT_EXCEPTIONS_LIST = [
    "I'm sorry, but I can't assist with that."
    "I'm sorry, but I can't generate a response to that.",
    "I'm sorry, but I can't assist with that request.",
    "but I can't assist with that request"
]

USER_S = "human"
SYSTEM_S = "system"
BOT_S = "gpt"


class PromptTemplate:
    system_prompt = None
    user_messages = []
    model_replies = []

    def __init__(self, system_prompt=None):
        system_prompt = system_prompt.replace("\n", "")
        system_prompt = system_prompt.replace("\t", "")
        system_prompt = system_prompt.replace("  ", "")
        self.system_prompt = system_prompt

    def add_user_message(self, message: str, return_prompt=True):
        self.user_messages.append(message)
        if return_prompt:
            return self.build_prompt()

    def add_model_reply(self, reply: str, includes_history=True, return_reply=True):
        reply_ = reply.replace(self.build_prompt(), "") if includes_history else reply
        self.model_replies.append(reply_)
        if len(self.user_messages) != len(self.model_replies):
            raise ValueError(
                "Number of user messages does not equal number of system replies."
            )
        if return_reply:
            return reply_

    def get_user_messages(self, strip=True):
        return [x.strip() for x in self.user_messages] if strip else self.user_messages

    def get_model_replies(self, strip=True):
        return [x.strip() for x in self.model_replies] if strip else self.model_replies

    def build_prompt(self):
        if len(self.user_messages) != len(self.model_replies) + 1:
            raise ValueError(
                "Error: Expected len(user_messages) = len(model_replies) + 1. Add a new user message!"
            )

        if self.system_prompt is not None:
            SYS = f"[INST] <<SYS>>\n{self.system_prompt}\n<</SYS>>"
        else:
            SYS = ""

        CONVO = ""
        SYS = "<s>" + SYS
        for i in range(len(self.user_messages) - 1):
            user_message, model_reply = self.user_messages[i], self.model_replies[i]
            conversation_ = f"{user_message} [/INST] {model_reply} </s>"
            if i != 0:
                conversation_ = "[INST] " + conversation_
            CONVO += conversation_

        CONVO += f"[INST] {self.user_messages[-1]} [/INST]"

        return SYS + CONVO

    def gather_training_date_for_multi_conversation(self, user_messages: List[str], model_replies: List[str]):

        if self.system_prompt is not None:
            SYS = f"[INST] <<SYS>>\n{self.system_prompt}\n<</SYS>>"
        else:
            SYS = ""

        CONVO = ""
        for i in range(len(user_messages)):
            user_message, model_reply = user_messages[i], model_replies[i]

            is_exception = False

            for exception in CURREENT_EXCEPTIONS_LIST:
                if exception in model_reply:
                    is_exception = True

            if i == 0:
                system_message = f"{B_SYS}{self.system_prompt}{E_SYS}"
            else:
                system_message = ""
            conversation_ = B_S + B_INST + system_message + user_message + E_INST + model_reply + E_S

            if is_exception is False:
                CONVO += conversation_

        return CONVO

    def gather_training_data_for_each_conversation(self, user_message: str, model_reply: str) -> str:

        for exception in CURREENT_EXCEPTIONS_LIST:
            if exception in model_reply:
                return ""

        if self.system_prompt is not None:
            SYS = f"[INST] <<SYS>>\n{self.system_prompt}\n<</SYS>>"
        else:
            SYS = ""

        system_message = f"{B_SYS}{self.system_prompt}{E_SYS}"
        conversation_ = B_S + B_INST + system_message + user_message + E_INST + model_reply + E_S

        return conversation_

    def gather_training_data_for_all_message(self) -> List[str]:
        conversations = []
        for i in range(len(self.user_messages)):
            user_message, model_reply = self.user_messages[i], self.model_replies[i]
            conversation = self.gather_training_data_for_each_conversation(user_message, model_reply)
            if conversation:
                conversations.append(conversation)
        return conversations

    def gather_messages_with_different_conversation_length(self):

        num_of_conversations_length = [1]
        all_conversations = []

        for conv_length in num_of_conversations_length:
            for start_message_index in range(0, len(self.user_messages) - conv_length, conv_length):
                user_messages = self.user_messages[start_message_index: start_message_index+conv_length]
                model_replies = self.model_replies[start_message_index: start_message_index + conv_length]
                conversation = self.gather_training_date_for_multi_conversation(user_messages, model_replies)
                token_length = len(encoding.encode(conversation))
                if token_length < DEFAULT_MAX_TOKEN * 0.8:
                    all_conversations.append(conversation)

        return all_conversations


    def gather_message_with_different_conversation_length_with_conv_format(self):
        num_of_conversations_length = [3]
        all_conversations = []

        for conv_length in num_of_conversations_length:
            for start_message_index in range(0, len(self.user_messages) - conv_length, conv_length):
                user_messages = self.user_messages[start_message_index: start_message_index+conv_length]
                model_replies = self.model_replies[start_message_index: start_message_index + conv_length]
                conversation = self.gather_training_date_for_multi_conversation_with_conv_format(user_messages, model_replies)
                if not conversation:
                    continue
                conversation_list = [""+self.flat_dict(x) for x in conversation['conversations']]

                token_length = len(encoding.encode("".join(conversation_list)))
                if token_length < DEFAULT_MAX_TOKEN * 0.8:
                    all_conversations.append(conversation)

        return all_conversations

    def flat_dict(self, target: dict):
        out = ', '.join("{!s}={!r}".format(key, val) for (key, val) in target.items())
        return out

    def gather_training_date_for_multi_conversation_with_conv_format(self, user_messages: List[str], model_replies: List[str]):
        """
        {'conversations': [
            {"from": "human", "value": "Who are you?"},
            {"from": "gpt", "value": "I am Vicuna"},
            ...
        ]}
        """


        if self.system_prompt is not None:
            SYS = f"[INST] <<SYS>>\n{self.system_prompt}\n<</SYS>>\n\n"
        else:
            SYS = ""
        conversations_list = [
            {
                "from": SYSTEM_S,
                "value": SYS
            }
        ]

        for i in range(len(user_messages)):
            user_message, model_reply = user_messages[i], model_replies[i]

            is_exception = False

            for exception in CURREENT_EXCEPTIONS_LIST:
                if exception in model_reply:
                    is_exception = True

            if is_exception is False:
                conversations_list.append(
                    {
                        "from": USER_S,
                        "value": self.filter_message(message=user_message)
                    }
                )
                conversations_list.append(
                    {
                        "from": BOT_S,
                        "value": self.filter_message(model_reply)
                    }
                )

        conversation_output = {
            'conversations': conversations_list
        }
        if len(conversations_list) < 3:
            return None
        return conversation_output


    def filter_message(self, message):
        message = message.replace("\n", "")
        message = message.replace("\t", "")
        message = message.replace("  ", "")
        return message



