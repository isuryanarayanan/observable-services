"""
Mutation to create a new user with social auth, this is used in the accounts schema.
"""


# Native imports
from datetime import datetime, timedelta
import random

# Graphene imports
import graphene

# Django imports
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests

# Local imports
from accounts.schema.types import UserType
from accounts.models import User, Referral, Referred, USER_PROVIDERS
from utils.mutations.public import PublicMutation
from utils.mutations.private import PrivateMutation
from utils.errors import BadRequestError, ServerError


class CreateOauthUser(PublicMutation):
    """
    # Create a new Social User
    This mutation is used to create a new user. It takes in the following arguments:
    - oauthToken 
    - provider
    - referral

    Here is an example of how to use this mutation:

    ```
    mutation {
        createOauthUser(oauthToken:<"oauth_token">, provider:"GOOGLE", referral:"<referral code> (optional))") {
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
    access_token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        oauth_token = graphene.String(required=True)
        provider = graphene.String(required=True)
        referral = graphene.String(required=False)

    def GOOGLE(self, token):
        """ Get user data from google resource with the oauth token. """
        try:
            # Get user info from google.
            client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
            id_info = id_token.verify_oauth2_token(
                token, requests.Request(), client_id)
            if id_info['iss'] not in ['accounts.google.com',
                                      'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            user_info = id_info
        except ValueError as e:
            print(e)
            raise BadRequestError(
                "Invalid token. Please try again.")

        # Return the user information
        return user_info['email']

    def mutate(self, info, oauth_token=None, provider=None, referral=None):

        if oauth_token is None:
            raise BadRequestError(
                'An oauth token is required to register.'
            )
        if provider is None:
            raise BadRequestError(
                'A provider is required to register.'
            )

        # Get provider list.
        providers = [provider[0] for provider in USER_PROVIDERS]
        user_email = None

        # run provider function based on provider
        print(provider, self)
        if provider in providers:
            user_email = getattr(CreateOauthUser, provider)(self, oauth_token)
        else:
            raise BadRequestError(
                'The provider is not supported.'
            )

        # Check if user info is valid.
        if user_email is None:
            raise BadRequestError(
                'The oauth token is invalid.'
            )

        try:

            if User.objects.filter(email=user_email).exists():
                message = 'User already exists'
                user = User.objects.get(email=user_email)

            else:
                message = 'User created successfully'
                user = User.objects.create_social_user(
                    email=user_email,
                    provider=provider
                )

                user.save()

                if referral is not None and len(referral) != 0:
                    Referred.objects.create(
                        user=user,
                        referral=Referral.objects.get(code=referral)
                    )

            # Generate access and refresh tokens
            access_token, refresh_token = RefreshToken.for_user(
                user).access_token, RefreshToken.for_user(user)

            return CreateOauthUser(user=user,  message=message, access_token=str(access_token), refresh_token=str(refresh_token))
        except Exception as e:
            if not isinstance(e, (BadRequestError)):
                raise ServerError(str(e))
            else:
                raise e


class UpdateUserDOB(PrivateMutation):
    """
    # Updating the user's date of birth (dob).

    Here is an example of how to use this mutation:

    ```
    mutation {
        updateUserDOB(dob:"2000-01-01"){
            message
            user{
                id
                dob
            }
        }
    }
    ```

    This mutation updates the user's dob with the provided date.
    """

    EXEMPT_CHECKS = True

    user = graphene.Field(UserType)

    class Arguments:
        dob = graphene.Date(required=True)

    @classmethod
    def perform_mutation(cls, root, info, user, **inputs):
        try:
            dob = inputs.get('dob')

            # Check if dob is valid
            if dob is None:
                raise BadRequestError(
                    'A valid date of birth is required.'
                )

            # Check if the user is above 13 years of age
            thirteen_years_ago = datetime.now() - timedelta(days=365*13)
            if dob > thirteen_years_ago.date():
                raise BadRequestError(
                    'You must be at least 13 years of age to use this service.'
                )

            user.dob = dob
            user.is_dob_verified = True
            user.save()
        except Exception as e:
            if not isinstance(e, (BadRequestError)):
                raise ServerError(str(e))
            else:
                raise e

        return UpdateUserDOB(
            user=user,
            message='DOB updated sucessfully',
        )
