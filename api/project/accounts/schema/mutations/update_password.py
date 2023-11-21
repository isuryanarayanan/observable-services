"""
Mutation to update a user's password, this is used in the accounts schema.
"""

# Graphene imports
import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

# Django imports
from rest_framework_simplejwt.authentication import JWTAuthentication

# Local imports
from accounts.schema.types import UserType
from utils.mutations.private import PrivateMutation
from utils.errors import BadRequestError, ServerError


# Mutation to update a user's password
class UpdatePassword(PrivateMutation):
    """
    # Updating a user's password

    This mutation is used to update a user's password. It takes in the following arguments:
    - password
    - newPassword

    Here is an example of how to use this mutation:

    ```
    mutation {
        updatePassword(password:"<Current password>", newPassword:"<>") {
            message
            user{
                id
                email
            }
        }
    }
    ```

    This is a private mutation, so you need to be logged in to use it.
    see [Obtaining access and refresh tokens](#obtaining-access-and-refresh-tokens) for more information.
    """
    user = graphene.Field(UserType)

    class Arguments:
        password = graphene.String(required=True)
        new_password = graphene.String(required=True)

    @classmethod
    def perform_mutation(cls, root, info, user, **inputs):
        try:
            password = inputs.get('password')
            new_password = inputs.get('new_password')

            if user.check_password(password):
                user.set_password(new_password)
                user.save()
                return UpdatePassword(user=user, message="Password updated")
            else:
                raise BadRequestError("Invalid current password")

        except Exception as e:
            if not isinstance(e, BadRequestError):
                raise ServerError(str(e))
            else:
                raise e
