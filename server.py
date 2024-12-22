from flask import Flask, render_template, request, redirect, make_response, send_from_directory
import pymysql
import random
import string
import os

app = Flask(__name__)
conn = pymysql.connect(host = 'localhost', user = 'root', password = '[censored]', database = 'forum', charset = 'utf8', cursorclass = pymysql.cursors.DictCursor)
cur = conn.cursor()
characters = string.ascii_letters + string.digits

@app.route('/', methods=['get'])
def main():
    query = "SELECT * FROM board"
    cur.execute(query)
    results = cur.fetchall()[::-1]
    user = request.cookies.get('user')
    if user:
        login = f"""
      <form action = "/write" method = "get">
        <button>글쓰기</button>
      </form>
      <form action = "/logout" method = "get">
        <button>로그아웃</button>
      </form>
      <a href = "/myprofile">
        <button>내 프로필</button>
        </a>
    """
        return render_template('main.html', results = results, login = login)
    else:
        login = """
      <form action = "/login" method = "get">
        <button>로그인</button>
      </form>
        """
        return render_template('main.html', results = results, login = login)
    
@app.route('/view')
def view1():
    id = request.args.get('id')
    query = "SELECT * FROM board WHERE id = " + str(id) + ";"
    cur.execute(query)
    result = cur.fetchall()
    file = ""
    if(result[0]['secret'] == 'y'):
        return render_template('check.html', id = id)
    else:
        if(result[0]['file'] != ""):
            file = "<a href=/download/" + str(result[0]['file']) + ">파일 다운로드</a><br>"
        return render_template('view.html', result = result, file = file)

@app.route('/view', methods = ['post'])
def view2():
    id = request.form['id']
    password = request.form['password']
    query = "SELECT * FROM board WHERE id = " + str(id) + ";"
    cur.execute(query)
    result = cur.fetchall()
    query = "SELECT * FROM userinformation WHERE user = '" + str(result[0]['user']) + "';"
    cur.execute(query)
    result2 = cur.fetchall()
    file = ""
    if(result[0]['file'] != ""):
        file = "<a href=/download/" + str(result[0]['file']) + ">파일 다운로드</a><br>"
    if(result2[0]['password'] == password):
        return render_template('view.html', result = result, file = file)
    else:
        return redirect('/view?id='+str(id))

@app.route('/write', methods = ['get'])
def write1():
    user = request.cookies.get('user')
    if user:
        return render_template('write.html', user = user)
    else:
        return redirect('/login')

@app.route('/write', methods = ['post'])
def write2():
    user = request.cookies.get('user')
    title = request.form['title']
    content = request.form['content']
    file = request.files['file']
    route = ""
    if(file.filename != ''):
        route = ''.join(random.choices(characters, k=10)) + os.path.splitext(file.filename)[1]
        file.save("uploadfile/" + str(route))
    if(request.form.get('secret') == None):
        secret = 'n'
    else:
        secret = 'y'
    query = "INSERT INTO board(user, title, content, secret, file) VALUES('" + str(user) + "','" + str(title) + "','" + str(content) + "','" + str(secret) + "','" + str(route) + "');"
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
    query = "SELECT * FROM board WHERE id = " + str(id) + ";"
    cur.execute(query)
    user = cur.fetchall()[0]['user']
    query = "SELECT * FROM userinformation WHERE user = '" + str(user) + "';"
    cur.execute(query)
    if(password == cur.fetchall()[0]['password']):
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
    query = "SELECT * FROM userinformation WHERE user = '" + str(user) + "';"
    cur.execute(query)
    result = cur.fetchall()
    if(result[0]['password'] == password):
        query = "UPDATE board SET user ='" + str(user) + "', title ='" + str(title) + "', content ='" + str(content) + "' WHERE id = " + str(id) + ";" 
        cur.execute(query)
        conn.commit()
        return redirect('/')
    else:
        return redirect('/edit?id='+str(id))
    
@app.route('/login', methods = ['get'])
def login1():
    return render_template('login.html')

@app.route('/login', methods = ['post'])
def login2():
    user = request.form['user']
    password = request.form['password']
    try:
        query = "SELECT * FROM userinformation WHERE user = '" + str(user) + "';"
        cur.execute(query)
        result = cur.fetchall()
        if(result[0]['password'] == password):
            resp = make_response(redirect('/'))
            resp.set_cookie('user', result[0]['user'], max_age=60*60*24)
            return resp
        else:
            return render_template('login.html', error = "비밀번호가 틀렸습니다.")
    except:
        return render_template('login.html', error = "존재하지 않는 사용자입니다.")

