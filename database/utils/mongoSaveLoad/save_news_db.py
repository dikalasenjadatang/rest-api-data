import pymongo
from pymongo import MongoClient

DATABASE_NAME = 'E2E_TESTING'
DATA_COLLECTION_NAME = 'data_scrape'

def save_scrape_news(data_json, collection_name, mongo_url='mongodb://localhost:27017/', database_name=DATABASE_NAME, document_id='news'):
    """
    Save data to MongoDB collection, avoiding duplicates based on the 'url' field.
    If 'url' exists but with a new 'label_owner', add the new 'label_owner' to the list.

    :param data_json: List of dictionaries containing the data to be saved.
    :param mongo_uri: MongoDB URI.
    :param database_name: Name of the database.
    :param collection_name: Name of the collection.
    :param document_id: The document ID to update or insert data.
    """
    client_db = MongoClient(mongo_url)
    db = client_db[database_name]
    data_collection = db[collection_name]

    existing_document = data_collection.find_one({'_id': document_id})

    if existing_document and 'data' in existing_document:
        existing_data = existing_document['data']
        existing_urls = {item['url'] for item in existing_data}

        for new_item in data_json:
            if new_item['url'] in existing_urls:
                for existing_item in existing_data:
                    if existing_item['url'] == new_item['url']:
                        if not isinstance(existing_item['label_owner'], list):
                            existing_item['label_owner'] = [existing_item['label_owner']]
                        if not isinstance(existing_item['label_timestamp'], list):
                            existing_item['label_timestamp'] = [existing_item['label_timestamp']]
                        
                        if new_item['label_owner'] not in existing_item['label_owner']:
                            existing_item['label_owner'].append(new_item['label_owner'])
                        existing_item['label_timestamp'].append(new_item['label_timestamp'])
                        break
            else:
                new_item['label_owner'] = [new_item['label_owner']]
                new_item['label_timestamp'] = [new_item['label_timestamp']]
                existing_data.append(new_item)

        data_collection.update_one(
            {'_id': document_id},
            {'$set': {'data': existing_data}}
        )
    else:
        for new_item in data_json:
            new_item['label_owner'] = [new_item['label_owner']]
            new_item['label_timestamp'] = [new_item['label_timestamp']]
        data_collection.update_one(
            {'_id': document_id},
            {'$set': {'data': data_json}},
            upsert=True
        )

    print("Data News Saved!")


def load_scrape_news(label_owner, database_name=DATABASE_NAME, collection_name = DATA_COLLECTION_NAME,mongo_url='mongodb://localhost:27017/', document_id='news'):
    """
    Load data from MongoDB collection based on label_owner.

    :param database_name: Name of the database.
    :param collection_name: Name of the collection.
    :param label_owner: The label owner to filter by.
    :param mongo_uri: MongoDB URI.
    :param document_id: The document ID to update or insert data.
    :return: Data filtered by label_owner.
    """
    client_db = MongoClient(mongo_url)
    db = client_db[database_name]
    data_collection = db[collection_name]

    existing_document = data_collection.find_one({'_id': document_id})
    
    if existing_document and 'data' in existing_document:
        filtered_data = [item for item in existing_document['data'] if label_owner in item['label_owner']]
        return filtered_data
    else:
        return []

def save_analyze_news(data_json, collection_name, mongo_url='mongodb://localhost:27017/', database_name='E2E_TESTING', document_id='news'):
    """
    Save data to MongoDB collection, avoiding duplicates based on the 'url' field.

    :param data_json: List of dictionaries containing the data to be saved.
    :param mongo_uri: MongoDB URI.
    :param database_name: Name of the database.
    :param collection_name: Name of the collection.
    :param document_id: The document ID to update or insert data.
    """
    client_db = MongoClient(mongo_url)
    db = client_db[database_name]
    data_collection = db[collection_name]

    existing_document = data_collection.find_one({'_id': document_id})

    # Check for duplicates based on 'url' and append new data
    if existing_document and 'data' in existing_document:
        existing_data = existing_document['data']
        existing_urls = {item['url'] for item in existing_data}

        # Filter out new items that already exist based on the 'url' field
        new_data = [item for item in data_json if item['url'] not in existing_urls]

        if new_data:
            existing_data.extend(new_data)
            data_collection.update_one(
                {'_id': document_id},
                {'$set': {'data': existing_data}}
            )
    else:
        data_collection.update_one(
            {'_id': document_id},
            {'$set': {'data': data_json}},
            upsert=True
        )

    print("Data News Saved!")