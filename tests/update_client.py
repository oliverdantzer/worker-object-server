import json
import asyncio
from websockets.asyncio.client import connect, ClientConnection
import time
import queue
import common
import threading

# self.jsonFile = jsonFile
#         try:
#             with open(self.jsonFile, "r") as file:
#                 self.data = json.load(file)
#         except FileNotFoundError:
#             raise FileNotFoundError(f"{self.jsonFile} not found")


# class RefDict:
#     def __init__(self, data: dict):
#         self.data = data

class ConnectorClient:
    update_event: asyncio.Event
    update_queue: 'queue.Queue[common.JsonUpdate]'

    def __init__(self, data: dict):
        self.data = data

        self.update_event = asyncio.Event()
        self.update_queue = queue.Queue()
        self.lock = threading.Lock()

    async def start_recieve(self, websocket):
        while True:
            data = await websocket.recv()
            data = json.loads(data)
            if data["type"] == "update":
                update = common.Update(data["timestamp"], common.Position.from_str(
                    data["position"]), data["data"])
                self.handle_incoming_update(update)

    async def start(self):
        async with connect("ws://localhost:8765") as websocket:
            print("server connection established")
            await asyncio.gather(self.start_recieve(websocket), self.start_send(websocket))

    def handle_incoming_update(self, update: common.Update):
        common.update_dict(self.data, update)
        json_update = common.JsonUpdate.from_update(update)

    # add update to queue
    def add_update(self, update: common.Update):
        # update data
        common.update_dict(self.data, update)

        json_update = common.JsonUpdate.from_update(update)
        with self.lock:
            self.update_queue.put(json_update)
            self.update_event.set()

    def get_value(self, position: common.Position):
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

                await websocket.send(common.build_update_packet(update))

                # write to json file
                with open("data.json", "w") as file:
                    json.dump(self.data, file)

    def start_threading(self):
        def run():
            asyncio.run(self.start())

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    client = ConnectorClient({})
    client.start_threading()
