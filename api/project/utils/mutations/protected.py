"""
This module contains the protected mutations for the project.

Protected mutation need authentication headers and a one time password
to be present to give any valid response. This is to prevent unauthorized 
and unauthenticated access to the mutation.

Here is an example of how to use this class with a email validation mutation.

---------------------
Initiate the mutation
---------------------

mutation {
  validateEmail(initate:true) {
    message
    status
  }
}

---------------------
Validate the mutation
---------------------

mutation {
  validateEmail(validate:true, otp:"<otp from email>") {
    message
    status
    ghostCode
    otp
  }
}

---------------------
Validate the mutation with ghost code
---------------------

mutation {
  validateEmail(complete:true, otp:"$otp", ghostCode:"$ghostCode") {
    message
    status
  }
}


"""

# Django imports
from graphene import String, Boolean as Bool

# Local imports
from utils.mutations.private import PrivateMutation
from otp.models import OneTimePassword, validateActionWithGhostCode, validateUserWithOTP
from aws.models import SESEmailTemplate
from utils.errors import BadRequestError, ServerError


class ProtectedMutation(PrivateMutation):
    """
    This class is the base class for all protected mutations.

    It is used to check if the user is authenticated and there is an 
    otp present which is valid before performing the mutation. 
    If the user is not authenticated, a PermissionDenied exception is raised.
    """
    class Meta:
        abstract = True

    initiate = Bool()
    validate = Bool()
    complete = Bool()

    otp = String()
    ghost_code = String()

    @classmethod
    def perform_mutation(cls, root, info, user, **inputs):
        """
        This method is called when the mutation is called.

        It is used to check what all inputs are present and then call the
        appropriate method to perform the mutation.

        If the initiate flag is present, the initiate_mutation method is called.
        If the validate flag is present, the validate_mutation method is called.
        If the complete flag is present, the complete_mutation method is called.
        else, error is raised.
        """

        try:

            initiate = inputs.get('initiate')
            validate = inputs.get('validate')
            complete = inputs.get('complete')

            # only one of the flags can be present and
            # the other two must be absent.
            if (initiate and validate) or (initiate and complete) or (validate and complete):
                raise BadRequestError(
                    message="Invalid request, only one mode should be active. Either initiate, validate or complete")

            if initiate:
                return cls.__initiate_mutation(cls, root, info, user, **inputs)
            elif validate:
                return cls.__validate_mutation(cls, root, info, user, **inputs)
            elif complete:
                return cls.__complete_mutation(cls, root, info, user, **inputs)

        except Exception as e:
            if not isinstance(e, BadRequestError):
                raise ServerError(message=str(e))
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
            template = getattr(
                cls, 'template', "EmailVerificationTemplate")

            OneTimePassword.objects.create(
                user=user,
                email_template=SESEmailTemplate.objects.get(
                    template_identifier=template),
            )

            return cls(message="OTP sent to your email.")
        except Exception as e:
            if not isinstance(e, BadRequestError):
                raise ServerError(message=str(e))
            else:
                raise e

    def __validate_mutation(cls, root, info, user, **inputs):
        """
        This method is called when the validate flag is present.

        This method will validate the otp and return the ghost code if
        the otp is valid.
        """
        try:

            # Check if a is set when this class is extended if not
            # use VALIDATION as the default purpose
            template = getattr(cls, 'template', "EmailVerificationTemplate"
                               )

            otp = inputs.get('otp')

            # Check if the otp is present
            if not otp:
                raise BadRequestError(message="OTP is required.")

            # Run the validateUserWithOTP method to validate the otp
            validation, ghost_code, otp_obj = validateUserWithOTP(
                code=otp, user_id=user.id, template=SESEmailTemplate.objects.get(
                    template_identifier=template)
            )

            # If the validation was successful, return the ghost code
            if validation:
                return cls(message="OTP validated.", ghost_code=ghost_code, otp=str(otp_obj.id))
            else:
                raise BadRequestError(message="Invalid OTP.")

        except Exception as e:
            if not isinstance(e, BadRequestError):
                raise ServerError(message=str(e))
            else:
                raise e

    def __complete_mutation(cls, root, info, user, **inputs):
        """
        This method is called when the complete flag is present.

        This method will validate the ghost code and return the 
        response if the ghost code is valid.
        """
        try:

            otp = inputs.get('otp')
            ghost_code = inputs.get('ghost_code')

            # Check if the ghost code is present
            if not ghost_code and not otp:
                raise BadRequestError(
                    message="Ghost code and OTP are required.")

            # Get the otp object
            try:
                otp_obj = OneTimePassword.objects.get(id=otp)
            except OneTimePassword.DoesNotExist:
                raise BadRequestError(message="Invalid OTP.")

            # Run the validateActionWithGhostCode method to validate the ghost code
            validation = validateActionWithGhostCode(
                ghost_code=ghost_code, otp=otp_obj)

            # If the validation was successful, return the response
            if validation:
                return cls.complete_mutation(cls, root, info, user, **inputs)
            else:
                raise BadRequestError(message="Invalid ghost code.")

        except Exception as e:
            if not isinstance(e, BadRequestError):
                raise ServerError(message=str(e))
            else:
                raise e

    def complete_mutation(cls, root, info, user, **inputs):
        """
        This method is called when the complete_mutation method is called.

        This method must be implemented in the class which extends this class.
        """
        raise NotImplementedError(
            "complete_mutation method must be implemented.")
