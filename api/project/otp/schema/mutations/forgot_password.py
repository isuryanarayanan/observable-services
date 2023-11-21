"""
Mutation to reset a forgotten password with user email and otp.
"""

# Native imports
from datetime import datetime, timedelta

# Graphene imports
import graphene
from graphql import GraphQLError

# Local imports
from accounts.models import User
from utils.mutations.public_protected import PublicProtectedMutation
from utils.errors import BadRequestError
from aws.models import SESEmailTemplate


class ForgotPassword(PublicProtectedMutation):
    """
    # Forgot password mutation

    This mutation is used to reset a forgotten password.
    It uses the OTP system to verify the user. There are three steps to this mutation.

    1. The user provides the email and initiates the mutation that sends the OTP.
    2. The OTP is then verified by the user in exchange for a ghost code and the OTP id.
    3. The user provides the OTP id and ghost code to complete the mutation.

    ## Steps

    1. The user provides the email and initiates the mutation.

        ```graphql
        mutation {
            forgotPassword(
                email: "<email>",
                initiate: true
            ) {
                message
            }
        }
        ```
    2. The OTP is sent to the user's email and validated.

        ```graphql
        mutation {
            forgotPassword(
                email: "<email>",
                validate: true,
                otp: "<otp>"
            ) {
                message
                otp
                ghostCode
            }
        }
        ```

    3. The user provides the OTP and ghostcode and completes the mutation.

        Keep in mind the OTP in this step is the otp id and not the otp code.

        ```graphql
        mutation {
            forgotPassword(
                email: "<email>",
                complete: true,
                otp: "<otp>",
                ghostCode: "<ghostCode>",
                newPassword: "<newPassword>"
            ) {
                message
            }
        }
        ```


    Ghost code is a unique code that is generated for each OTP. It is used to identify the OTP.
    It is not stored in the database. It is generated using the OTP id and the user's email.
    It is used to identify the OTP in the `PublicProtectedMutation` class.

    """

    class Arguments:
        email = graphene.String(required=True)
        new_password = graphene.String()

        otp = graphene.String()
        ghost_code = graphene.String()

        initiate = graphene.Boolean()
        validate = graphene.Boolean()
        complete = graphene.Boolean()

    template = "ForgotPasswordTemplate"

    def complete_mutation(cls, root, info, user, **inputs):

        # Check if new password is provided
        if not inputs.get('new_password'):
            raise BadRequestError("New password is required")

        # Check if new password is a valid password
        if not User.is_valid_password(inputs.get('new_password')):
            raise BadRequestError("Invalid password")

        # Set new password
        user.set_password(inputs.get('new_password'))
        user.save()

        return cls(message="Password changed successfully")
