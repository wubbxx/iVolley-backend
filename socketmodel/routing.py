from django.urls import path

from socketmodel.consumer import ChatConsumer

websocket_urlpatterns = [
    path('chat/', ChatConsumer.as_asgi())
]