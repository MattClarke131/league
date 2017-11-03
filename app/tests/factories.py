# -*- coding: utf-8 -*-
"""Factories to help in tests."""
from factory import PostGenerationMethodCall, Sequence, SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from league.admin.models import User
from league.database import db
from league.models import Color, Game, Player


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    """User factory."""

    username = Sequence(lambda n: 'user{0}'.format(n))
    email = Sequence(lambda n: 'user{0}@example.com'.format(n))
    password = PostGenerationMethodCall('set_password', 'example')
    active = True
    first_name = Sequence(lambda n: 'Jim{0}'.format(n))
    last_name = Sequence(lambda n: 'Jones{0}'.format(n))

    class Meta:
        """Factory configuration."""

        model = User


class PlayerFactory(BaseFactory):
    """Player factory."""

    first_name = Sequence(lambda n: 'first{0}'.format(n))
    last_name = Sequence(lambda n: 'last{0}'.format(n))
    aga_id = Sequence(lambda n: n + 1000)
    aga_rank = Sequence(lambda n: (n % 9) + 1)

    class Meta:
        """Factory configuration."""

        model = Player


class GameFactory(BaseFactory):
    """Game factory."""

    white = SubFactory(PlayerFactory)
    black = SubFactory(PlayerFactory)
    winner = Color.white
    handicap = 0
    komi = 7
    season = 1
    episode = 1
    created_at = None

    class Meta:
        """Factory configuration."""

        model = Game
