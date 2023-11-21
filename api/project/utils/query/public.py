"""
Public query functions
"""

# Graphene imports
import graphene

from utils.errors import AuthenticationError, BadRequestError, ServerError
from rest_framework_simplejwt.authentication import JWTAuthentication


class PublicQuery(graphene.ObjectType):
    """
    Public query functions
    """

    hello = graphene.String(description="A simple greeting")

    def resolve_hello(self, info):
        return "Hello, world!"


class PrivateQuery:
    """
    Private query functions

    This query is pretty much like the private mutation, it will be used to
    fetch data that is not public and will be used by the frontend to render
    the dashboard.

    This query will fetch data only if the user is authenticated. If the user
    is not authenticated, it will return an error.
    """

    @classmethod
    def __init_subclass_with_meta__(cls, **options):
        super().__init_subclass_with_meta__(**options)

        # For all functions that are implemented with the resolve_ prefix
        for name, field in cls._meta.fields.items():
            if name.startswith("resolve_"):
                # Get the original resolver function
                original_resolver = getattr(cls, name)

                # Wrap the original resolver function with the private resolver
                # function
                setattr(cls, name, cls.private_resolver(original_resolver))

    @classmethod
    def private_resolver(cls, original_resolver):
        """
        Private resolver function

        This function will be used to wrap the original resolver function
        and check if the user is authenticated or not.
        """

        print("Private resolver function")

        def resolver(self, info, **kwargs):
            """
            Resolver function
            """

            # Get the request object
            request = info.context

            # Get the user object
            user = request.user

            # Check if the user is authenticated or not
            if user.is_authenticated:
                # If the user is authenticated, return the original resolver
                # function
                return original_resolver(self, info, **kwargs)
            else:
                # If the user is not authenticated, return an error
                raise AuthenticationError("You are not authenticated.")

        return resolver
