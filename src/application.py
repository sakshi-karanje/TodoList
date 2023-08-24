from flask import Flask,render_template
from flask_restful import reqparse
import sqlite3
from flaskrun import flaskrun
import socket
ip=socket.gethostbyname(socket.gethostname())
#ip="127.0.0.1"
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
    return render_template('sign.html',ip=ip)
#################################################

@app.route('/login' ,methods=['POST'])
def signup():
    args = parser.parse_args()
    gusername = args['username']
    gpassword = args['password']
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
            c.execute("SELECT * FROM login")
            admusr=c.fetchall()
            c.execute("select tid,tname,tstatus,uname,tdate from login,todo where login.uid=todo.uid;")
            admtask=c.fetchall()
            return render_template('admin3.html',admtask=admtask,admusr=admusr,ip=ip)
        c.execute("select uid from login  WHERE uname=?;", [gusername])
        uid1 = c.fetchone()

        c.execute("SELECT tid,tname,tstatus,tdate FROM todo where uid=?", [uid1[0]])
        items = c.fetchall()
        return render_template('user1.html',uname=gusername,ip=ip,items=items)
    return "login failed"
############################################################


@app.route('/todo',methods=['POST'])
def insertp():

    args = parser.parse_args()
    _method1 = args['_method']
    if _method1 == "put":
        a = edit()
    elif _method1 == "delete":
        a = delete()
    elif _method1 == "post":
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
        c.execute("select * FROM todo WHERE tname=?",([tname]))
        res = c.fetchone()

        c.execute('SELECT tid,tname,tstatus,tdate FROM todo where uid=?', [uid1[0]])
        items = c.fetchall()
        c.close()
        return render_template('user1.html',items=items, uname=user1, ip=ip)

        ##return 'task created... tid is: '+str(res[0])+' task name is: '+res[1]+' task due date is: '+res[4]
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

    c.execute("SELECT tid,tname,tstatus,tdate FROM todo where uid=?", [uid1[0]])
    items = c.fetchall()
    c.close()

    output = render_template('user1.html',items=items,uname=user1,ip=ip)
    return output


@app.route('/todo',methods=['PUT'])
def edit():
    args = parser.parse_args()
    tid1 = args['tid']
    tstatus1 = args['t_status']
    tname1 = args['t_name']
    user=args['username']
    date=args['date']
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("select * from todo WHERE tid=?",([tid1]))
    res1 = c.fetchone()
    if res1 != None:
        c.execute("UPDATE todo SET tname=?, tstatus=? WHERE tid=?",(tname1,tstatus1,tid1,))
        conn.commit()
        c.execute("select * from todo WHERE tname=? AND tstatus=? AND tid=? AND tdate=?",(tname1,tstatus1,tid1,date))
        res = c.fetchone()
        #return render_template('user1.html')

        c.execute("select uid from login  WHERE uname=?;", [user])
        uid1 = c.fetchone()
        c.execute("SELECT tid,tname,tstatus,tdate FROM todo where uid=?", [uid1[0]])
        items = c.fetchall()
        c.close()
        return render_template('user1.html',items=items, uname=user, ip=ip)
        #return 'task edited.....<br> Older task: <b>'+res1[1]+'</b> task status: <b>'+str(res1[2])+'</b><br> new task is: <b>'+res[1]+'</b> task status is: <b>'+str(res[2])+'</b>'
    return 'wrong input'


@app.route('/todo', methods=['DELETE'])
def delete():
    args = parser.parse_args()
    tid = args['tid']
    user=args['username']

    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("select * from todo WHERE tid=?",([tid]))
    res1 = c.fetchone()
    if res1 != None:
        c.execute("DELETE FROM todo WHERE tid=?",([tid]))
        conn.commit()

        c.execute("select uid from login  WHERE uname=?;", [user])
        uid1 = c.fetchone()
        c.execute("SELECT tid,tname,tstatus,tdate FROM todo where uid=?", [uid1[0]])
        items = c.fetchall()
        c.close()
        return render_template('user1.html',items=items, uname=user, ip=ip)
    return "wrong task id"

###########################################################################################################################
@app.route('/overdue',methods=['get'])
def due_date():

    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT DATE ('now')")
    a=c.fetchall()
    c.execute("select tid,tname,tstatus,uname,tdate from login,todo where login.uid=todo.uid AND tdate<? AND tstatus NOT IN ('completed');",a[0])
    duetask=c.fetchall()
    forwho='overdue tasks'
    return render_template("make_table.html",items=duetask,ip=ip, forwho=forwho)


@app.route('/running')
def running():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT DATE ('now')")
    a=c.fetchall()
    c.execute("select tid,tname,tstatus,uname,tdate from login,todo where login.uid=todo.uid  AND tstatus='running';")
    runtask=c.fetchall()
    forwho = 'running tasks'
    return render_template("make_table.html",items=runtask,ip=ip, forwho=forwho)


