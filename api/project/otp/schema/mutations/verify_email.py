"""
Mutation to verify a new user's email, this is used in the otp schema.
"""

# Native imports
from datetime import datetime, timedelta

# Django imports
from rest_framework_simplejwt.authentication import JWTAuthentication

# Graphene imports
import graphene
from graphql import GraphQLError

# Local imports
from accounts.models import User
from accounts.schema.types import UserType
from utils.mutations.protected import ProtectedMutation
from aws.models import SESEmailTemplate


class ValidateEmail(ProtectedMutation):
    """
    # Validate email mutation

    This mutation is used to verify a new user's email. The user will receive an OTP
    when they sign up. This mutation provides a way to verify the OTP. and complete
    the email verification process.

    ## Steps

    1. The user provides the OTP and validates it, in exchange for a ghost code and otp id.
    2. The user provides the OTP id and ghost code to complete the mutation.

    ### Step 1

    ```graphql
    mutation {
        validateEmail(
            otp: "<otp>",
            validate: true
        ) {
            message
            otp
            ghostCode
        }
    }
    ```

    ### Step 2

    Here the otp is not the OTP that was sent to the user, but the OTP id that was
    returned in the previous mutation.

    ```graphql
    mutation {
        validateEmail(
            otp: "<otp>",
            ghostCode: "<ghostCode>",
            complete: true
        ) {
            message
        }
    }
    ```

    Once the mutation is completed, the user's email will be verified.

    ## Resend OTP

    If the user does not receive the OTP, they can request for a new OTP by providing
    the email and initiating the mutation.

    ```graphql
    mutation {
        validateEmail(
            initiate: true
        ) {
            message
        }
    }
    ```

    Note if you have already used the ghost code to send a request you will have to
    request a new one even if you have not used the OTP correctly.

    >``Since this is a private mutation, the user must be authenticated to use it.
    See the [accounts](/accounts) page/ obtain access and refresh tokens mutation for
    more information.``
    """

    EXEMPT_CHECKS = True

    class Arguments:
        otp = graphene.String()
        ghost_code = graphene.String()

        initiate = graphene.Boolean()
        validate = graphene.Boolean()
        complete = graphene.Boolean()

    template = "EmailVerificationTemplate"

    def complete_mutation(cls, root, info, user, **inputs):
        user.is_email_verified = True
        user.save()
        return cls(message="email verified sucessfully")
