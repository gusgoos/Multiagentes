from flask import Flask, send_file

app = Flask(__name__)

@app.route('/get_agent_positions', methods=['GET'])
def get_agent_positions():
    return send_file('agent_positions.json', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=54321)