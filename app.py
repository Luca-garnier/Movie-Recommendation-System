import pipeline
import sys

port = 8082
if (len(sys.argv) > 1):
    port = int(sys.argv[1])

api = pipeline.Pipeline(False, False, True, port)
api.run()