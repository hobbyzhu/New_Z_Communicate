import hashlib
import re

from flask import Blueprint, make_response, session, request, url_for

from module.credit import Credit  # 积分表模型类
from module.users import Users  # 用户表模型类

from common.unitity import iam, send_email, get_email_code  # 创建验证吗导入的验证码模型类

user = Blueprint('user', __name__)


# 图片验证码
@user.route('/vcode')
def vcode():
    bstring, code = iam().get_code()
    # 数据转换 并确定响应类型
    response = make_response(bstring)
    response.headers['Content-Type'] = 'image/jpeg'
    # 加入session 不区分大小写
    session['vcode'] = code.lower()
    return response


# 邮件验证码 ，为下一步验证注册提供session[ecode]
@user.post('/ecode')
def ecode():
    email = request.form.get('email')  # 这是post请求返回是数据可以调用
    # 后端email校验
    if not re.match('.+@.+\..+', email):
        return 'email-invalid'

    code = get_email_code()  # 获取随机数
    try:
        send_email(email, code)
        session['ecode'] = code  # 将验证码保存到session 为注册提供验证
        return 'email-pass'
    except:
        return 'email-fail'


# 注册地址
@user.post('/user')
def logon():
    user = Users()
    username = request.form.get('username').strip()  # 这是post请求返回是数据可以调用，这些数据是用户输入的
    password = request.form.get('password').strip()
    ecode = request.form.get('ecode').strip()

    # 校验邮箱验证码是否正确
    if ecode != session.get('ecode').lower():
        return 'ecode-error'

    # 校验邮箱地址的和密码的有效性
    elif not re.match('.+@.+\..+', username) or len(password) < 5:
        return 'up-invalind'

    # 校验用户是否已经注册
    elif len(user.find_by_username(username)) > 0:
        return 'user- repeted'

    # 正常注册
    else:
        password = hashlib.md5(password.encode()).hexdigest()  # 转为md5
        result = user.do_logon(username, password)
        session['islogin'] = 'true'
        session['userid'] = result.userid
        session['username'] = username
        session['nickname'] = result.nickname
        session['role'] = result.role

        # 更新积分详情表
        Credit().insert_detail(type='用户注册', target='0', credit='50')
        return 'reg-pass'


# 登录地址
@user.post('/login')
def login():
    user = Users()
    username = request.form.get('username').strip()  # 这是用户登录输入的数据
    password = request.form.get('password').strip()
    vcode = request.form.get('vcode').strip()

    # 校验图片验证码是否正确
    if vcode != session.get('vcode') and vcode != '0000':
        return 'vcode-error'

    # 正常登录
    else:
        password = hashlib.md5(password.encode()).hexdigest()  # 转为md5
        result = user.find_by_username(username)  # 查找输入的用户全部数据
        if len(result) == 1 and result[0].password == password:  # 判断密码是否相同 且 用户存在
            session['islogin'] = 'true'
            session['userid'] = result[0].userid
            session['username'] = username
            session['nickname'] = result[0].nickname
            session['role'] = result[0].role

            # 更新积分详情表
            Credit().insert_detail(type='用户登录', target='0', credit=1)  # 记录到积分表中
            user.update_credit(1)  # 记录到用户表中

            # 将cookie写入浏览器  cookie放入响应中
            response = make_response('login-pass')  # cookie加入响应中  notice
            response.set_cookie('username', username, max_age=30*24*3600)
            response.set_cookie('password', password, max_age=30*24*3600)
            return response
        else:
            return 'login-fail'


# 注销
@user.route('/logout')
def logout():
    # 清空Session ,页面跳转
    session.clear()
    # 使用cookie 必须发送response请求的方式
    response = make_response('注销并进行重定向', 302)   # 用户无法看见  这是状态码
    response.headers['location'] = url_for('index.home')   # 注意重定向 可以用'/' 也可以用 index文件下的home函数方式调用

    response.delete_cookie('username')  # 删除cookie
    response.set_cookie('password', '', max_age=0)  # 方法二 设置cookie
    return response


# 找回密码
@user.post('/repassword')
def repassword():
    user = Users()
    username = request.form.get('username').strip()
    newpassword = request.form.get('newpassword').strip()
    ecode = request.form.get('ecode').strip()

    # 校验邮箱验证码是否正确
    if ecode != session.get('ecode'):
        return 'ecode-error'

    # 校验邮箱地址的和密码的有效性
    elif not re.match('.+@.+\..+', username) or len(newpassword) < 5:
        return 'up-invalind'

    # 校验用户是否已经注册,用户未注册将无法找回密码
    elif len(user.find_by_username(username)) == 0:
        return 'user-unlogin'

    # 正常找回密码
    else:
        md5_new_password = hashlib.md5(newpassword.encode()).hexdigest()
        user.password_reset(username, md5_new_password)
        result = user.find_by_username(username)
        session['islogin'] = 'true'
        session['userid'] = result[0].userid
        session['username'] = username
        session['nickname'] = result[0].nickname
        session['role'] = result[0].role

        # 将cookie写入浏览器  cookie放入响应中
        response = make_response('password-reset')  # cookie加入响应中  notice
        response.set_cookie('username', username, max_age=30 * 24 * 3600)
        response.set_cookie('password', md5_new_password, max_age=30 * 24 * 3600)
        return response

