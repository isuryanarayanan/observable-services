"""
Extending the graphene GraphQLView to add custom headers to the response
"""

from graphene_django.views import GraphQLView
import json


class GraphQLRespondView(GraphQLView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if request.method == 'POST':
            # Parse the http response and check for errors
            response_data = json.loads(response.content)
            response_statuses = []

            # If errors array exist get the length and loop through it
            if 'errors' in response_data:
                errors = response_data['errors']
                errors_length = len(errors)
                for i in range(errors_length):
                    # Check if the extensions key exists
                    if 'extensions' in errors[i]:
                        # Check if the status key exists
                        if 'status' in errors[i]['extensions']:
                            # Append the status code to the array
                            response_statuses.append(
                                errors[i]['extensions']['status'])

            # Set the response.status_code to the highest status code in the array
            if response_statuses:
                response.status_code = max(response_statuses)

        return response
