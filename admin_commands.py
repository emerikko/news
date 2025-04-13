from data import db_session
from data.categories import Category


db_session.global_init("db/site.db")


def new_category(slug, title, description):
    db = db_session.create_session()
    category = Category(slug=slug, title=title, description=description)
    db.add(category)
    db.commit()
    return category
