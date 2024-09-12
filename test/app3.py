import os,json,logging,sys
from tenacity import retry, wait_random_exponential, stop_after_attempt
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType, QueryCaptionResult, QueryAnswerResult
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import(
    SearchIndexerDataContainer,
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerSkillset,
    SearchableField,
    IndexingParameters,
    SearchIndexerDataSourceConnection,
    IndexingParametersConfiguration,
    IndexingSchedule,
    CorsOptions,
    SearchIndexer,
    FieldMapping,
    ScoringProfile,
    ComplexField,
    TextWeights,
    SearchField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)
from dotenv import load_dotenv
from typing import List
from rich import print as pprint

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

load_dotenv()

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "20240912_1"
indexer_name = "202409121-indexer"
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = "20240912container"

def delete_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            search_index_client.delete_index(index_name)
            logger.info(f"Index {index_name} deleted")
    except Exception as ex:
        logger.error(ex)

def get_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.get_index(index_name)
            logger.info(f"Index {index_name} found")
    except Exception as ex:
        logger.error(ex)

def create_index():
    try:
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="category", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
        ]

        semantic_config = SemanticConfiguration(
            name="my-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="title"),
                keywords_fields=[SemanticField(field_name="category")],
                content_fields=[SemanticField(field_name="content")]
            )
        )

        semantic_search = SemanticSearch(configurations=[semantic_config])

        scoring_profiles:List[ScoringProfile] = []
        scoring_profile = ScoringProfile(
            name="MyProfile",
            text_weights=TextWeights(weights={"content":1.5})
        )
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        suggester = [{"name":"sg","source_fields":["category","content"]}]

        index = SearchIndex(
            name=index_name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options,
            semantic_search=semantic_search
        )

        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.create_index(index)
            logger.info(f"Index {index_name} created")

            return result

    except Exception as ex:
        logger.error(ex)

def delete_data_source():
    try:
        with SearchIndexerClient(service_endpoint, AzureKeyCredential(key)) as search_indexer_client:
            search_indexer_client.delete_data_source_connection("20240912-datasource")
            logger.info(f"Data source connection 20240912-datasource deleted")
    except Exception as ex:
        logger.error(ex)

def create_data_source():
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # create a new container
        if not container_name in [container.name for container in blob_service_client.list_containers()]:
            blob_service_client.create_container(container_name)
            logger.info(f"Container {container_name} created")

        container = SearchIndexerDataContainer(name=container_name)
        
        data_source_connection = SearchIndexerDataSourceConnection(
            name="20240912-datasource",
            type="azureblob",
            connection_string=connection_string,
            container=container
        )

        logger.info(f"Data source connection {data_source_connection.name} created")

        with SearchIndexerClient(service_endpoint, AzureKeyCredential(key)) as search_indexer_client:
            data_source = search_indexer_client.create_data_source_connection(data_source_connection)
            
            logger.info(f"Data source {data_source.name} created")
            return data_source

    except Exception as ex:
        logger.error(ex)

def delete_indexer():
    try:
        with SearchIndexerClient(service_endpoint, AzureKeyCredential(key)) as search_indexer_client:
            search_indexer_client.delete_indexer(indexer_name)
            logger.info(f"Indexer {indexer_name} deleted")
    except Exception as ex:
        logger.error(ex)

def trigger_indexer():
    try:
        delete_index()

        delete_data_source()

        # delete_indexer()

        datasource = create_data_source().name
        
        ind_name = create_index().name

        configuration = IndexingParametersConfiguration(parsing_mode="jsonArray", query_timeout=None)

        parameters = IndexingParameters(configuration=configuration)

        indexer = SearchIndexer(
            name=indexer_name,
            data_source_name=datasource,
            target_index_name=ind_name,
            parameters=parameters,
        )

        with SearchIndexerClient(service_endpoint, AzureKeyCredential(key)) as search_indexer_client:
            indexer = search_indexer_client.create_indexer(indexer)
            logger.info(f"Indexer {indexer.name} created")
            result = search_indexer_client.get_indexer(indexer_name)
            search_indexer_client.run_indexer(indexer_name)

    except Exception as ex:
        logger.error(ex)

if __name__ == "__main__":
    # delete_index()
    # create_index()
    # create_data_source()
    trigger_indexer()



        





