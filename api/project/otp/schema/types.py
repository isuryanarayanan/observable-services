"""
Types for the otp schema
"""

# Graphene imports
import graphene
from graphene_django import DjangoObjectType
from graphene import relay

# Local imports
from otp.models import OneTimePassword


# Graphql representation of the OneTimePassword model
class OneTimePasswordType(DjangoObjectType):
    class Meta:
        model = OneTimePassword

# Model
class OneTimePasswordNode(DjangoObjectType):
    class Meta:
        model = OneTimePassword
        interfaces = (relay.Node,)


# Custom types
class OtpSuccessType(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()
    otp = graphene.Field(OneTimePasswordNode)