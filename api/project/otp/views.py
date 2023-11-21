"""
This file contains the views for the otp app.
"""

# Django imports
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from otp.schema.schema import schema
from utils.views import GraphQLRespondView


@csrf_exempt
def otp_graphql_view(request):
    return GraphQLRespondView.as_view(graphiql=True, schema=schema)(request)
