"""
Schema for the otp app
"""

# Graphene imports
import graphene

# Mutations
from otp.schema.mutations.verify_email import ValidateEmail
from otp.schema.mutations.forgot_password import ForgotPassword

# Logger
from logs.config import config as logger_config
from logs.logger_templates import error_log,log
import logging

# Debugger
import pudb

logging.config.dictConfig(logger_config)
logger = logging.getLogger(__name__)


class Query(graphene.ObjectType):
    hello = graphene.String(description="A simple greeting")

    def resolve_hello(self, info):
        # pudb.set_trace()
        log(logger, 'info', {'message': 'Hello world!', 'description': 'A simple greeting', 'api': 'hello', 'user': 'anonymous'})
        return "Hello, world!"


class Mutation(graphene.ObjectType):
    """
    # OTP mutations
    - `validateEmail` - Validate an email
    - `forgotPassword` - Reset a forgotten password
    """
    validate_email = ValidateEmail.Field()
    forgot_password = ForgotPassword.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
