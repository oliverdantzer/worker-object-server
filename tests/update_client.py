import json
import asyncio
from websockets.asyncio.client import connect, ClientConnection
import time
import queue
from worker_object_server.update import UpdatePacket, update_dict, Position
import threading


class UpdateClient:
    update_event: asyncio.Event
    update_queue: 'queue.Queue[UpdatePacket]'

    def __init__(self, data: dict):
        self.data = data

        self.update_event = asyncio.Event()
        self.update_queue = queue.Queue()
        self.lock = threading.Lock()

    async def start_recieve(self, websocket):
        while True:
            data = await websocket.recv()
            self.handle_incoming_update(
                UpdatePacket.from_json_str(data.decode()))

    async def start(self):
        async with connect("ws://localhost:8765") as websocket:
            print("server connection established")
            await asyncio.gather(self.start_recieve(websocket), self.start_send(websocket))

    def handle_incoming_update(self, update: UpdatePacket):
        update_dict(self.data, update)

    # add update to queue
    def add_update(self, update: UpdatePacket):
        # update data
        update_dict(self.data, update)
        
        with self.lock:
            self.update_queue.put(update)
            self.update_event.set()

    def get_value(self, position: Position):
        current = self.data
        for key in position.position:
            current = current[key]
        return current

    # infinitely send updates added to queues
    async def start_send(self, websocket):
        while True:
            await self.update_event.wait()
            with self.lock:
                # if self.update_queue.empty():
                #     self.update_event.clear()
                #     continue
                update = self.update_queue.get()
                if self.update_queue.empty():
                    self.update_event.clear()

                await websocket.send(update.json())

    def start_threading(self):
        def run():
            asyncio.run(self.start())

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    client = UpdateClient({})
    client.start_threading()
