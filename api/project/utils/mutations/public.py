"""
This module contains the public mutations for the project.

Public mutations do not need authentication headers to be present to give any
valid response. This is to allow public access to the mutation. For example,
a mutation to create a new user account. This mutation does not need to be
authenticated because anyone can create a new account. 

Public mutation sets the standard for all other mutations, to ensure that
all responses are consistent. For example, all mutations will return a
status code and a message. This is to ensure that the frontend can handle
all responses in the same way.
"""

# Django imports
from graphene import Mutation, String, Int


class PublicMutation(Mutation):
    """
    This class is the base class for all public mutations.
    """
    class Meta:
        abstract = True

    message = String()
