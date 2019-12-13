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
    sql = 'select id,account,title,content_url,datetime,already from article where account=\'{}\''.format(account)
    cur.execute(sql)
    content = cur.fetchall()
    labels = ['','ID','公众号','文章','时间','是否已读']

    return render_template('view.html',labels=labels,content=content)

@app.route('/update',methods=['POST'])
def update():
    readList = request.values.getlist("Read")
    readList = ','.join(readList)
    cur = conn.cursor()
    sql = 'update article set already=1 where id in ({})'.format(readList)
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)
    return render_template('view.html')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')