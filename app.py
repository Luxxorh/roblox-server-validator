from flask import Flask, request, jsonify
import requests
import urllib.parse

app = Flask(__name__)

@app.route('/resolve')
def resolve():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL parameter'}), 400

    try:
        # Step 1: Follow initial redirect
        response = requests.get(url, allow_redirects=True)
        final_url = response.url

        # Step 2: Check for deep_link_value in final URL
        parsed = urllib.parse.urlparse(final_url)
        query = urllib.parse.parse_qs(parsed.query)
        deep_link = query.get('deep_link_value', [None])[0]

        if deep_link:
            decoded = urllib.parse.unquote(deep_link)
            # Step 3: If deep link contains privateServerLinkCode, return it
            if "privateServerLinkCode=" in decoded:
                return jsonify({'final_url': decoded})

            # Step 4: Otherwise, follow the deep link manually
            if decoded.startswith("roblox://"):
                # Roblox deep links can't be followed via HTTP, so simulate
                return jsonify({'deep_link': decoded, 'note': 'Roblox deep link detected. Cannot follow roblox:// links via HTTP.'})

        return jsonify({'final_url': final_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
