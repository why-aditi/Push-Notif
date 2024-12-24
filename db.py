from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['JBM']
user_info = db['User_Info']  