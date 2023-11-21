"""
This module contains the private mutations for the project.

Private mutation need authentication headers to be present to give any
valid response. This is to prevent unauthorized access to the mutation.

Private mutations are used to perform actions that are not meant to be
publicly available. For example, a mutation to delete a user account.
"""

# Django imports
from rest_framework_simplejwt.authentication import JWTAuthentication
from graphql import GraphQLError

# Local imports
from utils.mutations.public import PublicMutation
from utils.errors import AuthenticationError, ServerError, BadRequestError, AuthorizationError


class PrivateMutation(PublicMutation):
    """
    This class is the base class for all private mutations.

    It is used to check if the user is authenticated before performing
    the mutation. If the user is not authenticated, a PermissionDenied
    exception is raised.
    """
    class Meta:
        abstract = True

    EXEMPT_CHECKS = False

    @ classmethod
    def mutate(cls, root, info, **inputs):

        try:

            # Check if Authorization header is set
            if not info.context.headers.get('Authorization'):
                # Return message and status code
                raise AuthenticationError(
                    message="Authorization header is required")

            # Get the user from the token
            try:
                user = JWTAuthentication().authenticate(info.context)[0]
            except Exception as e:
                raise AuthenticationError(
                    message="Invalid token")

            # Check if the user is authenticated
            if not user.is_authenticated:
                raise AuthenticationError

            if not cls.EXEMPT_CHECKS:
                if not user.is_valid_user():
                    raise AuthorizationError(
                        message="User account setup is not complete.")

        except Exception as e:
            # If the exception is not an AuthenticationError or BadRequestError
            if not isinstance(e, (AuthenticationError, BadRequestError)):
                # Raise a server error
                raise ServerError(str(e))
            else:
                # Raise the exception
                raise e

        # Perform the mutation
        return cls.perform_mutation(root, info, user,  **inputs)

    @ classmethod
    def perform_mutation(cls, root, info, user, **inputs):
        # This method must be implemented by the subclass
        raise NotImplementedError(
            'PrivateMutation subclasses must implement perform_mutation()')
