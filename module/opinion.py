import time


from sqlalchemy import Table
from common.datebase import dbconnet

dbsession, md, DBase = dbconnet()


class Opinion(DBase):
    __table__ = Table('Opinion', md, autoload=True)

    # 插入一条点赞,控制器判断用户状态，不是登录用户userid=0, category类型0反对,1赞同也是控制器解决
    def insert_opinion(self, userid, commentid, category, ipaddr):
        now = time.strftime('%Y-%m-%d %H:%M:%S')  # 获取当前系统时间
        opinion = Opinion(userid=userid, commentid=commentid, category=category, ipaddr=ipaddr,
                          createtime=now, updatetime=now)
        dbsession.add(opinion)
        dbsession.commit()
        dbsession.close()

    # 判断用户是否重复点赞 登录用户
    def check_opinion_by_ip(self, commentid, ipaddr):
        result = dbsession.query(Opinion).filter(Opinion.commentid == commentid,
                                                 Opinion.ipaddr == ipaddr).all()
        dbsession.close()
        if len(result) > 0:
            return True
        else:
            return False




