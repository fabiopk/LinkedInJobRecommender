#!flask/bin/python
from flask import Flask
from pymongo import MongoClient, DESCENDING, ASCENDING
import json
# from bson.json_util import dumps
from flask import jsonify
from flask_cors import CORS, cross_origin
from flask import request
import datetime
from bson import ObjectId


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId) or isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


with open('config.json') as json_file:
    config = json.load(json_file)

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)


client = MongoClient(config['MONGO_URI'])
db = client.get_database('linkedin')
collection = db.jobIds


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/preds', methods=['GET'])
def get_predictions():
    output = []
    start = request.args.get('start')
    label = request.args.get('label')
    time = request.args.get('time')
    mode = request.args.get('mode')
    sortMode = ASCENDING if mode == 'worst' else DESCENDING

    if not start:
        start = 0

    if label == 'unlabeled':
        query = {'label': None, 'pred': {'$exists': True}}
    else:
        query = {'pred': {'$exists': True}}

    today = datetime.datetime.utcnow()

    if time == 'week':
        delta = datetime.timedelta(days=7)
        startDay = today - delta
        query['posted'] = {'$gt': startDay}

    if time == 'month':
        delta = datetime.timedelta(days=30)
        startDay = today - delta
        query['posted'] = {'$gt': startDay}

    if mode == 'doubt':
        query['pred'] = {'$gt': 0.4, '$lt': 0.6}

    sortMode = ASCENDING if mode == 'worst' else DESCENDING

    for s in collection.find(query).sort([("pred", sortMode)]).skip(int(start)).limit(20):
        if 'label' in s:
            label = s['label']
        else:
            label = -1
        output.append(
            {
                'title': s['title'],
                'jobId': s['jobId'],
                'description': s['description'],
                'company': s['company'],
                'label': label,
                'location': s['city'],
                'pred': s['pred'],
                'seniority': s['Seniority level']
            })
    return jsonify({'result': output})


@app.route('/api/preds/<int:job_id>', methods=['PUT'])
@cross_origin()
def update_task(job_id):
    job = collection.find_one({'jobId': str(job_id)})
    label = request.json['label']
    if label in [0, 1]:
        job['label'] = label
        collection.save(job)
    return JSONEncoder().encode({'result': job})


if __name__ == '__main__':
    app.run(debug=True, port=80)
