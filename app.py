from flask import Flask
from flask import request
from flask import render_template
import pymysql
app = Flask(__name__)

conn = pymysql.connect(host='192.168.2.11',
                       user='hive',
                       password='hive',
                       database='wx_spider')

@app.route('/')
def index():
    cur = conn.cursor()
    sql = 'select DISTINCT(account) from article'
    cur.execute(sql)
    accounts = cur.fetchall()
    print(accounts)
    return render_template('index.html',accounts=accounts)

@app.route('/view',methods=['POST'])
def view():
    account = request.form.get("account")
    cur = conn.cursor()
    sql = 'select account,title,content_url,datetime from article where account=\'{}\''.format(account)
    cur.execute(sql)
    content = cur.fetchall()
    labels = ['账号','文章','时间']

    return render_template('view.html',labels=labels,content=content)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')