"""
This module contains the public protected mutations for the project.

Protected mutation need authentication headers and a one time password
to be present to give any valid response. This is to prevent unauthorized 
and unauthenticated access to the mutation. Whereas public-protected mutations
do not need authentication headers to be present to give any valid response.
But requires a one time password to be present to give any valid response.
This is to verify that you are a valid user. For example, a mutation to
change the password of a user. This mutation does not need to be authenticated
because anyone can change the password of a user. But it requires a one time
password to be present to give any valid response. This is to verify that
you are a valid user.

Here is an example of how to use this class with a email validation mutation.

---------------------
Initiate the mutation
---------------------

mutation {
  forgotPassword(initate:true, email:"<email>") {
    message
  }
}

---------------------
Validate the mutation
---------------------

mutation {
  forgotPassword(validate:true, otp:"<otp from email>", email:"<email>") {
    message
    ghostCode
    otp
  }
}

---------------------
Validate the mutation with ghost code
---------------------

mutation {
  forgotPassword(complete:true, otp:"$otp", ghostCode:"$ghostCode") {
    message
  }
}


"""

# Django imports
from graphene import String, Boolean as Bool

# Local imports
from utils.mutations.public import PublicMutation
from otp.models import OneTimePassword, validateActionWithGhostCode, validateUserWithOTP
from accounts.models import User
from utils.errors import BadRequestError, ServerError
from aws.models import SESEmailTemplate


class PublicProtectedMutation(PublicMutation):
    """
    This class is the base class for all public protected mutations.
    """
    class Meta:
        abstract = True

    email = String(required=True)

    initiate = Bool()
    validate = Bool()
    complete = Bool()

    otp = String()
    ghost_code = String()

    @classmethod
    def mutate(cls, root, info, **inputs):
        """
        This is used to check what all inputs are present and then call the
        appropriate method to perform the mutation.

        If the initiate flag is present, the initiate_mutation method is called.
        If the validate flag is present, the validate_mutation method is called.
        If the complete flag is present, the complete_mutation method is called.
        else, error is raised.
        """
        # check if the email is present
        email = inputs.get('email')
        if not email:
            raise BadRequestError("Invalid request, email is required")

        # check if the user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise BadRequestError("Invalid request, user does not exist")

        try:
            initiate = inputs.get('initiate')
            validate = inputs.get('validate')
            complete = inputs.get('complete')

            # only one of the flags can be present and
            # the other two must be absent.
            if (initiate and validate) or (initiate and complete) or (validate and complete):
                raise BadRequestError(
                    "Invalid request, only one of the flags can be present")

            if initiate:
                return cls.__initiate_mutation(cls, root, info, user, **inputs)
            elif validate:
                return cls.__validate_mutation(cls, root, info, user, **inputs)
            elif complete:
                return cls.__complete_mutation(cls, root, info, user, **inputs)

        except Exception as e:
            if not isinstance(e, BadRequestError):
                raise ServerError(str(e))
            else:
                raise e

    def __initiate_mutation(cls, root, info, user, **inputs):
        """
        This method is called when the initiate flag is present.

        This method will create a new otp with purpose VALIDATION and
        send an email to the user with the otp.
        """
        try:

            # Check if a purpose is set when this class is extended if not
            # use VALIDATION as the default purpose
            template = getattr(cls, 'template', "ForgotPasswordTemplate")

            OneTimePassword.objects.create(
                user=user,
                email_template=SESEmailTemplate.objects.get(
                    template_identifier=template),
            )
            return cls(message="OTP sent to your email.")

        except Exception as e:
            if not isinstance(e, BadRequestError):
                raise ServerError(str(e))
            else:
                raise e

    def __validate_mutation(cls, root, info, user, **inputs):
        """
        This method is called when the validate flag is present.

        This method will validate the otp and return the ghost code if
        the otp is valid.
        """
        try:

            # Check if a purpose is set when this class is extended if not
            # use VALIDATION as the default purpose
            template = getattr(cls, 'template', "ForgotPasswordTemplate")

            otp = inputs.get('otp')

            # Check if the otp is present
            if not otp:
                raise BadRequestError("OTP is required to validate.")

            # Run the validateUserWithOTP method to validate the otp
            validation, ghost_code, otp_obj = validateUserWithOTP(
                code=otp, user_id=user.id, template=SESEmailTemplate.objects.get(
                    template_identifier=template)
            )

            # If the validation was successful, return the ghost code
            if validation:
                return cls(message="OTP validated.", ghost_code=ghost_code, otp=str(otp_obj.id))
            else:
                raise BadRequestError("Invalid OTP.")

        except Exception as e:
            if not isinstance(e, BadRequestError):
                raise ServerError(str(e))
            else:
                raise e

    def __complete_mutation(cls, root, info, user, **inputs):
        """
        This method is called when the complete flag is present.

        This method will validate the ghost code and return the 
        response if the ghost code is valid.
        """
        try:

            # Check if a purpose is set when this class is extended if not
            # use VALIDATION as the default purpose
            otp = inputs.get('otp')
            ghost_code = inputs.get('ghost_code')

            # Check if the ghost code is present
            if not ghost_code and not otp:
                raise BadRequestError("Ghost code is required to complete.")

            # Get the otp object
            try:
                otp_obj = OneTimePassword.objects.get(id=otp)
            except OneTimePassword.DoesNotExist:
                raise BadRequestError("Invalid OTP.")

            # Run the validateActionWithGhostCode method to validate the ghost code
            validation = validateActionWithGhostCode(
                ghost_code=ghost_code, otp=otp_obj)

            # If the validation was successful, return the response
            if validation:
                return cls.complete_mutation(cls, root, info, user, **inputs)
            else:
                raise BadRequestError("Invalid ghost code.")

        except Exception as e:
            if not isinstance(e, BadRequestError):
                raise ServerError(str(e))
            else:
                raise e

    def complete_mutation(cls, root, info, user, **inputs):
        """
        This method is called when the complete_mutation method is called.

        This method must be implemented in the class which extends this class.
        """
        raise NotImplementedError(
            "complete_mutation method must be implemented.")
