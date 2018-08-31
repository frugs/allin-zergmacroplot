import asyncio
import tempfile

CHUNK_SIZE = 1024


async def write_to_temporary_file(data_stream):
    replay_file = tempfile.TemporaryFile()
    loop = asyncio.get_event_loop()

    while True:
        chunk = await data_stream.read()
        if not chunk:
            break

        await loop.run_in_executor(None, replay_file.write, chunk)

    await loop.run_in_executor(None, replay_file.seek, 0)
    return replay_file
