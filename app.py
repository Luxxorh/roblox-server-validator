# app.py
from flask import Flask, request, jsonify
import requests
from urllib.parse import urljoin
import re

app = Flask(__name__)

def follow_roblox_redirects(share_link):
    """Follow redirects to get final private server URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
    }
    
    current_url = share_link
    session = requests.Session()
    session.headers.update(headers)
    
    for i in range(10):  # max 10 redirects
        try:
            response = session.get(current_url, allow_redirects=False, timeout=10)
            
            # Handle HTTP redirects
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location')
                if location:
                    if not location.startswith(('http://', 'https://')):
                        location = urljoin(current_url, location)
                    current_url = location
                    continue
            
            # Check if we reached the final URL
            if response.status_code == 200:
                final_pattern = r"https://www\.roblox\.com/games/\d+/[^?]+\?privateServerLinkCode="
                if re.search(final_pattern, current_url):
                    return current_url
                
                # Check for meta refresh
                meta_refresh = re.search(
                    r'<meta[^>]*http-equiv="refresh"[^>]*content="[^"]*;\s*url=([^"]+)"', 
                    response.text, 
                    re.IGNORECASE
                )
                if meta_refresh:
                    redirect_url = meta_refresh.group(1).replace('&amp;', '&')
                    if not redirect_url.startswith(('http://', 'https://')):
                        redirect_url = urljoin(current_url, redirect_url)
                    current_url = redirect_url
                    continue
            
            break  # No more redirects
            
        except Exception as e:
            return None
    
    return None

@app.route('/validate', methods=['GET'])
def validate_link():
    share_link = request.args.get('url')
    
    if not share_link:
        return jsonify({'error': 'No URL provided'}), 400
    
    if not re.search(r"https://www\.roblox\.com/share\?code=", share_link):
        return jsonify({'error': 'Invalid share link format'}), 400
    
    final_url = follow_roblox_redirects(share_link)
    
    if final_url:
        return jsonify({
            'valid': True,
            'final_url': final_url,
            'message': 'Private server is valid'
        })
    else:
        return jsonify({
            'valid': False,
            'message': 'Private server is invalid or could not be reached'
        })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
