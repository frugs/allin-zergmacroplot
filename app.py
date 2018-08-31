import asyncio

import aiohttp.web
import aiohttp_jinja2
import jinja2
import pkg_resources

import data
import storage.inmemorydatabase

database = storage.inmemorydatabase.InMemoryDatabase()


@aiohttp_jinja2.template('index.html.j2')
async def index(_: aiohttp.web.Request) -> dict:
    return {}


async def analyse_replay(request: aiohttp.web.Request) -> aiohttp.web.Response:
    if request.content_type.startswith("multipart/"):
        reader = await request.multipart()
        replay_data_stream = await reader.next()
        replay_name = replay_data_stream.filename
    else:
        replay_name = ""
        replay_data_stream = request.content

    if replay_data_stream is None:
        return aiohttp.web.HTTPClientError(body="Invalid Replay")

    temp_file = await storage.write_to_temporary_file(replay_data_stream)

    loop = asyncio.get_event_loop()

    replay_id, replay_analysis = await loop.run_in_executor(
        None, data.replay.analyse_replay_file, replay_name, temp_file)

    temp_file.close()

    await loop.run_in_executor(None, database.add_document, replay_id,
                               replay_analysis)

    return aiohttp.web.HTTPFound(replay_id)


@aiohttp_jinja2.template('analysis.html.j2')
async def show_analysis(request: aiohttp.web.Request) -> dict:
    replay_id = request.match_info['replay_id']
    analysis_data = await asyncio.get_event_loop().run_in_executor(
        None, database.get_document_as_str, replay_id)
    return {"analysis_data": analysis_data}


class App(aiohttp.web.Application):
    def __init__(self):
        super().__init__()

        aiohttp_jinja2.setup(
            self, loader=jinja2.FileSystemLoader('templates/'))

        self.router.add_get("/", index)
        self.router.add_get("/{replay_id}", show_analysis)
        self.router.add_post("/upload", analyse_replay)
        self.router.add_static('/static',
                               pkg_resources.resource_filename(
                                   __name__, "static"))


def main():
    aiohttp.web.run_app(App(), port=32433)


if __name__ == "__main__":
    main()
