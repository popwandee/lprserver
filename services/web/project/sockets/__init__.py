# sockets/__init__.py
from flask_socketio import Namespace

from .lpr_events import LPRNamespace
from .chat_events import ChatNamespace
from .edge_events import EdgeNamespace

def register_socketio_namespaces(socketio):
    socketio.on_namespace(LPRNamespace('/lpr'))
    socketio.on_namespace(ChatNamespace('/chat'))
    socketio.on_namespace(EdgeNamespace('/edge'))
