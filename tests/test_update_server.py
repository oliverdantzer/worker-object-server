from datetime import datetime

from worker_object_server.update import Position, Update
from worker_object_server.update_server import UpdateServer
import asyncio


def get_at_position(position):
    return "hello"


def handle_incoming_update(update):
    print(update)


update_server = UpdateServer(get_at_position, handle_incoming_update)
thread = update_server.start_threaded()

while True:
    update_str = input("> ")
    if update_str == "exit":
        break
    position = Position([])
    update = Update(timestamp=datetime.now(),
                    position=position, data=update_str)
    update_server.add_update(update)

update_server.shutdown()
thread.join()
