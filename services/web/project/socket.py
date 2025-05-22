class AdminNamespace(Namespace):
    def on_connect(self):
        print("Admin connected")

    def on_disconnect(self):
        print("Admin disconnected")

socketio.on_namespace(AdminNamespace("/admin"))