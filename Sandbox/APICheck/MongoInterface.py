from mongoengine import *
import json
import traceback

class previous_phone_info(DynamicEmbeddedDocument):
    id = StringField(required=True)
    
    
class phone_info(DynamicDocument):
    """
    A dynamic document that adds fields dynamically when they are inserted.
    It has a phone_number field.
    """
    id = StringField(required=True, primary_key=True)
    version = IntField(default=0)
    previous = EmbeddedDocumentListField(previous_phone_info)

def _previous_document_factory(parent_document_class, id, **input_json):
    if parent_document_class == phone_info:
        return previous_phone_info(id=id, **input_json)
    else:
        raise TypeError("Document is not supported")
        

def connect_to_db(database, host, port):
    """
    Closes any existing connections. Connects to the MongoDB database at the parameters specified.
    :param database:string The database name to connect to
    :param host:string The host on which to connect(localhost is 127.0.0.1)
    :param port:int The port to connect to(MongoDB defaults to 27017)
    :return: True if there were no errors. False if an exception occured.
    """
    try:
        disconnect()
        print("Connecting to the database...")
        connect(database, host=host, port=port)
        return True
    except Exception as e:
        print(e)
        disconnect()
        return False


class DatabaseHandler:
    """
    This is an interface to the MongoDB database.
    """

    def __init__(self):
        pass

    def insert_json(self, id_key, collection, **input_json):
        """
        Inserts the document and updates the version if it already exists.
        """
        try:
            if collection.objects(id=id_key).count() > 0 and not collection.objects(**input_json):
                print("Object already exist but is not the same. Updating object and storing previous version in previous array...")
                previous_document = self.get_embedded_previous_document(collection, id_key)
                self._insert_previous_version(id_key, collection, previous_document, **input_json)
                return True
            if not collection.objects(id=id_key):
                print("Document being inserted into MongoDB!")
                document = collection(**input_json)
                document.id = id_key
                document.save()
            else:
                print("Document exists....")
                print("Document not updated because the database contains the same information")
                return False
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()

    def get_embedded_previous_document(self, collection, id):
        doc = collection.objects().get(id=id)
        document_json = json.loads(doc.to_json())
        document_json.pop("_id")
        previous_document = _previous_document_factory(collection, id, **document_json)
        return previous_document
            

    def _insert_previous_version(self, id_key, collection, previous_document, **input_json):
        collection.objects(id=id_key).update(push__previous=previous_document)
        collection.objects(id=id_key).update(**input_json)
        collection.objects(id=id_key).update(inc__version=1)
        
    def _rename_key(self, document_json, id_key, new_name_for_id_key):
        new_json = document_json
        if id_key in document_json:
            identifier = document_json[id_key]
            new_json['new_name_for_id_key'] = identifier
            new_json.pop(id_key)
        return new_json





def key_finder(json_input, lookup_key):
    '''
    A geneator that recursively finds the next lookup_key's value in the possibly nested
    json input.
    '''
    if isinstance(json_input, dict):
        for key, value in json_input.items():
            if key == lookup_key:
                yield value
            else:
                yield from key_finder(value, lookup_key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from key_finder(item, lookup_key)

def json_upsert(json_to_insert, collection_class, id_key='id'):
    """
    Convenience function to connect to the database
    insert the item into the specified collection
    using the specified key as a unique idenitifer.
    :param item:dict The json dictionary to insert.
    :param id_key The key to use as a unique idenitifer.
    :param collection_class:MongoDBDocumentClass Currently 
                                                 just phone_info without string quotes    
    """
    connect_to_db('api', 'localhost', 27017)
    phone_number = next(key_finder(json_to_insert, id_key))
    db_handler = DatabaseHandler()
    input_json = db_handler._rename_key(json_to_insert, 'id', 'old_identifier')
    db_handler.insert_json(phone_number, collection_class, **input_json)
    disconnect()

if __name__ == "__main__":
    item = '''{

    "id": "Phone.3dbb6fef-a2df-4b08-cfe3-bc7128b6f5b4",


    "phone_number": "630936652802",
    "is_valid": true,
    "country_calling_code": "U3S2",
    "line_type": "NonFeixedVOIP",
    "carrier": "E2kata Telco2",
    "is_prepaid": false,
    "is_commercial": true,
    "belongs_to": 

{

    "id": "Busin3ess.d455e455-e647-4304-9679-06bd9550c568",
    "name": "string",
    "firstname": "string",
    "middlename": "string",
    "lastnamse": "string",
    "alternate_names": 

[],
"age_range": "string",
"gender": "string",
"type": "Business",
"link_to_phone_start_date": "string",
"industry": 

    []

},
"current_addresses": 
[

    {}

],
"historical_addresses": 
[

    {}

],
"associated_people": 
[

    {}

],
"alternate_phones": 
[

    {}

],
"error": 
{

    "name": "PartialError",
    "message": "Could not retrieve entire response"

},
"warnings": 

    [
        "Invalid Input"
    ]

}
'''
    item = json.loads(item)
    json_upsert(json_to_insert=item, collection_class=phone_info, id_key='phone_number')
 
