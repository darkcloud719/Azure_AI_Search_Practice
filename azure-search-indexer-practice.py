import os,json,logging,sys
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType, QueryCaptionResult, QueryAnswerResult
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import(
    SearchIndexerDataContainer,
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    EntityRecognitionSkill,
    SentimentSkill,
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
    ImageAnalysisSkill,
    OcrSkill,
    VisualFeature,
    TextWeights,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch
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

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "test1113"
indexer_name = "test1113-indexer"
data_source_name = "shenghuai-datasource1113"
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

def _delete_index():

    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            search_index_client.delete_index(index_name)
            logger.info(f"Index {index_name} deleted")
    except Exception as ex:
        logger.error(ex)

def _create_index():

    try:
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="category", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="content", type=SearchFieldDataType.String)
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
        suggest = [{"name":"sg","source_fields":["title","category"]}]

        index = SearchIndex(
            name=index_name,
            fields=fields,
            cors_options=cors_options
        )

        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.create_index(index)
            logger.info(f"Index {index_name} created")

    except Exception as ex:
        logger.error(ex)

def _create_data_source():
    
    try:

        container = SearchIndexerDataContainer(name="shenghuaitestcontainer")

        data_source_connection = SearchIndexerDataSourceConnection(
            name=data_source_name,
            type="azureblob",
            connection_string=connection_string,
            container=container
        )

        with SearchIndexerClient(service_endpoint, AzureKeyCredential(key)) as search_indexer_client:
            search_indexer_client.create_data_source_connection(data_source_connection)
            logger.info(f"Data source connection created: {data_source_connection.name}")
    except Exception as ex:
        logger.error(ex)

def _create_indexer():

    try:

        configuration = IndexingParametersConfiguration(
            parsing_mode="jsonArray",
            query_timeout=None
        )

        parameters = IndexingParameters(configuration=configuration)

        indexer = SearchIndexer(
            name="shenghuai-indexer1113",
            data_source_name=data_source_name,
            target_index_name=index_name,
            parameters=parameters
        )

        with SearchIndexerClient(service_endpoint, AzureKeyCredential(key)) as search_indexer_client:
            search_indexer_client.create_indexer(indexer)
            # result = search_indexer_client.get_indexer(indexer.name)
            # search_indexer_client.run_indexer(indexer_name)
            logger.info(f"Indexer {indexer.name} created")
    except Exception as ex:
        logger.error(ex)

def _simple_query():

    try:
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type=QueryType.SIMPLE,
                search_text="gateway",
                include_total_count=True
            )

            logger.info(f"Total count: {results.get_count()}")

            for result in results:
                for result_key, value in result.items():
                    logger.info(f"{result_key}:{value}")

                print("\n\n")

    except Exception as ex:
        logger.error(ex)

def _full_query():

    try:
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type=QueryType.FULL,
                search_text="title:gateway",
                include_total_count=True
            )

            logger.info(f"Total count: {results.get_count()}")

            for result in results:
                for result_key, value in result.items():
                    logger.info(f"{result_key}:{value}")

                print("\n\n")

    except Exception as ex:
        logger.error(ex)

if __name__ == "__main__":
    # _delete_index()
    # _create_index()
    # _create_data_source()
    # _create_indexer()
    # _simple_query()
    _full_query()
