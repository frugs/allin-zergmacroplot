import io

import flask

import data
import storage

ROOT_PATH = "/zergmacro/"

app = flask.Flask(__name__, static_url_path=ROOT_PATH + "static")

if __name__ == "__main__":
    # Assume we're running locally
    import storage.inmemorydatabase
    database = storage.inmemorydatabase.InMemoryDatabase()
else:
    # Assume we're running in Google App Engine
    from google.cloud import datastore
    import storage.firebasedatabase

    datastore_client = datastore.Client()
    firebase_config = datastore_client.get(datastore_client.key("Config", "firebaseConfig"))

    database = storage.firebasedatabase.FirebaseDatabase(firebase_config["value"])


@app.route(ROOT_PATH)
def index():
    return flask.render_template("index.html.j2")


@app.route(ROOT_PATH + "upload", methods=["POST"])
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

    return flask.redirect(flask.url_for(show_analysis.__name__, replay_id=replay_id))


@app.route(ROOT_PATH + "<replay_id>")
def show_analysis(replay_id: str):
    analysis_data = database.get_document_as_str(replay_id)

    if analysis_data is None:
        return flask.abort(404)

    return flask.render_template("analysis.html.j2", analysis_data=analysis_data)


def main():
    print("http://127.0.0.1:32444" + ROOT_PATH)
    app.run(host='127.0.0.1', port=32444, debug=True)


if __name__ == "__main__":
    main()
