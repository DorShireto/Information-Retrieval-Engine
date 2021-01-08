import os
import time

from flask import Flask, request
from flask_cors import CORS

import search_engine_best

app = Flask(_name_)
CORS(app)

print("start building inverted index")
se = search_engine_best.SearchEngine()
bench_data_path = os.path.join('data', 'benchmark_data_train.snappy.parquet')
se.build_index_from_parquet(bench_data_path)
print("finished")


@app.route('/', methods=['POST'])
def index():
    query = request.json['query']
    print(query)

    numOfResults, results = se.search(query)

    print(results[:5])
    # return jsonify({"return": results[:20]})
    return {'res': results[:100]}
    # return results[:200]


@app.route('/', methods=['OPTIONS'])
def options(self):
    return {'Allow': 'POST'}, 200, \
           {'Access-Control-Allow-Origin': '*', }


if _name_ == '_main_':
    app.run(host="0.0.0.0")