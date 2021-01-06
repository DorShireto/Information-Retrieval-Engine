import os

from flask import Flask, request, jsonify

import search_engine_best

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def index():

    query = request.json['query']
    print(query)
    se = search_engine_best.SearchEngine()
    bench_data_path=os.path.join('data','benchmark_data_train.snappy.parquet')
    se.build_index_from_parquet(bench_data_path)
    numOfResults,results = se.search(query)
    print(results[:5])
    # return jsonify({"return": results[:20]})
    return {'res': results[:100]}
    # return results[:200]

if __name__ == '__main__':
    app.run(debug=True)