from azure.cosmos import CosmosClient, exceptions
from config import COSMOSDB_URI, COSMOSDB_KEY, COSMOSDB_DATABASE_NAME, COSMOSDB_CONTAINER_NAME

class CosmosDBService:
    def __init__(self):
        self.client = CosmosClient(COSMOSDB_URI, COSMOSDB_KEY)
        self.database = self.client.get_database_client(COSMOSDB_DATABASE_NAME)
        self.container = self.database.get_container_client(COSMOSDB_CONTAINER_NAME)

    def query_items(self, query: str, parameters: list = None):
        try:
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            return items
        except exceptions.CosmosHttpResponseError as e:
            print(f"An error occurred: {e}")
            return []

    def get_item(self, item_id: str, partition_key: str):
        try:
            item = self.container.read_item(item=item_id, partition_key=partition_key)
            return item
        except exceptions.CosmosHttpResponseError as e:
            print(f"An error occurred: {e}")
            return None

    def create_item(self, item: dict):
        try:
            self.container.create_item(body=item)
            return True
        except exceptions.CosmosHttpResponseError as e:
            print(f"An error occurred: {e}")
            return False

    def update_item(self, item_id: str, partition_key: str, updated_item: dict):
        try:
            self.container.replace_item(item=item_id, body=updated_item)
            return True
        except exceptions.CosmosHttpResponseError as e:
            print(f"An error occurred: {e}")
            return False

    def delete_item(self, item_id: str, partition_key: str):
        try:
            self.container.delete_item(item=item_id, partition_key=partition_key)
            return True
        except exceptions.CosmosHttpResponseError as e:
            print(f"An error occurred: {e}")
            return False