@app.route('/completed')
def completed():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT DATE ('now')")
    a = c.fetchall()
    c.execute("select tid,tname,tstatus,uname,tdate from login,todo where login.uid=todo.uid AND tstatus='completed';")
    completed_task = c.fetchall()
    forwho = 'completed tasks'
    return render_template("make_table.html", items=completed_task, ip=ip, forwho=forwho)

##########################################################################################################################################


@app.route('/admintask')
def admtask():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT tid,tname,tstatus,tdate,uname FROM todo,login WHERE todo.uid=login.uid")
    items = c.fetchall()

    c.execute("SELECT DISTINCT uname FROM login WHERE uname NOT in ('admin')")
    user=c.fetchall()

    c.close()
    return render_template('admintask.html',ip=ip,items=items,user=user)


##########################################################################################################################


@app.route('/admin',methods=['POST'])
def admininsert():

    args = parser.parse_args()
    _method1 = args['_method']
    if (_method1 == "put"):
        a=adminedit()
    elif (_method1 == "delete"):
        a=admindelete()
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
        c.execute("select * FROM todo WHERE tname=?",([tname]))
        res=c.fetchone()

        c.execute("SELECT tid,tname,tstatus,tdate,uname FROM todo,login WHERE todo.uid=login.uid")
        items = c.fetchall()
        c.execute("SELECT DISTINCT uname FROM login WHERE uname NOT in ('admin')")
        user = c.fetchall()
        c.close()
        return render_template('admintask.html',items=items, uname=user1, ip=ip,user=user)
        #return 'task created... tid is: '+str(res[0])+' task name is: '+res[1]+' task due date is: '+res[4]
    else:return "wrong"
    return a


@app.route('/admin',methods=['GET'])
def adminshow():

    args = parser.parse_args()
    conn=sqlite3.connect('todo.db')
    c=conn.cursor()
    user1 = args['username']
    c.execute("select uid from login  WHERE uname=?;", [user1] )
    uid1 = c.fetchone()

    c.execute("SELECT tid,tname,tstatus,tdate,uname FROM todo,login WHERE todo.uid=login.uid")
    items = c.fetchall()
    c.execute("SELECT DISTINCT uname FROM todo,login WHERE todo.uid=login.uid")
    user = c.fetchall()
    c.close()

    output = render_template('admintask.html',items=items,user=user,ip=ip)
    return output


@app.route('/admin',methods=['PUT'])
def adminedit():
    args = parser.parse_args()
    tid1 = args['tid']
    tstatus1 = args['t_status']
    tname1 = args['t_name']
    user=args['username']
    date=args['date']
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("select * from todo WHERE tid=?",([tid1]))
    res1 = c.fetchone()
    c.execute("SELECT uid from login WHERE uname=?",[user])
    uid=c.fetchone()
    if res1 != None:
        c.execute("UPDATE todo SET tname=?, tstatus=?,uid=? WHERE tid=?",(tname1,tstatus1,uid[0],tid1,))
        conn.commit()
        c.execute("select * from todo WHERE tname=? AND tstatus=? AND tid=? AND tdate=?",(tname1,tstatus1,tid1,date))
        res = c.fetchone()#not necessary
        #return render_template('user1.html')


        c.execute("SELECT tid,tname,tstatus,tdate,uname FROM todo,login WHERE todo.uid=login.uid")
        items = c.fetchall()
        c.execute("SELECT DISTINCT uname FROM login WHERE uname NOT in ('admin')")
        user = c.fetchall()
        c.close()
        return render_template('admintask.html',items=items,user=user, uname=user, ip=ip)
        #return 'task edited.....<br> Older task: <b>'+res1[1]+'</b> task status: <b>'+str(res1[2])+'</b><br> new task is: <b>'+res[1]+'</b> task status is: <b>'+str(res[2])+'</b>'
    return 'wrong input'


@app.route('/admin', methods=['DELETE'])
def admindelete():
    args = parser.parse_args()
    tid = args['tid']
    user=args['username']

    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("select * from todo WHERE tid=?",([tid]))
    res1 = c.fetchone()
    if res1 != None:
        c.execute("DELETE FROM todo WHERE tid=?",([tid]))
        conn.commit()

        c.execute("select uid from login  WHERE uname=?;", [user])
        uid1 = c.fetchone()
        c.execute("SELECT tid,tname,tstatus,tdate,uname FROM todo,login WHERE todo.uid=login.uid")
        items = c.fetchall()
        c.execute("SELECT DISTINCT uname FROM login WHERE uname NOT in ('admin')")
        user = c.fetchall()
        c.close()
        return render_template('admintask.html',items=items, user=user, ip=ip)
    return "wrong task id"
###########################################################################################################################
if __name__ == '__main__':
    app.run(host=ip,debug=True)
	#flaskrun(app)

