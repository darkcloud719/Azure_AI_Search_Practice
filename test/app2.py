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

load_dotenv()

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "20240912_1"
indexer_name = "20240912_1-indexer"
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

def delete_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.delete_index(index_name)
            logger.info(f"Index {index_name} deleted")
    except Exception as ex:
        logging.error(ex)

def get_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.get_index(index_name)
            logger.info(f"Index {index_name} found")
    except Exception as ex:
        logging.error(ex)

def create_index():
    try:
        fields = [
            SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True, filterable=True, sortable=True),
            SimpleField(name="hotelName", type=SearchFieldDataType.String, sortable=True),
            SearchableField(name="description", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
            SearchableField(name="descriptionFr", type=SearchFieldDataType.String, analyzer_name="fr.lucene"),
            SearchableField(name="category" ,type=SearchFieldDataType.String, facetagble=True, filterable=True, sortable=True),
            SearchableField(name="tags", type=SearchFieldDataType.String, facetable=True, filterable=True, collection=True),
            SimpleField(name="parkingIncluded", type=SearchFieldDataType.Boolean, facetable=True, filterable=True, sortable=True),
            SimpleField(name="smokingAllowed", type=SearchFieldDataType.Boolean, facetable=True, filterable=True, sortable=True),
            SimpleField(name="lastRenovationData", type=SearchFieldDataType.DateTimeOffset, facetable=True, filterable=True, sortable=True),
            SimpleField(name="rating", type=SearchFieldDataType.Double, facetable=True, filterable=True, sortable=True),
            SimpleField(name="location", type=SearchFieldDataType.GeographyPoint),
            ComplexField(name="address", fields=[
                SearchableField(name="streetAddress", type=SearchFieldDataType.String),
                SearchableField(name="city", type=SearchFieldDataType.String),
                SearchableField(name="stateProvince", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True),
                SearchableField(name="postalCode", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True),
                SearchableField(name="country", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True)
            ]),
            SimpleField(name="url", type=SearchFieldDataType.String),
            SimpleField(name="file_name", type=SearchFieldDataType.String),
            SearchableField(name="emails", type=SearchFieldDataType.String, collection=True),
            SimpleField(name="mysentiment", type=SearchFieldDataType.String),
            ComplexField(
                name="nameEntities",
                fields=[
                    SimpleField(name="text", type=SearchFieldDataType.String),
                    SimpleField(name="category", type=SearchFieldDataType.String),
                    SimpleField(name="subcategory", type=SearchFieldDataType.String),
                    SimpleField(name="length", type=SearchFieldDataType.Int32),
                    SimpleField(name="offset", type=SearchFieldDataType.Int32),
                    SimpleField(name="confidence", type=SearchFieldDataType.Double)
                ],
                collection=True
            )
        ]

        semantic_config = SemanticConfiguration(
            name="my-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="hotelName"),
                description_fields=[
                    SemanticField(field_name="description"),
                    SemanticField(field_name="descriptionFr")
                ],
                keywords_fields=[SemanticField(field_name="category")],
                content_fields=[SemanticField(field_name="description")]
            )
        )

        semantic_search = SemanticSearch(configurations=[semantic_config])

        scoring_profiles:List[ScoringProfile] = []
        scoring_profile = ScoringProfile(
            name="MyProfile",
            text_weights=TextWeights(weights={"description":1.5})
        )
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        suggester = [{"name":"sg","source_fields":["tags","address/city","address/country"]}]

        index = SearchIndex(
            name=index_name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_otpions=cors_options,
            suggesters=suggester,
            semantic_search=semantic_search
        )

        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.create_index(index)

            return result
        
    except Exception as ex:
        logging.error(ex)



