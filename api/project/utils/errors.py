"""
This file contains extended error types.
"""

# Graphene imports
from graphql import GraphQLError
from builtins import BaseException


class BaseWSException(BaseException):
    """
    This class is the base class for all websocket exceptions.
    """

    def __init__(self, message, status=400):
        """
        This method initializes the class.

        Args:
            message (str): The error message.
            status (int): The status code.
        """

        # Initialize the class
        super().__init__(message)

        self.extensions = {
            'status': status
        }


class BaseError(BaseException):
    """
    This class is the base class for all errors.
    """
    pass


class BasicError(GraphQLError, BaseError):
    """
    This class is the base class for all errors.
    """

    def __init__(self, message, status=400):
        """
        This method initializes the class.

        Args:
            message (str): The error message.
            status (int): The status code.
        """

        # Initialize the class
        super().__init__(message)

        self.extensions = {
            'status': status
        }


class BadRequestError(BasicError):
    """
    This class is used to raise bad request errors.
    """

    def __init__(self, message="Bad request.", status=400):
        """
        This method initializes the class.

        Args:
            message (str): The error message.
            status (int): The status code.
        """

        # Initialize the class
        super().__init__(message, status)


class AuthenticationError(BasicError):
    """
    This class is used to raise authentication errors.
    """

    def __init__(self, message="You must be logged in to perform this action.", status=401):
        """
        This method initializes the class.

        Args:
            message (str): The error message.
            status (int): The status code.
        """

        # Initialize the class
        super().__init__(message, status)


class AuthorizationError(BasicError):
    """
    This class is used to raise authorization errors.
    """

    def __init__(self, message="You do not have permission to perform this action.", status=403):
        """
        This method initializes the class.

        Args:
            message (str): The error message.
            status (int): The status code.
        """

        # Initialize the class
        super().__init__(message, status)


class ServerError(BasicError):
    """
    This class is used to raise server errors.
    """

    def __init__(self, message="An error occurred on the server.", status=500):
        """
        This method initializes the class.

        Args:
            message (str): The error message.
            status (int): The status code.
        """

        # Initialize the class
        super().__init__(message, status)


class ValidationError(BasicError):
    """
    This class is used to raise validation errors.
    """

    def __init__(self, message="Validation error.", status=400):
        """
        This method initializes the class.

        Args:
            message (str): The error message.
            status (int): The status code.
        """

        # Initialize the class
        super().__init__(message, status)
