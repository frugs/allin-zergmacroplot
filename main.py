import io
import flask
import data
import storage.inmemorydatabase

database = storage.inmemorydatabase.InMemoryDatabase()

app = flask.Flask(__name__)


@app.route('/')
def index():
    return flask.render_template("index.html.j2")


@app.route("/upload", methods=["POST"])
def upload():
    if flask.request.files:
        file = next(flask.request.files.values(), None)
        replay_name = file.filename
        replay_data_stream = file.stream
    elif flask.request.data:
        replay_name = ""
        replay_data_stream = io.BytesIO(flask.request.data)
    else:
        return flask.abort(400)

    temp_file = storage.write_to_temporary_file(replay_data_stream)

    replay_id, replay_analysis = data.replay.analyse_replay_file(replay_name, temp_file)

    temp_file.close()

    database.add_document(replay_id, replay_analysis)

    return flask.redirect(replay_id)


@app.route("/<replay_id>")
def show_analysis(replay_id: str):
    analysis_data = database.get_document_as_str(replay_id)

    if analysis_data is None:
        return flask.abort(404)

    return flask.render_template("analysis.html.j2", analysis_data=analysis_data)


def main():
    app.run(host='127.0.0.1', port=32444, debug=True)


if __name__ == "__main__":
    main()
