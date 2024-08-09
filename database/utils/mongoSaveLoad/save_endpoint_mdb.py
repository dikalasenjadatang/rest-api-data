import pymongo
from pymongo import MongoClient
from datetime import datetime

def save_endpoint_MDB(result,collection_name, mongo_uri='mongodb://localhost:27017/', database_name='E2E_TESTING', document_id='news_ep'):
    """
    Save data to MongoDB collection, avoiding duplicates based on 'keyword' and 'createdAt' fields for any number of keys in the result.

    :param result: Dictionary containing data to be saved.
    :param mongo_uri: MongoDB URI.
    :param database_name: Name of the database.
    :param collection_name: Name of the collection.
    :param document_id: The document ID to update or insert data.
    """
    client_db = MongoClient(mongo_uri)
    db = client_db[database_name]
    topik_collection = db[collection_name]

    news_ep_document = topik_collection.find_one({'_id': document_id})

    def is_duplicate(record, existing_data):
        for entry in existing_data:
            if 'keyword' in entry and 'createdAt' in entry:
                if entry['keyword'] == record['keyword'] and entry['createdAt'] == record['createdAt']:
                    return True
        return False

    if news_ep_document:
        update_fields = {}
        for key, new_data in result.items():
            existing_data = news_ep_document.get(key, [])
            filtered_new_data = [
                item for item in new_data if not is_duplicate(item, existing_data)
            ]
            if filtered_new_data:
                update_fields[key] = existing_data + filtered_new_data
        
        if update_fields:
            topik_collection.update_one(
                {'_id': document_id},
                {'$set': update_fields}
            )
    else:
        topik_collection.insert_one({'_id': document_id, **result})

    print("Data checked for duplicates and inserted/updated successfully.")
