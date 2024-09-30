
#from app import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from database import db 
from sqlalchemy.sql import func
from sqlalchemy_serializer import SerializerMixin
from feedgen.feed import FeedGenerator

class Podcast(db.Model, SerializerMixin):
    __tablename__ = 'podcasts'
    serialize_only = ('id', 'user_id', 'title', 'subtitle', 'description', 'link', 'language', 'author', 'owner', 'image', 'category', 'explicit')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True, nullable=True)
    title = db.Column(db.String())
    subtitle = db.Column(db.String())
    description = db.Column(db.String())
    link = db.Column(db.String())
    language = db.Column(db.String)
    author = db.Column(JSONB)  #list of hash e.g. [{'name':'john', 'email': 'john@example.com', 'uri': ''}]
    owner = db.Column(db.String())
    image = db.Column(db.String())
    category = db.Column(JSONB) #list of hash e.g.[{'term': 'technology', 'scheme': 'xx', 'label': 'technology'}]
    explicit = db.Column(db.String())
    guid = db.Column(db.String(), index=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    items = db.relationship("PodcastItem", back_populates="podcast")

    def __init__(self, user_id, title, subtitle, description, link, language, author, owner, image, category, explicit):
        self.user_id = user_id
        self.title = title
        self.subtitle = subtitle
        self.descriptio  = description 
        self.link = link
        self.language = language
        self.author = author
        self.owner = owner
        self.image = image
        self.category = category
        self.explicit = explicit


    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def rss(self):
        fg = FeedGenerator()
        fg.load_extension('podcast')
        fg.link(href=self.link)
        fg.podcast.itunes_author(self.author[0]['name'])
        fg.podcast.itunes_category(self.category)
        fg.podcast.itunes_complete('yes')
        fg.podcast.itunes_image(self.image)
        fg.title(self.title)
        fg.podcast.itunes_subtitle(self.subtitle)
        fg.description(self.description)
        for item in self.items:
            fe = fg.add_entry()
            fe.id(item.url)
            fe.title(item.title)
            fe.description(item.description)
            fe.enclosure(item.url, item.duration, item.type)

        return fg.rss_str()