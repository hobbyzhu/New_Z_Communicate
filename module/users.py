import random
import time

from flask import session
from sqlalchemy import Table

from common.datebase import dbconnet

dbsession, md, DBase = dbconnet()


class Users(DBase):
    __table__ = Table('users', md, autoload=True)

    # 检查用户是否已经注册
    def find_by_username(self, username):
        result = dbsession.query(Users).filter_by(username=username).all()
        return result

    #注册用户
    def do_logon(self, username, password):
        now = time.strftime('%Y-%m-%d %H:%M:%S')  # 获取当前系统时间
        nikcname = username.split('@')[0]  # 将用户输入的邮箱@前部分作为 昵称
        avatar = str(random.randint(1, 10))  # 随机用户的头像
        user = Users(username=username, password=password, role='user', credit=50,
                     nickname=nikcname, avatar=avatar+'.png', createtime=now, updatetime=now)
        dbsession.add(user)
        dbsession.commit()
        return user

    # 修改用户表，积分+为增加 -为减少
    def update_credit(self, credit):
        user = dbsession.query(Users).filter_by(userid=session.get('userid')).one()
        user.credit = int(user.credit)+credit
        dbsession.commit()
        dbsession.close()

    # 根据用户名修改密码
    def password_reset(self, username, newpassword):
        result = dbsession.query(Users).filter_by(username=username).first()
        result.password = newpassword
        dbsession.commit()
        dbsession.close()