@app.route('/regist')
def regist1():
    return render_template('regist.html')

@app.route('/regist', methods = ['post'])
def regist2():
    user = request.form['user']
    password = request.form['password']
    school = request.form['school']
    name = request.form['name']
    password2 = request.form['password2']
    query = "SELECT EXISTS(SELECT 1 FROM userinformation WHERE user = '" + str(user) + "') AS result;"
    cur.execute(query)
    result = int(cur.fetchall()[0]['result'])
    if(result == 0):
        query = "INSERT INTO userinformation(user, password, school, name, password2) VALUES('" + str(user) + "','" + str(password) + "','" + str(school) + "','" + str(name) + "','" + str(password2) + "');" 
        cur.execute(query)
        conn.commit()
        return redirect('/')
    else:
        return render_template('regist.html', error = "이미 있는 id 입니다.")

@app.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.delete_cookie('user')
    return resp

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('uploadfile', filename, as_attachment=True)

@app.route('/searchidpd', methods = ['get'])
def searchidpd1():
    return render_template('searchidpd.html')

@app.route('/searchidpd', methods = ['post'])
def searchidpd2():
    name = request.form.get('name')
    user = request.form.get('user')
    password2 = request.form.get('password2')
    result = ""
    if(name != None):
        query = "SELECT * from userinformation WHERE name = '" + str(name) + "';"
        cur.execute(query)
        result = cur.fetchall()
        if(len(result) == 0):
            return render_template('searchidpd.html', result = "id를 찾을 수 없습니다.")
        else:
            return render_template('searchidpd.html', result = "id는 " + result[0]['user'] + "입니다.")
    elif(user != None and password2 != None):
        query = "SELECT * from userinformation WHERE user = '" + str(user) + "';"
        cur.execute(query)
        result = cur.fetchall()
        if(len(result) != 0):
            if(password2 == result[0]['password2']):
                return render_template('searchidpd.html', result = "비밀번호는 " + result[0]['password'] + "입니다.")
            else: 
                return render_template('searchidpd.html', result = "2차 비밀번호가 옳지 않습니다.")
        else:
            return render_template('searchidpd.html', result = "존재하지 않는 id입니다.")
    else:
        return render_template('searchidpd.html', result = "값을 입력해주세요")

@app.route('/profile')
def profile():
    user = request.args.get('user')
    usercookie = request.cookies.get('user')
    if (user == usercookie):   
        return redirect('/myprofile')
    else:
        query = "SELECT * from userinformation WHERE user = '" + str(user) + "';"
        cur.execute(query)
        result = cur.fetchall()
        if(result[0]['profile'] != None):
            filename = result[0]['profile']
            return render_template('profile.html', result = result, filename = filename)
        else:
            filename = "basic.jpg"
            return render_template('profile.html', result = result, filename = filename)

@app.route('/myprofile')
def myprofile():
    user = request.cookies.get('user')
    query = "SELECT * from userinformation WHERE user = '" + str(user) + "';"
    cur.execute(query)
    result = cur.fetchall()
    if(result[0]['profile'] != None):
        filename = result[0]['profile']
        return render_template('myprofile.html', result = result, filename = filename)
    else:
        filename = "basic.jpg"
        return render_template('myprofile.html', result = result, filename = filename)

@app.route('/editprofile')
def editprofile1():
    user = request.cookies.get('user')
    query = "SELECT * from userinformation WHERE user = '" + str(user) + "';"
    cur.execute(query)
    result = cur.fetchall()
    return render_template('editprofile.html', result = result)

@app.route('/editprofile', methods = ['post'])
def editprofile2():
    user = request.cookies.get('user')
    school = request.form['school']
    name = request.form['name']
    file = request.files['file']
    if(file.filename != ''):
        route = ''.join(random.choices(characters, k=10)) + os.path.splitext(file.filename)[1]
        file.save("static/profile/" + str(route))
        query = "UPDATE userinformation SET profile ='" + str(route) + "', school ='" + str(school) + "', name ='" + str(name) + "' WHERE user = '" + str(user) + "';"
        cur.execute(query)
        conn.commit()
    else:
        query = "UPDATE userinformation SET school ='" + str(school) + "', name ='" + str(name) + "' WHERE user = '" + str(user) + "';"
        cur.execute(query)
        conn.commit()
    return redirect('/myprofile')


if __name__ == '__main__':
    app.run(debug="true")
