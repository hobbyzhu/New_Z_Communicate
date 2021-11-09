from flask import Blueprint, request, session

from module.favourit import Favorite

favorite = Blueprint('favorite', __name__)


# 收藏文章 不需要渲染页面，直接在页面中post请求
@favorite.post('/favorite')
def add_favorite():
    articleid = request.form.get('articleid')
    if session.get('islogin') is None:
        return 'no-login'
    else:
        try:
            Favorite().insert_favorite(articleid)
            return 'favorite-pass'
        except:
            return 'favorite-fail'


# 取消收藏
@favorite.route('/favorite/<int:articleid>', methods=['DELETE'])
def cancel_favorite(articleid):
    try:
        Favorite().cancel_favorite(articleid)
        return 'cancel-pass'
    except:
        return 'cancel-fail'

