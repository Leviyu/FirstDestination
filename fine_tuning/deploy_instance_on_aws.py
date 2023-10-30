# !pip install huggingface_hub
# !pip install -U sagemaker

import json
import sagemaker
import boto3
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri

from data.auth.auth_config import HF_TOKEN


def deploy_on_aws():
	try:
		role = sagemaker.get_execution_role()
	except ValueError:
		iam = boto3.client('iam')
		role = iam.get_role(RoleName='sagemaker_execution_role')['Role']['Arn']

	env = {
		'HF_MODEL_ID': "RickBigL/llama2_13b_v26_50k",
		'SM_NUM_GPUS': json.dumps(1),
		'HUGGING_FACE_HUB_TOKEN': HF_TOKEN
	}
	# create Hugging Face Model Class
	huggingface_model = HuggingFaceModel(
		image_uri=get_huggingface_llm_image_uri("huggingface", version="1.1.0"),
		env=env,
		role=role,
	)

	predictor = huggingface_model.deploy(
		initial_instance_count=1,
		instance_type="ml.g5.2xlarge",  # ml.p3.2xlarge
		container_startup_health_check_timeout=300,
	)

	return predictor


if __name__ == '__main__':
	predictor = deploy_on_aws()
	predictor.predict({
		"inputs": "My name is Julien and I like to",
	})
	pass