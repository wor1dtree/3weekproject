from flask import Flask, render_template, request, redirect
import pymysql

app = Flask(__name__)
conn = pymysql.connect(host = 'localhost', user = 'root', password = 'gjt051219@', database = 'forum', charset = 'utf8', cursorclass = pymysql.cursors.DictCursor)
cur = conn.cursor()

@app.route('/', methods=['get'])
def main():
    query = "SELECT * FROM board"
    cur.execute(query)
    results = cur.fetchall()[::-1]
    return render_template('main.html', results = results)
    
@app.route('/view')
def view():
    id = request.args.get('id')
    query = "SELECT * FROM board WHERE id = " + str(id) + ";"
    cur.execute(query)
    result = cur.fetchall()
    return render_template('view.html', result = result)

@app.route('/write', methods = ['get'])
def write1():
    return render_template('write.html')

@app.route('/write', methods = ['post'])
def write2():
    user = request.form['user']
    title = request.form['title']
    content = request.form['content']
    password = request.form['password']
    query = "INSERT INTO board(user, title, content, password) VALUES('" + str(user) + "','" + str(title) + "','" + str(content) + "','" + str(password) + "');"
    cur.execute(query)
    conn.commit()
    return redirect('/')

@app.route('/search')
def search():
    mod = request.args.get('mod')
    target = request.args.get('search')
    if(mod == "title"):
        query = "SELECT * FROM board WHERE title LIKE '%" + str(target) + "%';"
        cur.execute(query)
        results = cur.fetchall()[::-1]
        return render_template('main.html', results = results)
    elif(mod == "content"):
        query = "SELECT * FROM board WHERE content LIKE '%" + str(target) + "%';"
        cur.execute(query)
        results = cur.fetchall()[::-1]
        return render_template('main.html', results = results)
    else:
        query = "SELECT * FROM board WHERE title LIKE '%" + str(target) + "%'" + " or content LIKE '%" + str(target) + "%';"
        cur.execute(query)
        results = cur.fetchall()[::-1]
        return render_template('main.html', results = results)

@app.route('/delete')
def delete():
    id = request.args.get('id')
    password = request.args.get('password')
    query = "SELECT password FROM board WHERE id = " + str(id) + ";"
    cur.execute(query)
    result = cur.fetchall()
    datapassword = result[0]['password']
    if(password == datapassword):
        query = "DELETE FROM board WHERE id = " + str(id) + ";"
        cur.execute(query)
        conn.commit()
        return redirect('/')
    else:
        return redirect('/view?id='+str(id))
    
@app.route('/edit', methods = ['get'])
def edit1():
    id = request.args.get('id')
    query = "SELECT * FROM board WHERE id = " + str(id) + ";"
    cur.execute(query)
    result = cur.fetchall()
    return render_template('edit.html', result = result)

@app.route('/edit', methods = ['post'])
def edit2():
    id = request.form['id']
    user = request.form['user']
    title = request.form['title']
    content = request.form['content']
    password = request.form['password']
    query = "SELECT * FROM board WHERE id = " + str(id) + ";"
    cur.execute(query)
    result = cur.fetchall()
    datapassword = result[0]['password']
    if(datapassword == password):
        query = "UPDATE board SET user ='" + str(user) + "', title ='" + str(title) + "', content ='" + str(content) + "' WHERE id = " + str(id) + ";" 
        cur.execute(query)
        conn.commit()
        return redirect('/')
    else:
        return redirect('/edit?id='+str(id))

if __name__ == '__main__':
    app.run()
