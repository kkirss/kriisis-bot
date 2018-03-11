from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import literal
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

DEFAULT_PICTURE_NOTIFICATIONS = False
DEFAULT_NOTIFY_TIME = -1


class Nameable(object):
    name = Column(String, nullable=False)

    @classmethod
    def search(cls, query, session, search_limit=10):
        return session.query(cls).filter(cls.name.contains(literal(query))).limit(search_limit).all()


class Category(Nameable, Base):
    __tablename__ = "categories"
    end_categories = []  # Categories with no children

    category_id = Column(Integer, primary_key=True)

    children = relationship("Category", back_populates="parents", secondary="category_associations",
                            primaryjoin="Category.category_id==CategoryAssociation.parent_id",
                            secondaryjoin="Category.category_id==CategoryAssociation.child_id")
    parents = relationship("Category", back_populates="children", secondary="category_associations",
                           primaryjoin="Category.category_id==CategoryAssociation.child_id",
                           secondaryjoin="Category.category_id==CategoryAssociation.parent_id")
    subscribed_users = relationship("User", back_populates="subscribed_categories", secondary="category_subscriptions")

    def __init__(self):
        self._ancestors = None

    @orm.reconstructor
    def init_on_load(self):
        self._ancestors = None

    def __str__(self):
        return "category {}: {} ({})".format(self.category_id, self.name,
                                             ",".join(parent.name for parent in self.parents))

    @property
    def ancestors(self):
        if self._ancestors is None:
            self._ancestors = set()
            stack = list(self.parents)
            while stack:
                parent = stack.pop()
                self._ancestors.add(parent)
                stack.extend(parent.parents)
        return self._ancestors

    @staticmethod
    def init(session_factory):
        session = session_factory()
        Category.end_categories = session.query(Category).filter(~Category.children.any()).all()


class CategoryAssociation(Base):
    __tablename__ = "category_associations"

    child_id = Column(Integer, ForeignKey("categories.category_id"), primary_key=True)
    parent_id = Column(Integer, ForeignKey("categories.category_id"), primary_key=True)


class CategorySubscription(Base):
    __tablename__ = "category_subscriptions"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), primary_key=True)


class Discount(Base):
    __tablename__ = "discounts"
    NOTIFICATION_FORMAT = """*{d.item_name}*\n_{d.item_description}_\n{d.price}\n{d.shop_names}\n{d.end_date:%d.%m.%y}"""
    NOTIFICATION_FORMAT_NO_DESCRIPTION = """*{d.item_name}*\n{d.price}\n{d.shop_names}\n{d.end_date:%d.%m.%y}"""

    discount_id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    item_name = Column(String, nullable=False)
    item_description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    image_url = Column(String, nullable=False)
    image_file_id = Column(String)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    category = relationship("Category")
    shops = relationship("Shop", back_populates="discounts", secondary="discount_shops")

    @property
    def shop_names(self):
        return ", ".join(shop.name for shop in self.shops)

    @property
    def notification_str(self):
        if self.item_description == "":
            return self.NOTIFICATION_FORMAT_NO_DESCRIPTION.format(d=self)
        else:
            return self.NOTIFICATION_FORMAT.format(d=self)


class DiscountShop(Base):
    __tablename__ = "discount_shops"

    discount_id = Column(Integer, ForeignKey("discounts.discount_id"), primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.shop_id"), primary_key=True)


class Shop(Nameable, Base):
    __tablename__ = "shops"

    shop_id = Column(Integer, primary_key=True)
    image_url = Column(String, nullable=False)

    subscribed_users = relationship("User", back_populates="subscribed_shops", secondary="shop_subscriptions")
    discounts = relationship("Discount", back_populates="shops", secondary="discount_shops")

    def __str__(self):
        return "shop {}: {}".format(self.shop_id, self.name)


class ShopSubscription(Base):
    __tablename__ = "shop_subscriptions"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.shop_id"), primary_key=True)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    picture_notifications = Column(Boolean, default=DEFAULT_PICTURE_NOTIFICATIONS, nullable=False)
    notification_time = Column(Integer, default=DEFAULT_NOTIFY_TIME, nullable=False)

    subscribed_categories = relationship("Category", back_populates="subscribed_users",
                                         secondary="category_subscriptions")
    subscribed_shops = relationship("Shop", back_populates="subscribed_users", secondary="shop_subscriptions")
