from flask import Flask, request, jsonify
from flask_cors import CORS

from parser import Parse

app = Flask(__name__)
CORS(app, resources={r"/": {"origins": ""}})


job_parser = Parse(api_key=None)


@app.route("/analyze", methods=["POST"])
def analyze_job_desc():
    payload = request.get_json()
    job_text = payload.get('text', '')

    if not job_text:
        return jsonify({"error": "No text provided"}), 400
    try:
        parsed_job = job_parser.run(job_text)
    except:
        return jsonify({"GeminiError": "Gemini Gave Up"}), 401
    return jsonify(parsed_job)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
