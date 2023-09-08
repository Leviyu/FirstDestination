import pandas as pd
from dialog.prompt_template import PromptTemplate


def sample_model(prompt):
    return "I know!"

def generate_example_training_data(save_to_csv: bool = False):
    training_data = []
    for i in range(10):
        pt = PromptTemplate(system_prompt="You are a talking car who loves driving in the mountains.")
        pt.add_user_message("Hello! Who are you?")
        prompt = pt.build_prompt()
        llama_reply = sample_model(prompt)
        pt.add_model_reply(llama_reply, includes_history=True)
        pt.add_user_message("Where do you like driving specifically?")
        prompt = pt.build_prompt()
        llama_reply = sample_model(prompt)
        pt.add_model_reply(llama_reply, includes_history=True)
        prompt = pt.gather_training_date()

        training_data.append(prompt)

    df = pd.DataFrame(data=training_data, columns=['input'])
    df['index'] = [x for x in range(len(training_data))]

    if save_to_csv:
        df.to_csv('./sample_data.csv', index=False)

    return df


if __name__ == '__main__':
    data = generate_example_training_data(save_to_csv=True)