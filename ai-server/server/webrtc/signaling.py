import asyncio

from aiortc import RTCPeerConnection


async def wait_for_ice_gathering(pc: RTCPeerConnection) -> None:
    if pc.iceGatheringState == "complete":
        return

    completed = asyncio.Event()

    @pc.on("icegatheringstatechange")
    async def on_ice_gathering_state_change() -> None:
        if pc.iceGatheringState == "complete":
            completed.set()

    await completed.wait()
