import boto3
import json

from data.auth.auth_config import AWS_KEY, AWS_SECRET

def invoke_sage_maker_endpoint():
	runtime = boto3.client('sagemaker-runtime',
						   aws_access_key_id=AWS_KEY,
						   aws_secret_access_key=AWS_SECRET,
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
		"inputs": "What is the first principle of physics!",
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