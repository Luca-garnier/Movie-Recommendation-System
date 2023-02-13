import re
from flask import Flask, request, redirect, session
from urllib.parse import urlparse

flsk = Flask(__name__)

MAIN_WEIGHT = 1
MAIN_PORT = 5000
CANARY_WEIGHT = 1
CANARY_PORT = 5001

requestNum = 1

@flsk.route('/', defaults={'path': ''})
@flsk.route('/<path:path>')
def distribute(path):
    global requestNum
    if (requestNum > MAIN_WEIGHT + CANARY_WEIGHT):
        requestNum = 1
    if (requestNum <= MAIN_WEIGHT):
        port = MAIN_PORT
    else:
        port = CANARY_PORT
    parsedURL = urlparse(request.host_url)
    newURL = parsedURL.scheme + "://" + parsedURL.hostname + ":" + str(port) + "/" + path
    requestNum += 1
    return redirect(newURL)

flsk.run(host="0.0.0.0", port=8082)