import asyncio
from websockets.asyncio.server import serve, ServerConnection
from pydantic import ValidationError
from .update import UpdatePacket, Position, Update
import threading
from typing import Callable, Any, Set


class UpdateServer:
    update_event: 'asyncio.Event | None'
    update_queue: 'asyncio.Queue[UpdatePacket] | None'
    handle_incoming_update: Callable[[UpdatePacket], None]

    def __init__(self, get_at_position: Callable[[Position], Any], handle_incoming_update: Callable[[UpdatePacket], None]):
        self.port = 8765

        self.connections: Set[ServerConnection] = set()

        self.get_at_position = get_at_position
        self.handle_incoming_update = handle_incoming_update

        self.update_event = None
        self.update_queue = None
        self.lock = threading.Lock()

    # send update of entire self.data to websocket
    # async def update_full(self, websocket):
    #     update = common.Update(time.time(), common.Position(), self.data)
    #     update = common.JsonUpdate.from_update(update)
    #     websocket.send(common.build_update_packet(update))

    async def handle_recieve(self, websocket):
        if websocket not in self.connections:
            self.connections.add(websocket)
            # await self.update_full(websocket)
        else:
            data = await websocket.recv()
            try:
                update = UpdatePacket.model_validate_json(data)
                self.handle_incoming_update(update)
            except ValidationError:
                return

    async def start_recieve(self):
        async with serve(self.handle_recieve, "localhost", self.port) as server:
            await server.serve_forever()  # run forever

    # add update to queue
    def add_update(self, update: Update):
        if self.update_queue is None:
            raise ValueError(
                "update queue not instantiated, call add_update after asyncio.run")

        json_update = UpdatePacket.from_update(update)
        self.update_queue.put_nowait(json_update)

    # infinitely send updates added to queues
    async def start_send(self):
        assert self.update_queue is not None
        while True:
            update = await self.update_queue.get()
            for websocket in self.connections:
                await websocket.send(update.json())

    def start_blocking(self):
        asyncio.run(self._start_all())

    async def _start_all(self):

        await asyncio.gather(self.start_recieve(), self.start_send())


if __name__ == "__main__":
    retry = UpdateServer(lambda position: 10, lambda update: print(update))
    retry.start_blocking()
