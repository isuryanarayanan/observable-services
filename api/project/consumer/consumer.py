"""
Consumer for websocket connections.

Here is how to work with this consumer:
1. Create a connection with the server by sending a token and a query.
2. The server will check the token and the query.
3. If the token is valid and the query is valid, the server will add the connection to the user's group.
4. The server will then call the method with the name of the app and the operation.
5. The method will then reply to the client.

Define your app consumers and inherit that class here.
"""

# Native imports
import json

# Django imports
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.http import HttpRequest
from asgiref.sync import sync_to_async

# Local imports
from .models import Connection
from utils.errors import BaseWSException

# Consumers
from accounts.consumer import AccountsConsumer


class BaseConsumer(AsyncWebsocketConsumer, AccountsConsumer):
    """
    Base consumer for websocket connections

    This consumer is the base consumer for all websocket connections.
    It handles the authentication and the query checks.
    It also handles the reply to the client.
    """

    def init_query_checks(self, query):
        """
        Initialize query checks, will raise exception if 
        the query is invalid. or if the operation is invalid.
        """
        try:

            if not query:
                raise BaseWSException(message='Query not found')

            app = query.get('app', None)
            operation = query.get('operation', None)
            code = query.get('code', None)

            if not code:
                raise BaseWSException(message='Code not found')

            if not app:
                raise BaseWSException(message='App not found')

            if not operation:
                raise BaseWSException(message='Operation not found')

            if not hasattr(self, f'{app}_{operation}'):
                raise BaseWSException(message='Invalid operation')

            self.passed_query_checks = True

        except BaseWSException as e:
            self.passed_query_checks = False
            raise BaseWSException(message=str(e))

    async def init_layer_checks(self, user):
        """
        Initialize layer checks

        This method will add the connection to the user's group.
        """

        user = self.user

        try:

            await self.channel_layer.group_add(
                f'user_{user.id}',
                self.channel_name
            )
            
            await self.channel_layer.group_add(
                f'broadcast',
                self.channel_name
            )


            self.passed_layer_checks = True

        except Exception as e:

            self.passed_layer_checks = False
            raise BaseWSException(message=str(e))

    async def init_auth_checks(self, token, client):
        """
        Initialize authentication checks.

        This method will check if the token is valid.
        If the token is valid, it will create a connection for the user.
        """

        try:
            request = HttpRequest()
            request.META['HTTP_AUTHORIZATION'] = f'{token}'

            authenticateJWT = sync_to_async(
                JWTAuthentication().authenticate)

            self.user, _ = await authenticateJWT(request)

            self.connection, _ = await database_sync_to_async(Connection.objects.get_or_create)(
                client=client,
                user=self.user
            )
            self.passed_auth_checks = True

        except Exception as e:
            self.passed_auth_checks = False
            if isinstance(e, Connection.DoesNotExist):
                raise BaseWSException(message='Unable to create connection')
            else:
                raise BaseWSException(message="Invalid token")
    
    async def init(self, ping):
        """
        To initialize the connection.
        """

        try:
            await self.send(text_data=json.dumps(ping))
        except Exception as e:
            raise BaseWSException(message=str(e))

    async def broadcast(self, event):
        """
        Broadcast method.

        This method will be called when the server sends a broadcast to the client.
        """

        BROADCAST_FORMATS = {
            'broadcast': {
                'type': None,
                'broadcast': {
                    'id': None,
                    'title': None,
                    'url': None,
                    'time': None,
                    'description': None,
                    'thumbnail': None,
                    'is_live': None,
                    'scheduled_time': None,
                    'viewers': None
                }
            }
        }


        if event.get('message', None):
            broadcast = BROADCAST_FORMATS['broadcast']
            broadcast['type'] = event['message'].get('type', None)
            broadcast['broadcast']['id'] = event['message']['broadcast'].get('id', None)
            broadcast['broadcast']['title'] = event['message']['broadcast'].get('title', None)
            broadcast['broadcast']['url'] = event['message']['broadcast'].get('url', None)
            broadcast['broadcast']['time'] = event['message']['broadcast'].get('time', None)
            broadcast['broadcast']['description'] = event['message']['broadcast'].get('description', None)
            broadcast['broadcast']['thumbnail'] = event['message']['broadcast'].get('thumbnail', None)
            broadcast['broadcast']['is_live'] = event['message']['broadcast'].get('is_live', None)
            broadcast['broadcast']['scheduled_time'] = event['message']['broadcast'].get('scheduled_time', None)
            broadcast['broadcast']['viewers'] = event['message']['broadcast'].get('viewers', None)
        
        try:
            await self.send(text_data = json.dumps(broadcast))
        except Exception as e:
            raise BaseWSException(message=str(e))

    async def notification(self, notification):
        """
        Notification method.

        This method will be called when the server sends a notification to the client.
        """
        NOTIFICATION_FORMATS = {
            'notification':{
                'type':None,
                'action':None,
                'content':None,
                'from_user':None,
                'to_user':None,
                'timestamp':None,
                'data':{
                    'post':None,
                    'comment':None
                }
            }
           
        }

        if notification.get('data',None):
            notify = NOTIFICATION_FORMATS['notification']
            notify['type'] = notification['data'].get('type',None)

            # notify['data'] = notification['data'].get('post', notification['data'].get('comment', {}))
            notify['data']['post']=notification['data'].get('post',None)
            notify['data']['comment']=notification['data'].get('comment',None)
            notify['action'] = notification['data'].get('action',None)
            notify['content'] = notification['data'].get('content',None)
            notify['from_user'] = notification['data'].get('from_user',None)
            notify['to_user'] = notification['data'].get('to_user',None)
            notify['timestamp'] = notification['data'].get('timestamp',None)
        
        try:
            await self.send(text_data = json.dumps(notify))
        except Exception as e:
            raise BaseWSException(message=str(e))
        

    async def reply(self, response):
        """
        Reply to the client.

        This method will reply to the client with the response.
        There are two types of responses:
        1. Success
        2. Error
        """

        REPLY_FORMATS = {
            'success': {
                'code': 'unique_code',
                'status': 'success',
                'message': 'Success',
                'data': None
            },
            'error': {
                'code': 'unique_code',
                'status': 'error',
                'message': None
            }
        }

        if response.get('status', None) == 'success':
            reply = REPLY_FORMATS['success']

            if response.get('message', None):
                reply['message'] = response.get('message', None)

            reply['data'] = response.get('data', None)
            reply['code'] = response.get('code', None)

        elif response.get('status', None) == 'error':
            reply = REPLY_FORMATS['error']

            reply['code'] = response.get('code', None)
            reply['message'] = response.get('message', None)

        else:
            reply = REPLY_FORMATS['error']
            reply['message'] = 'Invalid response format'

        try:
            await self.send(text_data=json.dumps(reply))
        except Exception as e:
            raise BaseWSException(message=str(e))

    async def connect(self):
        """
        Connect to the server.

        This method will be called when the client connects to the server.
        It will initialize the connection and the checks.
        """

        self.connection = None
        self.user = None
        self.passed_layer_checks = False
        self.passed_auth_checks = False
        self.passed_query_checks = False
        await self.accept()

    async def disconnect(self, close_code):
        try:
            await database_sync_to_async(self.connection.delete)()
            self.connection = None
            self.user = None
            self.passed_layer_checks = False
            self.passed_auth_checks = False
            self.passed_query_checks = False
        except Exception as e:
            pass

    async def receive(self, text_data):
        """
        Receive data from the client.

        This method will be called when the client sends data to the server.
        It will initialize the query checks and the reply to the client, 
        based on the query they passed.

        The query should be in the following format:
        {
            'app': 'app_name',
            'code': 'unique_code',
            'operation': 'operation_name',
            'variables': {
                'variable_name': 'variable_value'
            }
        }
        """

        text_data_json = json.loads(text_data)

        client = self.scope['client'][0]
        token = text_data_json.get('token', None)
        query = text_data_json.get('query', None)
        query_app = query.get('app', None)
        query_code = query.get('code', None)
        query_operation = query.get('operation', None)
        query_variables = query.get('variables', None)

        try:
            await self.init_auth_checks(token, client)
            await self.init_layer_checks(self.user)
            self.init_query_checks(query)
        except BaseWSException as e:
            await self.reply({
                'status': 'error',
                'code': query_code,
                'message': str(e),
                'data': None
            })

        try:

            if self.passed_auth_checks and self.passed_layer_checks and self.passed_query_checks:
                # If all checks have passed the query is executed by calling
                # the operation which should be available from the class that
                # inherits this class.
                method = getattr(self, f'{query_app}_{query_operation}')
                await method(query_variables, query_code)

        except BaseWSException as e:
            await self.reply({
                'status': 'error',
                'code': query_code,
                'message': str(e),
                'data': None
            })
