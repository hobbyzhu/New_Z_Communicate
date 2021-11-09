import os
from flask import Flask, request, redirect, url_for, session, make_response

# python 3.0支持
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__, static_url_path='/', template_folder='template', static_folder='resource')

app.config['SECRET_KEY'] = os.urandom(24)  # 生成随机数，用于产生Session ID

# 设置这flask中链接SQLachemy
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:901219@localhost:3306/woniunote?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 实列化对象
db = SQLAlchemy(app)


# 错误拦截
@app.errorhandler(404)
def returnerror(e):
    return render_template('error-404.html')


# cookie的全局拦截器，用来处理cookie的读取
@app.before_request
def before():
    url = request.path
    pass_list = ['/user', '/login', 'logout', 'repassword']   # 取消需要拦截器工作的path
    if url in pass_list or url.endswith('.js') or url.endswith('.jpg'):  # 静态页面需要放行的资源
        pass
    # 增加全局拦截器，进行cookie判断 没有 session的登录状态就进行判断
    elif session.get('islogin') is None:
        username = request.cookies.get('username')  # 读取cookie中的值
        password = request.cookies.get('password')
        if username != None and password != None:  # 如果cookie值不为空，就进行判断，为空就是过期了
            user = Users()
            result = user.find_by_username(username)  # 查找输入的用户全部数据
            if len(result) == 1 and result[0].password == password:  # 判断密码是否相同 且 用户存在
                session['islogin'] = 'true'
                session['userid'] = result[0].userid
                session['username'] = username
                session['nickname'] = result[0].nickname
                session['role'] = result[0].role


# 定义类型 用来供前端模板页面调用
@app.context_processor
def gettype():
    type = {
        '1': '击杀视频',
        '2': '宣传视频',
        '3': '物品出售',
        '4': '物品购买',
        '5': '击杀展示',
        '6': '建议'
    }
    return dict(article_type=type)


# 自定义过滤器来重构truncate 原生过滤器
def mytruncate(s, length, end='.'):
    count = 0
    new = ''
    for i in s:
        new = new + i
        if ord(i) < 128:
            count += 1
        else:
            count += 2
        if count > length:
            break
    return new + end


# 注册mytruncate过滤器
app.jinja_env.filters.update(mytruncate=mytruncate)

if __name__ == '__main__':
    from controller.index import *
    app.register_blueprint(index)

    from controller.user import *
    app.register_blueprint(user)

    from controller.article import *
    app.register_blueprint(article)

    from controller.favourite import *
    app.register_blueprint(favorite)

    from controller.comment import *
    app.register_blueprint(comment)
    app.run(debug=True)
