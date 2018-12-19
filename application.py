from flask import Flask, request, abort
import configparser
import requests

app = Flask(__name__)


@app.route("/")
def hello():
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
            print(item["messaging"][0])
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
