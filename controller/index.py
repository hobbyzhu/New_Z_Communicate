import math
from flask import Blueprint, render_template, abort, jsonify, session, request
from module.users import Users

from module.article import Article

index = Blueprint('index', __name__)


@index.route('/')
def home():
    article = Article()
    result = article.find_limit_with_user(0, 10)
    if article.get_total_count() % 10 == 0:
        total = int(article.get_total_count() / 10)
    else:
        total = int(article.get_total_count() // 10 + 1)
    last, most, recommended = article.find_last_readcount_recommended()
    return render_template('center.html', result=result, total=total, page=1, last=last, most=most,
                           recommonded=recommended)


@index.route('/page/<int:page>')
def pagenate(page):
    start = (page - 1) * 10
    article = Article()
    result = article.find_limit_with_user(start, 10)
    if article.get_total_count() % 10 == 0:
        total = int(article.get_total_count() / 10)
    else:
        total = int(article.get_total_count() // 10 + 1)
    last, most, recommended = article.find_last_readcount_recommended()
    return render_template('center.html', result=result, total=total, page=page, recommonded=recommended)


@index.route('/type/<int:type>-<int:page>')
def page_type(type, page):
    article = Article()
    start = (page - 1) * 10
    result = article.find_by_type(type=type, start=start, count=10)
    total = math.ceil(article.get_artilce_type_count(type) / 10)
    last, most, recommended = article.find_last_readcount_recommended()
    return render_template('type.html', result=result, total=total, page=page, type=type, recommonded=recommended)


@index.route('/search/<int:page>-<keyword>')
def search(page, keyword):
    keyword = keyword.strip()
    # 接口限制
    if keyword is None or keyword == '' or '%' in keyword or len(keyword) > 10:
        abort(404)
    article = Article()
    start = (page - 1) * 10
    result = article.find_by_handline(keyword, start, 10)
    total = math.ceil(article.get_count_by_headline(keyword) / 10)
    last, most, recommended = article.find_last_readcount_recommended()
    return render_template('search.html', result=result, total=total, page=page, keyword=keyword, recommonded=recommended)


def model_list(result):  # list 转 json
    lt = []
    for low in result:
        d = [low[0], low[1]]
        lt.append(d)
    return lt


# 接口参数给前端调用 jQuery
@index.route('/recommend')  # 不知道为什么我的数据不行 ，只能自己转json
def recommend():
    article = Article()
    last, most, recommended = article.find_last_readcount_recommended()
    last = model_list(last)
    most = model_list(most)
    recommended = model_list(recommended)
    return jsonify(last, most, recommended)
