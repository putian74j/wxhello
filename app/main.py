import os

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '欢迎使用微信云托管 哈哈4'

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8032)))