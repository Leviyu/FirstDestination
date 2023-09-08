from typing import TypedDict, Literal, List

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"

Role = Literal["system", "user", "assistant"]

class Message(TypedDict):
    role: Role
    content: str

class LlmFineTune:
    def __int__(self):
        self._is_complete = False

    def convert_dialog_into_token(self, dialogs: list):
        for dialog in dialogs:
            if dialog[0]['role'] == 'system':
                dialog = [{
                    'role': dialog[1]['role'],
                    'content': B_SYS
                        + dialog[0]["content"]
                        + E_SYS
                        + dialog[1]["content"],
                }] + dialog[2:]
                pass
        return []


    # def chat_completion(
    #         self,
    #         dialogs: List[Dialog],
    #         temperature: float = 0.6,
    #         top_p: float = 0.9,
    #         max_gen_len: Optional[int] = None,
    #         logprobs: bool = False,
    # ):
    #     if max_gen_len is None:
    #         max_gen_len = self.model.params.max_seq_len - 1
    #     prompt_tokens = []
    #     unsafe_requests = []
    #     for dialog in dialogs:
    #         unsafe_requests.append(
    #             any([tag in msg["content"] for tag in SPECIAL_TAGS for msg in dialog])
    #         )
    #         if dialog[0]["role"] == "system":
    #             dialog = [
    #                          {
    #                              "role": dialog[1]["role"],
    #                              "content": B_SYS
    #                                         + dialog[0]["content"]
    #                                         + E_SYS
    #                                         + dialog[1]["content"],
    #                          }
    #                      ] + dialog[2:]
    #         assert all([msg["role"] == "user" for msg in dialog[::2]]) and all(
    #             [msg["role"] == "assistant" for msg in dialog[1::2]]
    #         ), (
    #             "model only supports 'system', 'user' and 'assistant' roles, "
    #             "starting with 'system', then 'user' and alternating (u/a/u/a/u...)"
    #         )
    #         dialog_tokens: List[int] = sum(
    #             [
    #                 self.tokenizer.encode(
    #                     f"{B_INST} {(prompt['content']).strip()} {E_INST} {(answer['content']).strip()} ",
    #                     bos=True,
    #                     eos=True,
    #                 )
    #                 for prompt, answer in zip(
    #                 dialog[::2],
    #                 dialog[1::2],
    #             )
    #             ],
    #             [],
    #         )
    #         assert (
    #                 dialog[-1]["role"] == "user"
    #         ), f"Last message must be from user, got {dialog[-1]['role']}"
    #         dialog_tokens += self.tokenizer.encode(
    #             f"{B_INST} {(dialog[-1]['content']).strip()} {E_INST}",
    #             bos=True,
    #             eos=False,
    #         )
    #         prompt_tokens.append(dialog_tokens)

        # generation_tokens, generation_logprobs = self.generate(
        #     prompt_tokens=prompt_tokens,
        #     max_gen_len=max_gen_len,
        #     temperature=temperature,
        #     top_p=top_p,
        #     logprobs=logprobs,
        # )




if __name__ == '__main__':
    eg_dialog = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "What's the best food?"},
        {"role": "assistant", "content": "Taco is the best food ever."},
    ]

    dialogs = [eg_dialog]


    l = LlmFineTune()
    tokens = l.convert_dialog_into_token(dialogs)
    pass

