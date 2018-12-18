from flask import Flask
import requests

app = Flask(__name__)

@app.route("/")
def hello():
    return get_link()

def get_link():
    r = requests.post("https://www.reddit.com/api/v1/access_token",
        data={"grant_type":"https://oauth.reddit.com/grants/installed_client", "device_id": "DO_NOT_TRACK_THIS_DEVICE"},
        auth=("ZJKlJzbFxkGauA", ""),
        headers={'User-agent': 'Muzei for reddit 0.1'})

    token = r.json()['access_token']

    r2 = requests.get("https://api.reddit.com/r/rarepuppers/top?t=day&limit=1",
        headers={'User-agent': 'Muzei for reddit 0.1', "Authentication": "bearer {}".format(token)})

    j = r2.json()
    print(j)
    return j["data"]["children"][0]["data"]["url"]

if __name__ == "__main__":
    app.run(host='0.0.0.0')
