

import ngrok

token = '2W52kLyRYmetup2ZxnbMbj9WRoR_7W47mGRBPV6dAHKJ7h3gj'
def connect():
	tunnel = ngrok.connect(3000, authtoken=token)
	print (f"Ingress established at {tunnel.url()}")


if __name__ == "__main__":
	connect()
