
import boto3
import json

from service.hugging_face.data_eg import eg2


def invoke_sage_maker_endpoint():
	# Create a SageMaker runtime client object using your IAM role ARN
	runtime = boto3.client('sagemaker-runtime',
						   aws_access_key_id='AKIA2TOOM5H45TSBVX5C',
						   aws_secret_access_key='CRDxrhccHbLe8BGAVj8qVDHG0VYs73yVcXQ/ViuM',
						   # aws_session_token=<your-session-token>,
						   region_name='us-east-2'
	)

	endpoint = "huggingface-pytorch-tgi-inference-2023-09-30-22-46-44-984"
	parameters = {
		'repetition_penalty': 4.,
		'length_penalty': 0.5,
		'temperature': 1,
		'max_gen_len': 4096,
		'max_length': 4096
	}
	input_data = {
		# "inputs": "[INST]<>You are a helpful assistant.<> What does a cat like to do?[/INST]",
		"inputs": eg2,
		"parameters": parameters
	}


	# Invoke the endpoint using the `invoke_endpoint` method of the SageMaker runtime client object
	response = runtime.invoke_endpoint(EndpointName=endpoint,
									   ContentType='application/json',
									   Body=json.dumps(input_data))

	# Parse the output data returned by the endpoint
	output_data = json.loads(response['Body'].read().decode())
	print(output_data)


if __name__ == '__main__':
	invoke_sage_maker_endpoint()