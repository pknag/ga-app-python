from flask.json.provider import JSONProvider
import json
from datetime import date
from werkzeug.http import http_date
from neo4j.time import Date as neoDate

# Utilities to deal with serializing neo4j date time data

# use json to convert to string first and then back to json
def stringify_json(data):
    res = json.loads(json.dumps(data, default=str))
    return res

# json encoder for flask
# adapted from https://github.com/pallets/flask/blob/2.3.x/src/flask/json/provider.py

def _default(o) :
    if isinstance(o, date):
        return http_date(o)

    if isinstance(o, neoDate):
        # result = str(o) # string format
        result = o.iso_format()  # iso format
        return result

    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")

# for flask app, either:
# set app.json = NeoJsonProvider(app) or
# set app.json_provider_class = NeoJsonProvider

class NeoJsonProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        # output readable json useful for debugging
        return json.dumps(obj, indent=2, default=_default, ensure_ascii=True, sort_keys=True, **kwargs)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)

