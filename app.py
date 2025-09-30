from flask import Flask, request, jsonify
import requests
import urllib.parse
import re

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

        # Step 2: Extract deep_link_value from final URL
        parsed = urllib.parse.urlparse(final_url)
        query = urllib.parse.parse_qs(parsed.query)
        deep_link = query.get('deep_link_value', [None])[0]

        if deep_link:
            decoded = urllib.parse.unquote(deep_link)

            # Step 3: If decoded deep link is a Roblox web URL, follow it
            if decoded.startswith("https://www.roblox.com"):
                follow = requests.get(decoded, allow_redirects=True)
                final = follow.url

                # Step 4: Extract privateServerLinkCode from final URL
                match = re.search(r'https://www\.roblox\.com/games/\d+/[^?]+\?privateServerLinkCode=[a-zA-Z0-9]+', final)
                if match:
                    return jsonify({
                        'resolved_url': match.group(0)
                    })

                return jsonify({
                    'final_url': final,
                    'note': 'No privateServerLinkCode URL found'
                })

            return jsonify({
                'decoded_deep_link': decoded,
                'note': 'Deep link is not a Roblox web URL'
            })

        return jsonify({'final_url': final_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
