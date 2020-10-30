import pytest

import datetime

from sqlalchemy.exc import IntegrityError

from csflix.domain.model import User, Movie as Article, Review as Comment, Tag, make_comment, make_tag_association



def insert_user(empty_session, values=None):
    new_name = "Andrew"
    new_password = "1234"

    if values is not None:
        new_name = values[0]
        new_password = values[1]

    empty_session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
                          {'username': new_name, 'password': new_password})
    row = empty_session.execute('SELECT id from users where username = :username',
                                {'username': new_name}).fetchone()
    return row[0]

def insert_users(empty_session, values):
    for value in values:
        empty_session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
                              {'username': value[0], 'password': value[1]})
    rows = list(empty_session.execute('SELECT id from users'))
    keys = tuple(row[0] for row in rows)
    return keys

def insert_article(empty_session):
    empty_session.execute(
        'INSERT INTO articles (id, title, genres, description, director, actors, release_year, runtime, rating, votes, revenue, metascore) VALUES (10, "Passengers", "Adventure,Drama,Romance", "A spacecraft traveling to a distant colony planet and transporting thousands of people has a malfunction in its sleep chambers. As a result, two passengers are awakened 90 years early.", "Morten Tyldum", "Jennifer Lawrence, Chris Pratt, Michael Sheen,Laurence Fishburne", "2016", "116", "7", "192177", "100.01", "41")'
    )
    row = empty_session.execute('SELECT id from articles').fetchone()
    return row[0]


def insert_commented_article(empty_session):
    article_key = insert_article(empty_session)
    user_key = insert_user(empty_session)


    empty_session.execute(
        'INSERT INTO comments (user_id, article_id, review_text, rating) VALUES '
        '(:user_id, :article_id, "Comment 1", "9"),'
        '(:user_id, :article_id, "Comment 2", "8")',
        {'user_id': user_key, 'article_id': article_key}
    )

    row = empty_session.execute('SELECT id from articles').fetchone()
    return row[0]


def make_article():
    article = Article('Movie', '2013', '10', '23434', '32', '8.8')
    article.title = 'Movie'
    article.runtime = 50
    article.description = "In a world"
    article.genres = "Comedy, Horror"
    article.director = "Mr Man"
    article.actors = "Actor 1, Actor 2"
    article.release_year = 2013
    article.rating = 4
    article.votes = 23434
    article.revenue = 32
    article.metascore = 8.8

    return article


def make_user():
    user = User('Bob', '212434')
    user.password = '212434'
    user.username = 'Bob'
    return user



def test_loading_of_users(empty_session):
    users = list()
    users.append(("Andrew", "1234"))
    users.append(("Cindy", "1111"))
    insert_users(empty_session, users)

    user1 = User("Andrew", "1234")
    user2 = User("Cindy", "999")
    user1.username = 'Andrew'
    user1.password = '1234'
    user2.username = 'Cindy'
    user2.password = '999'
    assert empty_session.query(User).all() == [user1, user2]

def test_saving_of_users(empty_session):
    user = make_user()
    empty_session.add(user)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT username, password FROM users'))
    assert rows == [("Bob", "212434")]


def test_saving_of_users_with_common_username(empty_session):
    insert_user(empty_session, ("Andrew", "1234"))
    empty_session.commit()

    with pytest.raises(IntegrityError):
        user = User("Andrew", "111")
        empty_session.add(user)
        empty_session.commit()


def test_loading_of_article(empty_session):
    article_key = insert_article(empty_session)
    expected_article = Article("Passengers", 
        "Adventure,Drama,Romance",
        "A spacecraft traveling to a distant colony planet and transporting thousands of people has a malfunction in its sleep chambers. As a result, two passengers are awakened 90 years early.",
        "Morten Tyldum",
        "Jennifer Lawrence, Chris Pratt, Michael Sheen,Laurence Fishburne",
        "2016")
    fetched_article = empty_session.query(Article).filter(Article.id == 10).one()

    assert article_key == fetched_article.id


def test_loading_of_commented_article(empty_session):
    insert_commented_article(empty_session)

    rows = empty_session.query(Article).all()
    article = rows[0]

    assert len(article.comments) == 2

    for comment in article.comments:
        assert comment._article is article


def test_saving_of_comment(empty_session):
    article_key = insert_article(empty_session)
    user_key = insert_user(empty_session, ("Andrew", "1234"))

    rows = empty_session.query(Article).all()
    article = rows[0]
    user = empty_session.query(User).filter(User.username == "Andrew").one()

    # Create a new Comment that is bidirectionally linked with the User and Article.
    comment_text = "Some comment text."
    comment = make_comment(comment_text, user, article, 6)

    # Note: if the bidirectional links between the new Comment and the User and
    # Article objects hadn't been established in memory, they would exist following
    # committing the addition of the Comment to the database.
    empty_session.add(comment)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_id, article_id, review_text FROM comments'))

    assert rows == [(user_key, article_key, comment_text)]

def test_saving_of_article(empty_session):
    article = make_article()
    empty_session.add(article)
    empty_session.commit()
    expected_article = make_article()

    rows = list(empty_session.execute('SELECT id, title, genres, description FROM articles'))
    assert rows == [(1,
                     expected_article.title,
                     expected_article.genres,
                     expected_article.description)]



def test_save_commented_article(empty_session):
    # Create Article User objects.
    article = make_article()
    user = make_user()

    # Create a new Comment that is bidirectionally linked with the User and Article.
    comment_text = "Some comment text."
    comment = make_comment(comment_text, user, article, 5)

    # Save the new Article.
    empty_session.add(article)
    empty_session.commit()

    # Test test_saving_of_article() checks for insertion into the articles table.
    rows = list(empty_session.execute('SELECT id FROM articles'))
    article_key = rows[0][0]

    # Test test_saving_of_users() checks for insertion into the users table.
    rows = list(empty_session.execute('SELECT id FROM users'))
    user_key = rows[0][0]

    # Check that the comments table has a new record that links to the articles and users
    # tables.
    rows = list(empty_session.execute('SELECT user_id, article_id, review_text FROM comments'))
    assert rows == [(user_key, article_key, comment_text)]