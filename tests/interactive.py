from worker_object_server.object_server import ObjectServer
obj = ObjectServer()


def end():
    obj.stop()
    exit()
