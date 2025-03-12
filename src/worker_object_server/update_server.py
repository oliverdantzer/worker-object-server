from __future__ import annotations

import asyncio
import threading
from typing import Any, Callable, Set

from pydantic import ValidationError
from websockets.asyncio.server import ServerConnection, serve
from websockets.exceptions import ConnectionClosed

from .update import Position, Update, UpdatePacket

from datetime import datetime


class UpdateServer:
    update_queue: asyncio.Queue[UpdatePacket]
    handle_incoming_update: Callable[[Update], None]
    stop_event: asyncio.Event

    def __init__(
        self,
        get_at_position: Callable[[Position], Any],
        handle_incoming_update: Callable[[Update], None],
    ):
        self.port = 8765

        self.connections: Set[ServerConnection] = set()

        self.get_at_position = get_at_position
        self.handle_incoming_update = handle_incoming_update

        self.lock = threading.Lock()
        self.initialized_event = threading.Event()
        self.loop = asyncio.get_event_loop()

    async def handle_recieve(self, websocket):
        if websocket not in self.connections:
            self.connections.add(websocket)

        root_position = Position([])
        root_value = self.get_at_position(root_position)
        root_update = Update(timestamp=datetime.now(),
                             position=root_position, data=root_value)
        root_update_packet = UpdatePacket.from_update(root_update)
        await websocket.send(root_update_packet.json())

        try:
            while True:
                data = await websocket.recv()
                try:
                    update_pkt = UpdatePacket.from_json(data)
                    update = UpdatePacket.to_update(update_pkt)
                    self.handle_incoming_update(update)
                except ValidationError:
                    continue
        except asyncio.CancelledError:
            pass
        except ConnectionClosed as e:
            pass
            # if e.code == 1001:
            #     print(
            #         f"Connection closed (going away): {websocket.remote_address}")
            # else:
            #     print(f"Connection closed with code {e.code}: {e.reason}")
        except Exception as e:
            print(f"Error in handle_recieve: {e}")
        finally:
            if websocket in self.connections:
                self.connections.remove(websocket)

    async def start_recieve(self):
        async with serve(self.handle_recieve, "localhost", self.port) as server:
            await self.stop_event.wait()
            for websocket in self.connections:
                await websocket.close()
            self.connections.clear()
            server.close()

    def add_update(self, update: Update):
        print("Adding update to queue")
        json_update = UpdatePacket.from_update(update)
        self.update_queue.put_nowait(json_update)

    async def start_send(self):
        while not self.stop_event.is_set():
            try:
                update = await asyncio.wait_for(self.update_queue.get(), timeout=0.1)
                print("sending update", update)
                assert isinstance(update, UpdatePacket)
                for websocket in self.connections:
                    await websocket.send(update.json())
                    print(
                        f"Sent update to {websocket.remote_address}: {update.json()}")
            except asyncio.TimeoutError:
                pass

    def start_threaded(self) -> threading.Thread:
        thread = threading.Thread(
            target=self.loop.run_until_complete, args=(self._start_all(),))
        thread.start()
        self.initialized_event.wait()  # Wait for the update queue to be initialized
        return thread

    async def _start_all(self):
        self.update_queue = asyncio.Queue()
        self.stop_event = asyncio.Event()
        self.initialized_event.set()
        try:
            await asyncio.gather(self.start_recieve(), self.start_send())
        except Exception as e:
            print(f"Error in _start_all: {e}")

    def shutdown(self):
        self.stop_event.set()
