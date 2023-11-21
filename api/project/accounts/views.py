"""
This file contains the views for the accounts app.
"""

# Native imports
import json

# Django imports
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Graphene imports
from accounts.schema.schema import schema

# Local imports
from utils.views import GraphQLRespondView


@csrf_exempt
def accounts_graphql_view(request):
    # Use extended view
    return GraphQLRespondView.as_view(graphiql=True, schema=schema)(request)
