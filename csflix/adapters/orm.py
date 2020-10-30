from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime,
    ForeignKey
)
from sqlalchemy.orm import mapper, relationship

from csflix.domain import model

metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False)
)

comments = Table(
    'comments', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('users.id')),
    Column('article_id', ForeignKey('articles.id')),
    Column('review_text', String(1024), nullable=False),
    Column('rating', Integer, nullable=False)
)

articles = Table(
    'articles', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False),
    Column('genres', String(1024), nullable=False),
    Column('description', String(1024), nullable=False),
    Column('director', String(255), nullable=False),
    Column('actors', String(1024), nullable=False),
    Column('release_year', String(255), nullable=False),
    Column('runtime', String(255), nullable=False),
    Column('rating', String(255), nullable=False),
    Column('votes', String(255), nullable=False),
    Column('revenue', String(255), nullable=False),
    Column('metascore', String(255), nullable=False)
)

tags = Table(
    'tags', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(64), nullable=False)
)

article_tags = Table(
    'article_tags', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('article_id', ForeignKey('articles.id')),
    Column('tag_id', ForeignKey('tags.id'))
)


def map_model_to_tables():
    mapper(model.User, users, properties={
        'username': users.c.username,
        'password': users.c.password,
        'comments': relationship(model.Review, backref='_user')
    })
    mapper(model.Review, comments, properties={
        'review_text': comments.c.review_text,
        'user_id' : comments.c.user_id,
        'article_id' : comments.c.article_id,
        'rating': comments.c.rating
    })
    articles_mapper = mapper(model.Movie, articles, properties={
        'id': articles.c.id,
        'title': articles.c.title,
        'genres': articles.c.genres,
        'description': articles.c.description,
        'director': articles.c.director,
        'actors': articles.c.actors,
        'release_year': articles.c.release_year,
        'runtime': articles.c.runtime,
        'rating' : articles.c.rating,
        'votes' : articles.c.votes,
        'revenue' : articles.c.revenue,
        'metascore' : articles.c.metascore,
        'comments': relationship(model.Review, backref='_article')
    })

    mapper(model.Tag, tags, properties={
        '_tag_name': tags.c.name,
        '_tagged_articles': relationship(
            articles_mapper,
            secondary=article_tags,
            backref="_tags"
        )
    })
