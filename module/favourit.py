import time

from flask import session
from sqlalchemy import Table
from common.datebase import dbconnet

dbsession, md, DBase = dbconnet()


class Favorite(DBase):
    __table__ = Table('favorite', md, autoload=True)

    # 插入收藏表 增加一条数据
    def insert_favorite(self, articleid):
        # 1.查询是否被收藏
        row = dbsession.query(Favorite).filter_by(articleid=articleid, userid=session.get('userid')).first()
        # 判断是否存在
        # 当有数据 0表示已经收藏
        if row is not None:
            row.canceled = 0
        else:
            # 没有数据
            now = time.strftime('%Y-%m-%d %H:%M:%S')  # 获取当前系统时间
            favorite = Favorite(articleid=articleid, userid=session.get('userid'), canceled=0, createtime=now,
                                updatetime=now)
            dbsession.add(favorite)
        dbsession.commit()
        dbsession.close()

    # 取消收藏 只需要将开关打开
    def cancel_favorite(self, articleid):
        row = dbsession.query(Favorite).filter_by(articleid=articleid, userid=session.get('userid')).first()
        row.canceled = 1
        dbsession.commit()
        dbsession.close()

    # 判断是否已经被收藏
    def check_favorite(self, articleid):
        row = dbsession.query(Favorite).filter_by(articleid=articleid, userid=session.get('userid')).first()
        dbsession.close()
        if row is None:
            return False
        elif row.canceled == 1:
            return False
        else:
            return True
