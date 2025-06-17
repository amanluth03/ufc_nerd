import json
from flask import Flask, jsonify
import os

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/champions_records.json')

@app.route('/api/champions/records', methods=['GET'])
def get_champion_records():
    with open(DATA_FILE) as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get('API_PORT', 5000))
    app.run(host='0.0.0.0', port=port)
