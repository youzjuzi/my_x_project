import asyncio

from ..scenes import BaseSession


async def receive_video_track(track, session: BaseSession) -> None:
    try:
        while True:
            frame = await track.recv()
            await session.publish_frame(frame)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        await session.send_json({"type": "error", "message": str(exc)})
