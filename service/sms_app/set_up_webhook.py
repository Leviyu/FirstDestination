from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook-endpoint', methods=['POST'])
def webhook():
    try:
        # Parse the incoming JSON data
        data = request.get_json()

        # Process the webhook data here
        # Example: Print the received data
        print("Received webhook data:", data)

        # You can add your own processing logic here

        return jsonify({"message": "Webhook received successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)