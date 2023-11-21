"""
Mutation to obtain and refresh access and refresh tokens, this is used in the accounts schema.
"""

# Django imports
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests

# Graphene imports
import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

# Local imports
from accounts.schema.types import UserType
from accounts.models import User, Username, USER_PROVIDERS
from utils.mutations.public import PublicMutation
from utils.mutations.private import PrivateMutation
from utils.errors import BadRequestError, ServerError

class ObtainSocialJSONWebToken(PublicMutation):
    """
    # Obtaining access and refresh tokens
    This mutation is used to obtain access and refresh tokens. It takes in the following arguments:
    - token
    - provider

    Here is an example of how to use this mutation:

    ```
    mutation {
        obtainSocialToken(provider:"GOOGLE", oauthToken:"<>") {
            message
            user{
                id
                email
                isEmailVerified
                isPoliciesAccepted
                isSelectedGames
                isAppliedUsername
                isSelectedAvatar
            }
            accessToken
            refreshToken
        }
    }
    ```
    
    """

    user = graphene.Field(UserType)
    access_token = graphene.Field(graphene.String)
    refresh_token = graphene.Field(graphene.String)

    class Arguments:
        oauth_token = graphene.String(required=True)
        provider = graphene.String(required=True)

    def GOOGLE(self, token):
        """ Google login. """
        email = None

        try:
            # Get user info from google.
            client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
            id_info = id_token.verify_oauth2_token(
                token, requests.Request(), client_id)
            if id_info['iss'] not in ['accounts.google.com',
                                    'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            email = id_info
        except ValueError:
            raise BadRequestError(
                "Invalid token. Please try again.")

        return email['email']
    
    def mutate(self, info, oauth_token=None, provider=None):

        if oauth_token is None:
            raise BadRequestError(
                'Token required field'
            )
        if provider is None:
            raise BadRequestError(
                'Provider required field'
            )
        
        # Get provider list
        providers = [provider[0] for provider in USER_PROVIDERS]

        # run provider function based on provider
        if provider in providers:
            user_email = getattr(ObtainSocialJSONWebToken, provider)(self,oauth_token)
        else:
            raise BadRequestError(
                'The provider is not supported.'
            )
        
        # Get user with user_email
        try:
            user = User.objects.get(email = user_email)

            # Generate access and refresh tokens
            access_token, refresh_token = RefreshToken.for_user(
                user).access_token, RefreshToken.for_user(user)
            
            return ObtainSocialJSONWebToken(user=user,  message='logged in successfully', access_token=str(access_token), refresh_token=str(refresh_token))
        
        except User.DoesNotExist:
            raise BadRequestError({
                "non_field_errors": [
                    'You dont have an account registered yet.'
                ]})
        
