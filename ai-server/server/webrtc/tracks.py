import asyncio

from .session import SessionState


async def receive_video_track(track, session: SessionState) -> None:
    try:
        while True:
            frame = await track.recv()
            await session.publish_frame(frame)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        await session.send_json({"type": "error", "message": str(exc)})
