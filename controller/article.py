import math

from flask import Blueprint, abort, render_template, request

from module.article import Article
from module.comment import Comment
from module.credit import Credit
from module.favourit import Favorite
from module.users import Users

article = Blueprint('article', __name__)


@article.route('/article/<int:articleid>')
def red(articleid):
    try:
        # (Article, 'nickname') ==>格式
        result = Article().find_by_id(articleid)
        if result is None:
            abort(404)
    except:
        abort(500)

    # 将元组转化为字典，将nickname也加进去
    d = {}
    for k, v in result[0].__dict__.items():
        if k.startswith('_sa_instance_state') == False:
            d[k] = v
    d['nickname'] = result.nickname

    # 如果已经购买过文章 则直接全部渲染，不要显示一半 前端接口重复购买限制
    payed = Credit().check_payed_article(articleid)

    position = 0  # 解决已购买 就没有参数传递的错误
    if payed == False and d['credit'] > 0:  # 文章未购买且需要积分
        content = d['content']
        # 取一半文章 并加入字典中文章只有一半
        temp = content[0:len(content) // 2]
        # 由于文章中有HTML标记会影响文章布局，需要在中心点往前查找</p>标签 并留下</p>标签 -rindex是
        position = temp.rindex('</p>') + 4
        d['content'] = temp[0:position]

    Article().update_read_count(articleid)  # 阅读次数 + 1

    # 增加是否收藏开关  判断当前文章收藏状态
    is_favourite = Favorite().check_favorite(articleid)

    # 获取当前文章的上一篇和下一篇
    perv_next = Article().find_prev_next_by_id(articleid)

    # 显示当前文章的评论
    # comment_user = Comment().find_limit_with_user(articleid=articleid, start=0, count=50) 已构造就是下面的一条
    # 文章评论的回复 注意带分页参数 默认只显示10条原始评论，剩余评论通过前端页面加载
    comment_list = Comment().get_comment_user_list(articleid, 0, 10)

    # 获取每一篇文章的评论总数，为评论做分页，前端分页
    count = Comment().gen_count_by_article(articleid)
    total = math.ceil(count/10)

    #  这是侧边栏第三加载方式 后端渲染 要放入所有端口中
    article = Article()
    last, most, recommended = article.find_last_readcount_recommended()
    return render_template('article-user.html', recommonded=recommended, article=d, position=position, payed=payed,
                           is_favourite=is_favourite, perv_next=perv_next, comment_list=comment_list, total=total)


# 通过post请求将剩余部分渲染出来
@article.post('/readall')
def readall():
    position = int(request.form.get('position'))  # 上面的接口将剩余位置返回前端，在这又被前端返回给后端
    articleid = request.form.get('articleid')
    article = Article()
    result = article.find_by_id(articleid)  # 重写拉取文章
    content = result[0].content[position:]  # 获取剩余部分

    # 如果积分已经消耗，则不再扣除, 防止后端接口重复请求限制
    payed = Credit().check_payed_article(articleid)
    if not payed:
        # 积分消耗  积分表
        Credit().insert_detail(type='文章阅读', target=articleid, credit=-1 * result[0].credit)
        # 用户表 剩余积分扣除
        Users().update_credit(credit=-1 * result[0].credit)

    return content
