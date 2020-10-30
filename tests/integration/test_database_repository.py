from datetime import date, datetime

import pytest

from csflix.adapters.database_repository import SqlAlchemyRepository
from csflix.domain.model import User, Movie as Article, Tag, Review as Comment, make_comment
from csflix.adapters.repository import RepositoryException

def test_repository_can_add_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User('Dave', '123456789')
    user.username = 'Dave'
    user.password = '123456789'
    repo.add_user(user)

    user2 = repo.get_user('Dave')

    assert user2 == user 

def test_repository_can_retrieve_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('fmercury')
    user2 = User('fmercury', '8734gfe2058v')
    user2.username = 'fmercury'
    user2.password = '8734gfe2058v'
    assert user == user2

def test_repository_does_not_retrieve_a_non_existent_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('prince')
    assert user is None

def test_repository_can_retrieve_article_count(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_articles = repo.get_number_of_articles()

    assert number_of_articles == 1000

def test_repository_can_add_article(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_articles = repo.get_number_of_articles()

    new_article_id = number_of_articles + 1

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
    repo.add_article(article)

    assert repo.get_article(new_article_id) == article

def test_repository_can_retrieve_article(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    article = repo.get_article(1)

    # Check that the Article has the expected title.
    assert article.title == 'Guardians of the Galaxy'

    # Check that the Article is commented as expected.
    comment_one = article.comments[0]
    comment_two = article.comments[1]

    assert comment_one.user_id== 2
    assert comment_two.user_id == 1


def test_repository_does_not_retrieve_a_non_existent_article(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    article = repo.get_article(2001)
    assert article is None

def test_repository_can_retrieve_articles_by_empty_search_and_None_searchtype(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    articles = repo.get_all_movies(0, '', None)

    for movie in articles:
        assert '' in movie.title.lower()
        
def test_repository_can_retrieve_articles_by_search_and_None_searchtype(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    articles = repo.get_all_movies(0, 'o', None)

    for movie in articles:
        assert 'o' in movie.title.lower()

def test_repository_can_retrieve_articles_by_search_and_searchtype(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    articles = repo.get_all_movies(0, 'adam', 'actors')

    for movie in articles:
        assert 'adam' in movie.actors.lower()

def test_repository_can_retrieve_articles_by_search(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    articles = repo.get_all_movies(0, 'la', 'title')

    for movie in articles:
        assert 'la' in movie.title.lower()


def test_repository_raises_error_upon_invalid_search(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    with pytest.raises(IndexError):
        articles = repo.get_all_movies(0, "dkzsjlfhgkxdj", 'title')



def test_repository_can_get_first_article(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    article = repo.get_first_article()
    assert article.title == 'Guardians of the Galaxy'

def test_repository_can_get_last_article(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    article = repo.get_last_article()
    assert article.title == 'Nine Lives'

def test_repository_can_get_articles_by_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    articles = repo.get_articles_by_id([2, 5, 6])

    assert len(articles) == 3
    assert articles[0].title == 'Prometheus'
    assert articles[1].title == "Suicide Squad"
    assert articles[2].title == 'The Great Wall'

def test_repository_does_not_retrieve_article_for_non_existent_id(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    articles = repo.get_articles_by_id([2, 1001])

    assert len(articles) == 1
    assert articles[0].title == 'Prometheus'


def test_repository_can_add_a_comment(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('thorke')
    article = repo.get_article(2)
    comment = make_comment("Boo", user, article, 0)

    repo.add_comment(comment)

    assert comment in repo.get_comments()



def test_repository_can_retrieve_comments(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    assert len(repo.get_comments()) == 3


def make_article(new_article_date):
    article = Article(
        new_article_date,
        'Coronavirus travel restrictions: Self-isolation deadline pushed back to give airlines breathing room',
        'The self-isolation deadline has been pushed back',
        'https://www.nzherald.co.nz/business/news/article.cfm?c_id=3&objectid=12316800',
        'https://th.bing.com/th/id/OIP.0lCxLKfDnOyswQCF9rcv7AHaCz?w=344&h=132&c=7&o=5&pid=1.7'
    )
    return article

def test_can_retrieve_an_article_and_add_a_comment_to_it(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    # Fetch Article and User.
    article = repo.get_article(5)
    author = repo.get_user('thorke')

    # Create a new Comment, connecting it to the Article and User.
    comment = make_comment('ehhh', author, article, 2)

    article_fetched = repo.get_article(5)
    author_fetched = repo.get_user('thorke')

    assert comment.user_id == 1
    assert comment.article_id == 5
