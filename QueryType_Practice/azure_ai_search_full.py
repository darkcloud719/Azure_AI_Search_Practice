import os,json,logging,sys
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType, QueryCaptionResult, QueryAnswerResult, VectorizedQuery
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
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch
)
from dotenv import load_dotenv
from typing import List
from rich import print as pprint

load_dotenv()

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

service_endponit = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "test0819_s"

def search_index_by_querytype_full():
    try:
        with SearchClient(service_endponit, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type=QueryType.FULL,
                search_text="gateway",
                # search_text="gateway AND networking",
                # search_text="gateway OR networking",
                # search_text="gatewar AND NOT networking",
                # search_text="title:gateway",
                # search_text="rating:[4 TO 5]",
                # search_text="gateway AND (networking OR security)"
                include_total_count=True,
                top=2
            )

            for result in results:
                for result_key, value in result.items():
                    print(f"{result_key}:{value}")
                print("\n\n")

    except Exception as ex:
        logging.error(ex)

if __name__ == "__main__":
    search_index_by_querytype_full()