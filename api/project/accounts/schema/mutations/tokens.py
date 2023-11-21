"""
Mutation to obtain and refresh access and refresh tokens, this is used in the accounts schema.
"""

# Django imports
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

# Graphene imports
import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

# Local imports
from accounts.schema.types import UserType
from accounts.models import User, Username
from utils.mutations.public import PublicMutation
from utils.mutations.private import PrivateMutation
from utils.errors import BadRequestError, ServerError


# Mutation to obtain access and refresh tokens
class ObtainJSONWebToken(PublicMutation):
    """
    # Obtaining access and refresh tokens
    This mutation is used to obtain access and refresh tokens. It takes in the following arguments:
    - email | username
    - password

    Here is an example of how to use this mutation:

    ```
    mutation {
        obtainToken(identifier:"<Email address or Username with tag>", password:"<>") {
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

    You can use the access token to identify yourself in the future. The access token is valid for 10 minutes.
    It is used via the Authorization header in the following format:

    ```
    {
        "Authorization": "JWT <Access token>"
    }
    ```

    The refresh token is valid for 365 days. It is used to refresh the period of the access token.
    """
    user = graphene.Field(UserType)
    access_token = graphene.Field(graphene.String)
    refresh_token = graphene.Field(graphene.String)

    class Arguments:

        # email or username can be used to login
        # It is required but can be null

        identifier = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, identifier, password):

        email = None
        username = None

        # Check if the identifier is an email or username
        if '@' in identifier:
            email = identifier
        else:
            username = identifier

        if username is not None:
            try:
                username, tag = username.split('#')
                email = Username.objects.get(
                    username=username, tag=tag).user.email
            except Exception:
                raise BadRequestError('Invalid Credentials')

        user = authenticate(info.context, email=email, password=password)
        if user is None:
            raise BadRequestError('Invalid credentials')

        refresh = RefreshToken.for_user(user)
        return ObtainJSONWebToken(
            user=user,
            access_token=str(refresh.access_token),
            refresh_token=str(refresh),
            message='User logged in successfully'
        )


# Mutation to refresh access and refresh tokens
class RefreshJSONWebToken(PublicMutation):
    """
    # Refreshing access and refresh tokens

    This mutation is used to refresh the access and refresh tokens. It takes in the following arguments:
    - refresh_token
    - refresh

    Here is an example of how to use this mutation:
    ```
    mutation {
        refreshToken(refreshToken:"<your-refresh-token>", refresh:<true or false>) {
            message
            accessToken
            refreshToken
        }
    }
    ```

    If the refresh argument is true, then the refresh token is also refreshed, else it is not only the access token that is refreshed.
    This is used when the user logs out and logs in again.
    """
    access_token = graphene.Field(graphene.String)
    refresh_token = graphene.Field(graphene.String)

    class Arguments:
        refresh_token = graphene.String(required=True)
        refresh = graphene.Boolean(required=False)

    def mutate(self, info, refresh_token, refresh):

        # If refresh is true, then the refresh token is also refreshed
        # This is used when the user logs out and logs in again
        # The refresh token is refreshed so that the old refresh token is no longer valid

        if refresh:
            try:
                # Get user from refresh token
                refresh = RefreshToken(refresh_token)
                user = User.objects.get(id=refresh['user_id'])
                refresh = RefreshToken.for_user(user)
            except Exception as e:
                raise BadRequestError(str(e))

            return RefreshJSONWebToken(
                refresh_token=str(refresh),
                access_token=str(refresh.access_token),
                message='Access token refreshed successfully'
            )

        else:

            try:
                refresh = RefreshToken(refresh_token)
            except Exception as e:
                raise BadRequestError(str(e))

            return RefreshJSONWebToken(
                refresh_token=str(refresh),
                access_token=str(refresh.access_token),
                message='Access token refreshed successfully'
            )


class VerifyJSONWebToken(PrivateMutation):
    """
    # Verifying an access token

    This mutation is used to verify the access token. It takes in the following arguments:
    - access_token

    Here is an example of how to use this mutation:
    ```graphql
    mutation {
        verifyToken {
            message
            user{
                id
                email
            }
        }
    }
    ```

    This is used to verify the access token, so the header must contain the access token.
    Here is how to use the access token in the header:
    ```
    {
    "Authorization":"JWT <access_token>"
    }
    """

    user = graphene.Field(UserType)

    @classmethod
    def perform_mutation(cls, root, info, user, **inputs):
        return VerifyJSONWebToken(user=user, message=f'Hello {user.email}, you are logged in!')
