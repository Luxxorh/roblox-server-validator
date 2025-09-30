from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

@app.route('/resolve')
def resolve():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL parameter'}), 400

    try:
        # Step 1: Follow the share link
        response = requests.get(url, allow_redirects=True)
        final_url = response.url

        # Step 2: Check if final URL is a usable game link
        match = re.search(r'https://www\.roblox\.com/games/\d+/[^?]+\?privateServerLinkCode=[a-zA-Z0-9]+', final_url)
        if match:
            return jsonify({'resolved_url': match.group(0)})

        # Step 3: If not, try to extract from intermediate redirect
        # Sometimes Roblox returns a JSON with deep_link_value
        try:
            data = response.json()
            deep = data.get("final_url") or data.get("deep_link_value")
            if deep and "privateServerLinkCode=" in deep:
                # Extract full joinable URL
                match = re.search(r'https://www\.roblox\.com/games/\d+/[^?]+\?privateServerLinkCode=[a-zA-Z0-9]+', deep)
                if match:
                    return jsonify({'resolved_url': match.group(0)})
        except:
            pass

        return jsonify({'final_url': final_url, 'note': 'No joinable game URL found'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
