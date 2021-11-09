from sqlalchemy import Table, func

from common.datebase import dbconnet
from module.users import Users

dbsession, md, DBase = dbconnet()


class Article(DBase):
    __table__ = Table('article', md, autoload=True)

    # 查询所有文章
    def find_all(self):
        result = dbsession.query(Article).all()
        dbsession.close()
        return result

    # 指定分也参数，同时与用户表做连接查询 filter()过滤 隐藏和草稿，order_by 排序
    def find_limit_with_user(self, start, count):
        result = dbsession.query(Article, Users.nickname).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1) \
            .order_by(Article.articleid.asc()).limit(count).offset(start).all()
        dbsession.close()
        return result

    # 统计文章的数量
    def get_total_count(self):
        count = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1).count()
        dbsession.close()
        return count

    # 接口2
    # 根据文章类型获取文章
    def find_by_type(self, type, start, count):
        result = dbsession.query(Article, Users.nickname).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1, Article.category == type) \
            .order_by(Article.articleid.asc()).limit(count).offset(start).all()
        dbsession.close()
        return result

    # 根据文章类型获取文章的数量 ，统计分页数量，进行分页
    def get_artilce_type_count(self, type):
        count = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                                                Article.category == type).count()
        dbsession.close()
        return count

    # 接口3
    # 根据文章标题进行搜索
    def find_by_handline(self, headline, start, count):
        result = dbsession.query(Article, Users.nickname).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                    Article.headline.like('%' + headline + '%')) \
            .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        dbsession.close()
        return result

    # 统计文章数量 按上面的要求 ，统计分页数量，进行分页
    def get_count_by_headline(self, headline):
        count = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                                                Article.headline.like('%' + headline + '%')).count()
        dbsession.close()
        return count

    # 接口4
    # 最新文章
    def find_last_9(self):
        result = dbsession.query(Article.articleid, Article.headline) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1) \
            .order_by(Article.articleid.desc()).limit(9).all()
        dbsession.close()
        return result

    # 最多阅读
    def find_readcount_last_9(self):
        result = dbsession.query(Article.articleid, Article.headline) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1) \
            .order_by(Article.readcount.desc()).limit(9).all()
        dbsession.close()
        return result

    # 特别推荐 如果超过9 就随机显示 order by rand()  完整的sql==> SELECT * FROM article ORDER BY RAND() LIMIT 9
    def find_recommended_last_9(self):
        result = dbsession.query(Article.articleid, Article.headline) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1, Article.recommended == 1) \
            .order_by(func.rand()).limit(9).all()
        dbsession.close()
        return result

    # 将上面三个全部封装
    def find_last_readcount_recommended(self):
        last = self.find_last_9()
        most = self.find_recommended_last_9()
        recommended = self.find_readcount_last_9()
        return last, most, recommended

    # 接口5  文章阅读--》
    # 根据ID查询文章 只要一篇文章和作者 (Article, 'nickename') ==>格式
    def find_by_id(self, articleid):
        row = dbsession.query(Article, Users.nickname).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                    Article.articleid == articleid).first()
        dbsession.close()
        return row

    # 文章阅读次数+1
    def update_read_count(self, articleid):
        article = dbsession.query(Article).filter_by(articleid=articleid).first()
        article.readcount += 1
        dbsession.commit()
        dbsession.close()

    # 接口 6 上一篇下一篇文章
    # 根据文章编号查询文章标题
    def find_headline_by_id(self, articleid):
        row = dbsession.query(Article.headline).filter_by(articleid=articleid).first()
        dbsession.close()
        return row.headline

    # 获取文章上一篇和下一篇
    def find_prev_next_by_id(self, articleid):
        dict = {}
        # 小于判断的点，并且按id降序排序，取最大值
        row = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1,
                                              Article.articleid < articleid) \
            .order_by(Article.articleid.desc()).limit(1).first()
        # 如果已经是第一篇，上一篇还是第一篇
        if row is None:
            prev_id = articleid
        else:
            prev_id = row.articleid

        dict['prev_id'] = prev_id
        dict['prev_headline'] = self.find_headline_by_id(prev_id)

        # 小于判断的点，并且按id升序排序，取最小值
        row1 = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1, Article.articleid > articleid) \
            .order_by(Article.articleid).limit(1).first()
        # 如果已经是第一篇，上一篇还是第一篇
        if row1 is None:
            prev_id = articleid
        else:
            prev_id = row1.articleid

        dict['next_id'] = prev_id
        dict['next_headline'] = self.find_headline_by_id(prev_id)
        dbsession.close()
        return dict

    # 文章评论数量，当发表或者评论后，可以为文章表 字段replaycount +1
    def update_replay_count(self, articleid):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.replycount += 1
        dbsession.commit()
        dbsession.close()