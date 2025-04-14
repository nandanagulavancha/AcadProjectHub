import gridfs
from database import mongo
from bson.objectid import ObjectId
from flask import current_app

def get_fs():
    """Get GridFS instance within the app context."""
    return gridfs.GridFS(mongo.db)

def save_file(file, filename):
    fs = get_fs()
    file_id = fs.put(file, filename=filename)
    return str(file_id)

def get_file(file_id):
    fs = get_fs()
    return fs.get(ObjectId(file_id))

def delete_file(file_id):
    fs = get_fs()
    fs.delete(ObjectId(file_id))