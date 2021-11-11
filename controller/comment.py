from flask import Blueprint, request, session, jsonify

from module.article import Article
from module.comment import Comment
from module.credit import Credit
from module.users import Users

comment = Blueprint('comment', __name__)


# 蓝图拦截器
@comment.before_request
def before_comment():
    if session.get('islogin') is None or session.get('islogin') != 'true':
        return '你还没有登录'
    else:
        pass

# 文章评论
@comment.post('/comment')
def article_replay():
    articleid = request.form.get('articleid')  # 前端获取
    content = request.form.get('content')
    ipaddr = request.remote_addr  # 获取用户ip地址

    # 对评论内容进行校验 校验过于简单后期会完善添加非法词汇检查
    if len(content) < 5 or len(content) > 1000:
        return 'content-invalid'

    comment = Comment()
    if not comment.check_limit_per():  # 如果返回False说明没有超过评论限制
        try:
            comment.insrt_comment(articleid, content, ipaddr)
            # 评论成功后增加积分明细
            Credit().insert_detail('添加评论', target=articleid, credit=2)
            # 为用户表增加积分
            Users().update_credit(2)
            # 为文章表 用户评论 + 1
            Article().update_replay_count(articleid)
            return 'add-pass'
        except:
            return 'add-fail'
    else:  # 当用户评论超限制，会取消积分获取，但是不会限制评论
        try:
            comment.insrt_comment(articleid, content, ipaddr)
            return 'replay-pass'
        except:
            return 'replay-fail'


@comment.route('/reply', methods=['POST'])
def reply():
    articleid = request.form.get('articleid')
    commentid = request.form.get('commentid')
    content = request.form.get('content').strip()
    ipaddr = request.remote_addr
    if len(content) < 5 or len(content) > 1000:
        return 'comtent-invalid'

    comment = Comment()

    # 没有超出评论限制才能获得积分，否则只能评论。不要限制评论，让用户水
    if not comment.check_limit_per():
        try:
            # 注意 此处比普通评论增加一条参数， 原始评论的ID，用来区分原始评论
            comment.insert_replay(articleid=articleid, commentid=commentid, content=content, ipaddr=ipaddr)

            # 评论成功后积分表增加积分明细,用户表增加积分，文章表评论数 + 1
            Credit().insert_detail(type='回复评论', target=articleid, credit=2)

            Users().update_credit(2)

            Article().update_replay_count(articleid)
            return 'replay-pass'
        except:
            return 'replay-fail'
    else:
        try:
            # 当用户超过限制后，将无法获得积分，但是不限制回复
            comment.insert_replay(articleid=articleid, commentid=commentid, content=content, ipaddr=ipaddr)
            return 'replay-10-Limit'
        except:
            return 'reply-Limit'



# 测试接口，为了测试Ajax分页
# 由于分页已经完成渲染，此接口仅根据前端的页码请求后台数据
@comment.route('/comment/<int:articleid>-<int:page>')
def comment_page(articleid, page):
    start = (page - 1)*10
    listx =Comment().get_comment_user_list(articleid, start, 10)  # 所有分页数据的获取
    return jsonify(listx)
