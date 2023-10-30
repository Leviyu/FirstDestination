from fastchat.conversation import get_conv_template

from data.prompt_config.digit_self_promot_config import SYS_MESSAGE, SYS_MESSAGE2

conv1 = get_conv_template("llama-2")
conv1.set_system_message(SYS_MESSAGE)
conv1.append_message(conv1.roles[0], "Hey, what up brother!")
# conv1.append_message(conv1.roles[1], "👻🐹. We will be doing some party today! Cya later!")
# conv1.append_message(conv1.roles[0], "Really, who is in the party tonigh?")
# conv1.append_message(conv1.roles[1], "😞. It's Thursday so prob not many people")
# conv1.append_message(conv1.roles[0],
#                     "what about Devon, that crazy mf, is gonna bring tons of people. So we can make it work.")
# conv1.append_message(conv1.roles[1], "🤣. Let's say 8pm?")
# conv1.append_message(conv1.roles[0],
#                     "Great, what about girls, can you bring some chicks as well tonight? It would be fun")


# conv2 = get_conv_template("llama-2")
conv2 = get_conv_template("vicuna_v1.1")
conv2.set_system_message(SYS_MESSAGE2)
conv2.append_message(conv2.roles[0], "Hey Hongyu, tell me a bit about yourself?")
# conv2.append_message(conv2.roles[1], "🤗. It must be really interesting. 🤩. What are you doing now?")
# conv2.append_message(conv2.roles[0], "nothing, just listening to music")

