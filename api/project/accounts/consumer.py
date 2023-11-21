"""
consumer for accont app
"""

# Django imports
from channels.layers import get_channel_layer
import json


from utils.errors import BaseWSException

class AccountsConsumer():
    async def accounts_init(self,variable, code):
        print(variable)
        channel_layer = get_channel_layer()


        try:
            try:
                message = variable[0]
            except IndexError as e:
                raise BaseWSException("Invalid variablesss")

            try:
                # Send pong to the user channel layer
                await channel_layer.group_send(
                    f"user_{self.user.id}",
                    {
                        'type':'init',
                        'message':"pong",
                        'data':None
                    }
                )
            except Exception as e:
                raise BaseWSException(str(e))
            
        except BaseWSException as e:
            # Send message to the users channel layer
            await channel_layer.group_send(
            f"user_{self.user.id}",
                {
                    'type':'init',
                    'message': str(e)
                }
            )
            raise BaseWSException(str(e))