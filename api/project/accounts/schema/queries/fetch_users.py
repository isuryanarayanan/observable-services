"""
Query to fetch all users
"""

# Graphene imports
import graphene
from graphene_django import DjangoObjectType

# Local imports
from accounts.schema.types import BaseUserType as UserType
from accounts.models import User


class fetchUsers(graphene.ObjectType):
    users = graphene.List(UserType)

    def resolve_users(self, info):
        return User.objects.all()
