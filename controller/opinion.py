from flask import Blueprint, session, request

from module.comment import Comment
from module.opinion import Opinion

opinion = Blueprint('opinion', __name__)

# 点赞接口
@opinion.post('/opinion')
def Publish_opinions():
    commentid = request.form.get('commentid')
    if session.get('islogin') is None or session.get('islogin') != 'true':
        userid = 0
    else:
        userid = session.get('userid')
    category = request.form.get('category')
    ipaddr = request.remote_addr

    opinion = Opinion()
    try:
        if opinion.check_opinion_by_ip(commentid=commentid, ipaddr=ipaddr) is False:  # 判断是否点赞否就继续
            opinion.insert_opinion(userid=userid, commentid=commentid, category=category, ipaddr=ipaddr)  # 点赞表详细数据
            # 0是反对，1是赞成 ，为评论表加入数据
            if int(category) == 0:
                Comment().Opposition(commentid)
            elif int(category) == 1:
                Comment().Publish(commentid)
            return 'opinion-pass'
        else:
            return 'opinion-fail'
    except:
        return 'system-opinion-fail'


