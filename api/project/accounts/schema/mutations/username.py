"""
Mutation to create a new username for the user, this is used in the accounts schema.
"""

# Native imports
from datetime import datetime, timedelta

# Graphene imports
import graphene

# Local imports
from accounts.schema.types import UserType, UsernameType
from accounts.models import User, Username
from utils.mutations.private import PrivateMutation
from utils.errors import BadRequestError, ServerError


class CreateUsername(PrivateMutation):
    """
    # Creating a username for the user.
    A username is not just a field in the user model, it is a separate model
    that has a 1 to 1 relationship with the user model. So when you create a 
    username, you are creating a new object in the username model and is automatically
    linked to the user model of the user which created it.

    Here is an example of how to use this mutation:

    ```
    mutation {
        createUsername(username:"superuser"){
            message
            user{
                id
            }
            username {
                id
                username
                tag
            }
        }
    }
    ```

    Username consists of 2 parts:
    - username
    - tag

    The username is the name that the user chooses, and the tag is a random 4 digit number
    that is generated when the username is created. The tag is used to differentiate between
    users with the same username. A user can only have 1 username, and a username can only be used by 1 user.
    """
    user = graphene.Field(UserType)
    username = graphene.Field(UsernameType)

    EXEMPT_CHECKS = True

    class Arguments:
        username = graphene.String(required=True)

    @classmethod
    def perform_mutation(cls, root, info, user, **inputs):
        try:
            username = inputs.get('username')
            username_obj = Username.objects.filter(
                username=username, user=user).first()
            if username_obj:

                return CreateUsername(
                    user=user,
                    message='Username created sucessfully',
                    username=username_obj
                )

            else:
                # Save the username to the database
                username = Username.objects.create(
                    user=user,
                    username=username,
                )
                username.save()

        except Exception as e:
            if not isinstance(e, (BadRequestError)):
                raise ServerError(str(e))
            else:
                raise e

        return CreateUsername(
            user=user,
            message='Username created sucessfully',
            username=username
        )


class EditUsername(PrivateMutation):
    """
    # Editing a username for the user.
    A username is not just a field in the user model, it is a separate model
    that has a 1 to 1 relationship with the user model. So when you edit a 
    username, you are editing an object in the username model and is automatically
    linked to the user model of the user which created it.

    Here is an example of how to use this mutation:

    ```
    mutation {
        editUsername(username:"superuser"){
            message
            user{
                id
            }
            username {
                id
                username
                tag
            }
        }
    }
    ```

    Username consists of 2 parts:
    - username
    - tag

    The username is the name that the user chooses, and the tag is a random 4 digit number
    that is generated when the username is created. The tag is used to differentiate between
    users with the same username. A user can only have 1 username, and a username can only be used by 1 user.
    """
    user = graphene.Field(UserType)
    username = graphene.Field(UsernameType)

    class Arguments:
        username = graphene.String(required=True)

    @classmethod
    def perform_mutation(cls, root, info, user, **inputs):
        try:
            username = inputs.get('username')
            if Username.objects.filter(username=username).exists():
                raise BadRequestError('Username already exists')

            # Check if user has a username already
            if not Username.objects.filter(user=user).exists():
                raise BadRequestError('User does not have a username')

            # Save the username to the database
            username_obj = Username.objects.get(user=user)
            username_obj.username = username

            username_obj.save()

        except Exception as e:
            if not isinstance(e, (BadRequestError)):
                raise ServerError(str(e))
            else:
                raise e

        return EditUsername(
            user=user,
            message='Username edited sucessfully',
            username=username_obj
        )
