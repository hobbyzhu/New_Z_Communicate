import time

from flask import session
from sqlalchemy import Table
from common.datebase import dbconnet
from module.users import Users
from common.unitity import *

dbsession, md, DBase = dbconnet()


class Comment(DBase):
    __table__ = Table('Comment', md, autoload=True)

    # 新增评论 参数->
    def insrt_comment(self, articleid, content, ipaddr):
        now = time.strftime('%Y-%m-%d %H:%M:%S')  # 获取当前系统时间
        comment = Comment(userid=session.get('userid'), articleid=articleid, content=content, ipaddr=ipaddr,
                          createtime=now, updatetime=now)
        dbsession.add(comment)
        dbsession.commit()
        dbsession.close()

    # 根据文章标号查询所有评论 replyid =0 是原始评论
    def find_comment_by_articleid(self, articleid):
        result = dbsession.query(Comment).filter_by(hide=0, replyid=0, articleid=articleid).all()
        return result

    # 根据用户编号和日期查询是否已经超过评论限制
    def check_limit_per(self):
        start = time.strftime('%Y-%m-%d 00:00:00')  # 一天的开始时间
        end = time.strftime('%Y-%m-%d 23:59:59')  # 一天的结束时间
        # 查看所有评论
        result = dbsession.query(Comment).filter(Comment.userid == session.get('userid'),
                                                 Comment.createtime.between(start, end)).all()
        dbsession.close()
        if len(result) > 9:
            return True  # 返回今天不能再获取积分，在功能上限制积分获取，不限制评论
        else:
            return False

    # 查询评论与用户信息，注意评论需要分页 评论表和用户表关联，然后根据条件查找，然后降序排序(最新评论)，再分页
    def find_limit_with_user(self, articleid, start, count):
        result = dbsession.query(Comment, Users).join(Users, Users.userid == Comment.userid) \
            .filter(Comment.articleid == articleid, Comment.hide == 0) \
            .order_by(Comment.commentid.desc()).limit(count).offset(start).all()
        return result

    #  新增加回复，将原始id作为新评论的replayid 字段进行关联   注意 此增加数据是根据用户的原始回复新增加的回复
    def insert_replay(self, articleid, commentid, content, ipaddr):
        now = time.strftime('%Y-%m-%d %H:%M:%S')  # 获取当前系统时间
        comment = Comment(userid=session.get('userid'), articleid=articleid, replyid=commentid, content=content,
                          ipaddr=ipaddr, createtime=now, updatetime=now)
        dbsession.add(comment)
        dbsession.commit()
        dbsession.close()

    # 评论分页功能
    # 查询原始评论与对于的用户信息，带分页参数
    def find_comment_with_user(self, articleid, start, count):
        result = dbsession.query(Comment, Users).join(Users, Users.userid == Comment.userid). \
            filter(Comment.articleid == articleid, Comment.hide == 0, Comment.replyid == 0). \
            order_by(Comment.commentid.desc()).limit(count).offset(start).all()

        return result

    # 查询回复的评论，回复评论不要分页,注意这里通过传入参数确定查询范围
    def find_reply_with_user(self, replyid):
        result = dbsession.query(Comment, Users).join(Users, Users.userid == Comment.userid). \
            filter(Comment.hide == 0, Comment.replyid == replyid).all()
        return result

    # 根据原始评论和回复评论生成一个关联列表    # 这是数据结构重写构造的方法，   ==》十分重要,本功能的核心点
    def get_comment_user_list(self, articleid, start, count):
        result = self.find_comment_with_user(articleid, start, count)
        # result是2个对象的表，通过下面的方法转为json
        comment_list = model_join_list(result)  # 原始评论的连接结果
        for comment in comment_list:
            # 查询原始评论对于的回复评论，并转换为列表保存到comment_list中
            result = self.find_reply_with_user(comment['commentid'])
            # 为comment_list 列表中的原始评论字典对象添加新key--》reply_list
            # 用于储存当前这条评论的所有回复评论，如果没有回复评论则返回为空
            comment['reply_list'] = model_join_list(result)
        return comment_list
