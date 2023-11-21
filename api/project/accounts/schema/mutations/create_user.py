"""
Mutation to create a new user, this is used in the accounts schema.
"""

# Native imports
from datetime import datetime, timedelta
import random

# Graphene imports
import graphene

# Django imports
from rest_framework_simplejwt.tokens import RefreshToken

# Local imports
from accounts.schema.types import UserType
from accounts.models import User, Referral, Referred
from utils.mutations.public import PublicMutation
from utils.errors import BadRequestError, ServerError


class CreateUser(PublicMutation):
    """
    # Creating a new user
    This mutation is used to create a new user. It takes in the following arguments:
    - email
    - dob
    - password

    Here is an example of how to use this mutation:

    ```
    mutation {
        createUser(email:"superuser@gmail.com", password:"superuser123", dob:"1999-01-01", referral:"<referral code> (optional))", isPoliciesAccepted:true/false) {
            message
            user{
                id
                email
            }
            accessToken
            refreshToken
        }
    }
    ```

    Access token and refresh token are generated when the user is created. It is needed
    to authenticate the user for future requests.

    To authenticate using access token, add the following to the request header:
    ```
    Authorization: JWT <access_token>
    ```

    After the user is created an One Time Password is sent to the user's email address. The user can then use
    the OTP to verify their email address and activate their account. This mutation is available in the /otp/
    endpoint.
    """
    user = graphene.Field(UserType)
    accessToken = graphene.String()
    refreshToken = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        dob = graphene.Date(required=True)
        password = graphene.String(required=True)
        is_policies_accepted = graphene.Boolean(required=True)
        referral = graphene.String(required=False)

    def mutate(self, info, email, password, dob, is_policies_accepted, referral=None):
        try:                                                                            
            if is_policies_accepted is False:
                raise BadRequestError("You must accept the user policies to proceed")
            
            if User.objects.filter(email=email).exists():
                raise BadRequestError('User already exists')

            # Check if the user is 18 years old
            if datetime.now().date() - dob < timedelta(days=6570):
                raise BadRequestError('User must be 18 years old')

            # Check if password is valid
            if len(password) < 8:
                raise BadRequestError(
                    'Password must be at least 8 characters long')

            if referral:
                if len(referral) >= 35:
                    raise BadRequestError('Referral code too long.')

                if not Referral.objects.filter(code=referral).exists():
                    raise BadRequestError('Invalid referral code.')

            user = User.objects.create_email_user(
                email=email,
                dob=dob,
                password=password
            )
            user.save()

            if referral is not None:
                Referred.objects.create(
                    user=user,
                    referral=Referral.objects.get(code=referral)
                )

            # Generate access and refresh tokens
            access_token, refresh_token = RefreshToken.for_user(
                user).access_token, RefreshToken.for_user(user)

            return CreateUser(user=user,  message='User created successfully', accessToken=str(access_token), refreshToken=str(refresh_token))
        except Exception as e:
            if not isinstance(e, (BadRequestError)):
                raise ServerError(str(e))
            else:
                raise e
