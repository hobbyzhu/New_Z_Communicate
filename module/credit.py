import time

from flask import session
from sqlalchemy import Table

from common.datebase import dbconnet

dbsession, md, DBase = dbconnet()


class Credit(DBase):
    __table__ = Table('credit', md, autoload=True)

    # 积分表增加积分明细
    def insert_detail(self, type, target, credit):
        now = time.strftime('%Y-%m-%d %H:%M:%S')  # 获取当前系统时间
        # 积分类型     用户ID         多少分
        credit1 = Credit(userid=session.get('userid'), category=type, target=target, credit=credit, createtime=now,
                         updatetime=now)
        dbsession.add(credit1)
        dbsession.commit()
        dbsession.close()

    # 判断用户是否已经购买文章
    def check_payed_article(self, articleid):
        # 检查积分表 用户ID(id直接从session中获得) 和 文章 是 否有记录
        result = dbsession.query(Credit).filter_by(userid=session.get('userid'), target=articleid).all()
        dbsession.close()
        if len(result) > 0:
            return True
        else:
            return False
