from azure.cosmos import CosmosClient, exceptions
from azure.identity import DefaultAzureCredential
from config import COSMOSDB_URI, COSMOSDB_KEY, COSMOSDB_DATABASE_NAME, COSMOSDB_CONTAINER_NAME
import logging
from typing import List, Dict, Any
import asyncio

logger = logging.getLogger(__name__)
credential = DefaultAzureCredential()

class CosmosDBService:
    def __init__(self):
        self.client = CosmosClient(COSMOSDB_URI, credential=credential)
        self.database = self.client.get_database_client(COSMOSDB_DATABASE_NAME)
        self.container = self.database.get_container_client(COSMOSDB_CONTAINER_NAME)
        logger.info("CosmosDBService initialized")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # CosmosClient doesn't need explicit closing
        self.client = None
        logger.info("CosmosDB context exited")

    async def query_items(self, query: str, parameters: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        logger.info(f"Querying items with query: {query} and parameters: {parameters}")
        try:
            items = await asyncio.to_thread(
                lambda: list(self.container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True
                ))
            )
            logger.info(f"Query returned {len(items)} items")
            return items
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"An error occurred during query: {e}")
            return []