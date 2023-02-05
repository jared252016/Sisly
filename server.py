from flask import Flask
from flask import request
import subprocess
app = Flask(__name__)
@app.route('/sisly_add', methods=['POST'])
def exec_sisly():
    subprocess.Popen(['./sisly.py', request.data])
    return "Success"
if __name__ == '__main__':
    app.run(host='192.168.2.3', port=9105)