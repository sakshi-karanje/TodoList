from flask import Flask,jsonify,render_template,request,Response
import os.path
from flask_restful import reqparse, abort, Api, Resource,url_for
import sqlite3
import html
import socket
ip=socket.gethostbyname(socket.gethostname())

app = Flask(__name__)

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('t_name')
parser.add_argument('t_status')
parser.add_argument('tid')
parser.add_argument('_method')
parser.add_argument('mail')
parser.add_argument('date')
################################################


@app.route('/')
def home():
    return render_template('loginP.html',ip=ip)


@app.route('/sign',methods=['GET'])
def home_signup():
    return render_template('sign.html',ip=ip,port=po)
#################################################

@app.route('/login' ,methods=['POST'])
def signup():
    args=parser.parse_args()
    gusername=args['username']
    gpassword=args['password']
    mail = args['mail']
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("INSERT INTO login('uname','password','email') VALUES (?,?,?)",(gusername,gpassword,mail))
    conn.commit()

    return render_template('loginp.html',ip=ip)


@app.route('/login',methods=['GET',])
def loginp():

    args = parser.parse_args()
    gusername=args['username']
    gpassword=args['password']
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT * FROM login WHERE uname=? AND password=?",(gusername,gpassword))

    result=c.fetchall()

    if result:
        if gusername=='admin':
            return render_template('admin.html')

        return render_template('user1.html',uname=gusername,ip=ip)
    return "login failed"
############################################################

@app.route('/todo',methods=['POST'])
def insertp():

    args = parser.parse_args()
    _method1 = args['_method']
    if (_method1 == "put"):
        a=edit()
    elif (_method1 == "delete"):
        a=delete()
    elif(_method1 == "post"):
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        user1 = args['username']
        c.execute("select uid from login WHERE uname=(?);",[user1])
        uid1 = c.fetchone()
        tname = args['t_name']
        tstatus = args['t_status']
        date=args['date']

        c.execute("insert into todo('tname','tstatus','uid','tdate') values (?,?,?,?);",(tname,tstatus,uid1[0],date))
        conn.commit()
        c.close()
        return render_template('user1.html',uname=user1)
    else:return "wrong"
    return a
@app.route('/todo',methods=['GET'])
def showp():

    args = parser.parse_args()
    conn=sqlite3.connect('todo.db')
    c=conn.cursor()
    user1 = args['username']
    c.execute("select uid from login  WHERE uname=?;", [user1] )
    uid1 = c.fetchone()

    c.execute("SELECT tid,tname,tstatus FROM todo where uid=?", [uid1[0]])
    items = c.fetchall()
    c.close()

    output = render_template('user1.html',items=items,uname=user1)
    return output


@app.route('/todo',methods=['PUT'])
def edit():
    args = parser.parse_args()
    tid1 = args['tid']
    tstatus1 = args['t_status']
    tname1 = args['t_name']
    user=args['username']
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("select * from todo WHERE tid=?",([tid1]))
    res1 = c.fetchone()
    if res1 != None:
        c.execute("UPDATE todo SET tname=?, tstatus=? WHERE tid=?",(tname1,tstatus1,tid1,))
        conn.commit()
        c.execute("select * from todo WHERE tname=? AND tstatus=? AND tid=?",(tname1,tstatus1,tid1))
        res = c.fetchone()
        #return render_template('user1.html')

        return 'task edited.....<br> Older task: <b>'+str[res1[1]]+'</b> task status: <b>'+str[res1[2]]+'</b><br> new task is: <b>'+str[res[1]]+'</b> task status is: <b>'+str[res[2]]+'</b>'
    return 'wrong input'


@app.route('/todo', methods=['DELETE'])
def delete():
    args = parser.parse_args()
    tid = args['tid']

    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("select * from todo WHERE tid=?",([tid]))
    res1 = c.fetchone()
    if res1 != None:
        c.execute("DELETE FROM todo WHERE tid=?",([tid]))
        conn.commit()
        return "task deleted"
    return "wrong task id"


if __name__ == '__main__':
    app.run(host=ip,debug=True)

