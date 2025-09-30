from flask import Flask, request, jsonify, gunicorn
import requests

app = Flask(__name__)

@app.route('/resolve')
def resolve():
    url = request.args.get('url')
    try:
        response = requests.get(url, allow_redirects=True)
        return jsonify({'final_url': response.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
