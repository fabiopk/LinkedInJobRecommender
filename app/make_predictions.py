from pymongo import MongoClient
import pandas as pd
from feature_extractor import get_ohe_features
from scipy.sparse import hstack
import joblib as jb
import datetime
import json

with open('config.json') as json_file:
    config = json.load(json_file)

client = MongoClient(config['MONGO_URI'])
db = client.get_database('linkedin')
collection = db.jobIds

df = pd.DataFrame(list(collection.find({'label': {'$exists': False}})))

lgbm = jb.load('./models/lgbm_19_Jul_2020.jb')
rf = jb.load('./models/rf_19_Jul_2020.jb')
lr = jb.load('./models/lr_19_Jul_2020.jb')
desc_vec = jb.load('./models/desc_vec_19_Jul_2020.jb')
title_vec = jb.load('./models/title_vec_19_Jul_2020.jb')

usedFeatures = ['applicants', 'applicants_per_day', 'description_len']

features_list = [df[usedFeatures]]
categorical_fields = ['Seniority level',
                      'Employment type', 'Job function', 'Industries']

for field in categorical_fields:
    features_list.append(get_ohe_features(df, field))

title_bow_test = title_vec.transform(df['title'])
desc_bow_test = desc_vec.transform(df['description'])
features_list.append(title_bow_test)
features_list.append(desc_bow_test)

X_test = hstack(features_list)
pred_lgbm = lgbm.predict_proba(X_test)[:, 1]
pred_rf = rf.predict_proba(X_test)[:, 1]
pred_lr = lr.predict_proba(X_test)[:, 1]

df['pred'] = pred_lgbm * 0.5 + pred_rf * 0.2 + pred_lr * 0.3

for unpred_result in collection.find({'label': {'$exists': False}}):
    print('Added pred for job {}'.format(unpred_result['jobId']))
    unpred_result['pred'] = float(
        df[df['jobId'] == unpred_result['jobId']]['pred'])
    unpred_result['pred_date'] = datetime.datetime.utcnow()
    collection.replace_one({'jobId': unpred_result['jobId']}, unpred_result)
