import io
import flask
from . import data
from . import storage

app = flask.Flask(__name__)

try:
    from google.cloud import datastore
    from .storage.firebasedatabase import FirebaseDatabase

    datastore_client = datastore.Client()
    firebase_config = datastore_client.get(datastore_client.key("Config", "firebaseConfig"))

    database: storage.Database = FirebaseDatabase(firebase_config["value"])
except Exception as err:
    print("DB connection failed with error - using in-memory database instead.")
    print(err)
    from .storage.inmemorydatabase import InMemoryDatabase
    database: storage.Database = InMemoryDatabase()


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

    replay_id, replay_analysis = data.analyse_replay_file(replay_name, temp_file)

    temp_file.close()

    database.add_document(replay_id, replay_analysis)

    return flask.redirect(flask.url_for(show_analysis.__name__, replay_id=replay_id))


@app.route("/<replay_id>")
def show_analysis(replay_id: str):
    analysis_data = database.get_document_as_str(replay_id)

    if analysis_data is None:
        return flask.abort(404)

    return flask.render_template("analysis.html.j2", analysis_data=analysis_data)