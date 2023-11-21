"""
Types for the accounts schema
"""

# Graphene imports
import graphene
from graphene_django import DjangoObjectType

# Local imports
from accounts.models import User, Username, Referral, Referred

# Graphql representation of the User model
class BaseUserType(DjangoObjectType):
    class Meta:
        model = User

class UserType(BaseUserType):
    class Meta:
        model = User
        exclude_fields = ('password', 'referred')
    
    is_applied_username = graphene.Boolean()

    def resolve_is_applied_username(self,info):
        return Username.objects.filter(user = self).exists()

class UsernameType(DjangoObjectType):
    class Meta:
        model = Username


class ReferralType(DjangoObjectType):
    class Meta:
        model = Referral


class ReferredType(DjangoObjectType):
    class Meta:
        model = Referred
