
"""
Llama2 Format Guide
https://huggingface.co/blog/llama2#how-to-prompt-llama-2

<s>[INST] <<SYS>>
{{ system_prompt }}
<</SYS>>
{{ user_msg_1 }} [/INST] {{ model_answer_1 }} </s><s>[INST] {{ user_msg_2 }} [/INST]
"""
from typing import List

B_S, E_S = "<s>", "</s>"
B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"

CURREENT_EXCEPTIONS_LIST = [
    "I'm sorry, but I can't assist with that."
    "I'm sorry, but I can't generate a response to that.",
    "I'm sorry, but I can't assist with that request."
]

class PromptTemplate:
    system_prompt = None
    user_messages = []
    model_replies = []

    def __init__(self, system_prompt=None):
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

    def gather_training_date(self):
        if self.system_prompt is not None:
            SYS = f"[INST] <<SYS>>\n{self.system_prompt}\n<</SYS>>"
        else:
            SYS = ""

        CONVO = ""
        for i in range(len(self.user_messages)):
            user_message, model_reply = self.user_messages[i], self.model_replies[i]
            if i == 0:
                system_message = f"{B_SYS}{self.system_prompt}{E_SYS}"
            else:
                system_message = ""
            conversation_ = B_S + B_INST + system_message + user_message + E_INST + model_reply + E_S
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
