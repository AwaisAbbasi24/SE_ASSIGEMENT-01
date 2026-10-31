from flask import Flask, request, jsonify
import secrets

app = Flask(__name__)

# Generate three unique API keys
API_KEYS = {
    secrets.token_hex(16): "Consumer 1",
    secrets.token_hex(16): "Consumer 2",
    secrets.token_hex(16): "Consumer 3"
}

# Display generated API keys
print("\n========== GENERATED API KEYS ==========")

for key, consumer in API_KEYS.items():
    print(f"{consumer}: {key}")

print("========================================\n")


@app.route('/process', methods=['POST'])
def process_text():

    # Get API key from request header
    api_key = request.headers.get('X-API-Key')

    # Validate API key
    if not api_key or api_key not in API_KEYS:
        return jsonify({
            "error": "Invalid or missing API key"
        }), 401

    # Read JSON data
    data = request.get_json(silent=True)

    # Validate JSON
    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON data"
        }), 400

    # Get text
    text = data.get('text')

    # Validate text
    if not isinstance(text, str):
        return jsonify({
            "error": "Please provide text as a string"
        }), 400

    # Process text
    processed_text = text.upper()

    # Return response
    return jsonify({
        "message": "Text processed successfully",
        "consumer": API_KEYS[api_key],
        "original_text": text,
        "processed_text": processed_text
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5001)