from sqlalchemy import MetaData

def dbconnet():
    from main import db
    dbsession = db.session
    DBase = db.Model
    matadata = MetaData(bind=db.engine)
    return (dbsession, matadata, DBase)  # 注意 返回顺序