import os
import uuid
import psycopg2
import psycopg2.extras
from flask import Flask, session
from flask.ext.socketio import SocketIO, emit, request

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secrbkkjbkhbkhbet!'
app.debug = True
socketio = SocketIO(app)

messages = [{'text':'test', 'name':'testName'}]
users = {}


def db_connect():
    connectionString = 'dbname=chat user=postgres password=gohan host=localhost'
    try:
        return psycopg2.connect(connectionString)
    except:
        print("Can't connect to database")
        
        
def updateRoster():
    names = []
    for user_id in  users:
        #print users[user_id]['username']
        if len(users[user_id]['username'])==0:
            names.append('Anonymous')
        else:
            names.append(users[user_id]['username'])
    #print 'broadcasting names'
    emit('roster', names, broadcast=True)
    

@socketio.on('connect', namespace='/chat')
def test_connect():
    session['uuid']=uuid.uuid1()
    session['username']='starter name'
    print 'connected'
    
    users[session['uuid']]={'username':'New User'}
    updateRoster()
    
    conn = db_connect()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = "select users.username, message from messages join users on users.id = messages.username"
    cur.execute(query)
    results = cur.fetchall()
    

    for result in results:
        
        print (result)
        result = {'name': result['username'], 'text':result['message']}
        emit('message', result)

@socketio.on('message', namespace='/chat')
def new_message(message):
    #tmp = {'text':message, 'name':'testName'}
    
    tmp = {'text':message, 'name':users[session['uuid']]['username']}
    messages.append(tmp)
    #query = "insert into messages (username, message) values ('
    conn = db_connect()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""INSERT INTO messages VALUES (default,%s, %s);""", 
    (session['id'], message))
    conn.commit()
    
    emit('message', tmp, broadcast=True)
    
    
@socketio.on('search', namespace='/chat')
def search(search):
    db =db_connect()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = "select users.username, message from messages join users on users.id = messages.username where message like %s"
    cur.execute(query,(search,))
    results = cur.fetchall()
    
    for result in results:
        result = {'name': result['username'], 'textSearch':result['message']}
        emit('search', result, broadcast=True)
    
@socketio.on('identify', namespace='/chat')
def on_identify(message):
    #print 'identify' + message
    users[session['uuid']]={'username':message}
    updateRoster()


@socketio.on('login', namespace='/chat')
def on_login(data):
    #print 'login '  + pw
    db = db_connect()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #print "HI"
    username = data['username']
    password = data['password']
    #zipcode = request.form['zipcode']
    query = "select * from users where username = %s and password = crypt(%s,password)"
    cur.execute(query, (username, password))
    result = cur.fetchone()
    if result:
        users[session['uuid']]={'username':data['username']}
        session['username'] =data['username']
        session['id'] = result['id']
        updateRoster()


    
@socketio.on('disconnect', namespace='/chat')
def on_disconnect():
    print 'disconnect'
    if session['uuid'] in users:
        del users[session['uuid']]
        updateRoster()

@app.route('/')
def hello_world():
    print 'in hello world'
    return app.send_static_file('index.html')
    return 'Hello World!'

@app.route('/js/<path:path>')
def static_proxy_js(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('js', path))
    
@app.route('/css/<path:path>')
def static_proxy_css(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('css', path))
    
@app.route('/img/<path:path>')
def static_proxy_img(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('img', path))
    
if __name__ == '__main__':
    print "A"

    socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))
     