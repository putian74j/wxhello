import os

from flask import Flask
import akshare as ak
import pandas as pd

import common as co


fund_open_fund_info_em_df = ak.fund_open_fund_info_em(symbol="000961", indicator="单位净值走势")
str(fund_open_fund_info_em_df['单位净值'][0])


app = Flask(__name__)

@app.route('/')
def hello_world():
    # return f'欢迎使用微信云托管 哈哈666:  {os.environ.get('MYSQL_USERNAME')}'
    return f'欢迎使用微信云托管 哈哈666:  {str(fund_open_fund_info_em_df['单位净值'][100])}'

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8032)))
    # app.run(debug=True,host='0.0.0.0',port=8032)