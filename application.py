from flask import Flask, request, abort
from flask.logging import default_handler
from logging.config import dictConfig
import configparser
import os
import requests

def configure_logging():
    if not os.path.exists("logs/default.log"):
        os.mkdir("logs")

    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },
            'files': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/default.log',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi', 'files']
        }
    })

configure_logging()

app = Flask(__name__)
app.logger.removeHandler(default_handler)

@app.route("/")
def hello():
    app.logger.info("Hello there")
    return get_link()

@app.route("/webhook")
def verification():
    config = configparser.ConfigParser()
    config.read('vars.ini')
    original_token = config["Tokens"]["fb_verify_token"]
    mode = request.args["hub.mode"]
    token = request.args["hub.verify_token"]
    challenge = request.args["hub.challenge"]

    if mode is None or token is None:
        abort(403)
    elif mode == "subscribe" and token == original_token:
        return challenge
    else:
        abort(403)

@app.route("/webhook", methods=["POST"])
def messages():
    # '{"object": "page", "entry": [{"messaging": [{"message": "TEST_MESSAGE"}]}]}'
    all = request.json
    if all["object"] == "page":
        for item in all["entry"]:
            app.logger.info(item["messaging"][0])
        return "EVENT_RECEIVED"
    else:
        abort(404)

def get_link():
    r = requests.post("https://www.reddit.com/api/v1/access_token",
        data={"grant_type":"https://oauth.reddit.com/grants/installed_client", "device_id": "DO_NOT_TRACK_THIS_DEVICE"},
        auth=("ZJKlJzbFxkGauA", ""),
        headers={'User-agent': 'Muzei for reddit 0.1'})

    token = r.json()['access_token']

    r2 = requests.get("https://api.reddit.com/r/rarepuppers/top?t=day&limit=1",
        headers={'User-agent': 'Muzei for reddit 0.1', "Authentication": "bearer {}".format(token)})

    j = r2.json()

    return j["data"]["children"][0]["data"]["url"]

if __name__ == "__main__":
    app.run(host='0.0.0.0')
