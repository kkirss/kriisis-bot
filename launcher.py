import logging

import sqlalchemy
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from kriisis import KriisisBot, Scraper
from kriisis.models import Base, Category, Shop, User, Discount


def launch():  # TODO: Recheck discount expiring
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("Launcher")
    logger.info("Initializing...")
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("bs4").setLevel(logging.ERROR)
    engine = sqlalchemy.create_engine("sqlite:///db.sqlite3")
    Base.metadata.create_all(engine)
    session_factory = scoped_session(sessionmaker(engine, autoflush=False))
    if engine.execute("SELECT 1 FROM shops").first() is None:
        logger.info("Scraping all shops and categories...")
        session = session_factory()
        session.query(Shop).delete()
        session.query(Category).delete()
        shops = Scraper.scrape_shops()
        categories = Scraper.scrape_categories()
        session.add_all(shops)
        session.add_all(categories)
        session.commit()
        session.close()
    Category.init(session_factory)
    scraper = Scraper(session_factory)
    logging.info("Starting telegram bot...")
    kriisis_bot = KriisisBot(session_factory, scraper)
    kriisis_bot.start_bot()
    logging.info("Telegram bot started")
    session = session_factory()
    all_discounts = session.query(Discount).all()
    kriisis_bot.process_new_discounts(all_discounts)
    # with open("discounts.txt", "w", encoding="utf-8") as f:
    #     f.write("\n".join("{d.price}€ {d.start_date:%d.%m.%y}-{d.end_date:%d.%m.%y} {d.item_name} ({d.shop_names})".format(d=discount) for discount in all_discounts))
    # user = session.query(User).get(195688507)
    # url = "http://www.kriisis.ee/testing/files/05-12-2016/175207.jpg"
    # message = kriisis_bot.send_photo(user.chat_id, url)
    pass


if __name__ == "__main__":
    launch()
