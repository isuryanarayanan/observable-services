"""
Schema for the accounts app
"""

# Graphene imports
import graphene

# Schema imports

# Mutations
from accounts.schema.mutations.create_user import CreateUser
from accounts.schema.mutations.social_auth import CreateOauthUser, UpdateUserDOB
from accounts.schema.mutations.username import CreateUsername, EditUsername
from accounts.schema.mutations.update_password import UpdatePassword
from accounts.schema.mutations.tokens import ObtainJSONWebToken, RefreshJSONWebToken, VerifyJSONWebToken
from accounts.schema.mutations.social_token import ObtainSocialJSONWebToken

# Queries
from accounts.schema.queries.fetch_users import fetchUsers


class Query(graphene.ObjectType):
    """
    All the queries for the accounts app need to be added here as a parameter.
    """
    serverTime = graphene.DateTime()

    async def resolve_serverTime(self, info):
        return asyncio.get_event_loop().time()


class Mutation(graphene.ObjectType):
    """
    # Accounts mutations
    - `createUser` - Create a new user
    - `createOauthUser` - Create a new user with social oauth
    - `updateUserDob` - Update the date of birth of the user
    - `createUsername` - Create a username for the user
    - `editUsername` - Edit the username of the user
    - `passwordUpdate` - Update the password of a user
    - `obtainToken` - Obtain access and refresh tokens
    - `obtainSocialToken` - Obtain access and refresh token with social oauth
    - `refreshToken` - Refresh the access token
    - `verifyToken` - Verify the access token
    - `createPhone` - Adds a phone number for the user
    - `editPhone` - Edit the phone number of the user
    """
    create_user = CreateUser.Field()
    create_oauth_user = CreateOauthUser.Field()
    update_user_dob = UpdateUserDOB.Field()
    create_username = CreateUsername.Field()
    edit_username = EditUsername.Field()
    update_password = UpdatePassword.Field()
    obtain_token = ObtainJSONWebToken.Field()
    obtain_social_token = ObtainSocialJSONWebToken.Field()
    refresh_token = RefreshJSONWebToken.Field()
    verify_token = VerifyJSONWebToken.Field()


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
)
