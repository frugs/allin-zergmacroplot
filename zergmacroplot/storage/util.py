import tempfile

CHUNK_SIZE = 1024


def write_to_temporary_file(data_stream):
    replay_file = tempfile.TemporaryFile()

    while True:
        chunk = data_stream.read()
        if not chunk:
            break

        replay_file.write(chunk)

    replay_file.seek(0)
    return replay_file
