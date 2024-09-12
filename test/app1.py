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

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s -%(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S"
# )

logger = logging.getLogger("custom_logger")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

# logger.debug("This is a debug message")
# logger.info("This is an info message")
# logger.warning("This is a warning message")
# logger.error("This is an error message")
# logger.critical("This is a critical message")


service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "20240912"

def delete_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            search_index_client.delete_index(index_name)
            logger.warning(f"Index {index_name} deleted")
    except Exception as e:
        logger.error(f"Error: {e}")
        
def create_index():
    try:
        fields = [
            SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
            SearchableField(name="hotelName", type=SearchFieldDataType.String, sortable=True),
            SearchableField(name="description", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
            SearchableField(name="description_fr", type=SearchFieldDataType.String, analyzer_name="fr.lucene"),
            SearchableField(name="category", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True),
            SearchableField(name="tags", type=SearchFieldDataType.String, facetable=True, filterable=True, collection=True),
            SimpleField(name="parkingIncluded", type=SearchFieldDataType.Boolean, filterable=True, sortable=True),
            SimpleField(name="lastRenovationDate", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
            SimpleField(name="rating", type=SearchFieldDataType.Double, facetable=True, filterable=True, sortable=True),
            ComplexField(name="address", fields=[
                SearchableField(name="streetAddress", type=SearchFieldDataType.String),
                SearchableField(name="city", type=SearchFieldDataType.String),
                SearchableField(name="stateProvince", type=SearchFieldDataType.String),
                SearchableField(name="postalCode", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True),
                SearchableField(name="country", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True)
            ])
        ]

        semantic_config = SemanticConfiguration(
            name="my-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="hotelName"),
                keywords_fields=[SemanticField(field_name="category")],
                content_fields=[SemanticField(field_name="description")]
            )
        )

        semantic_search = SemanticSearch(configurations=[semantic_config])

        scoring_profiles:List[ScoringProfile] = []
        scoring_profile = ScoringProfile(name="MyProfile", text_weights=TextWeights(weights={"description":1.5}))
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        suggester = [{"name":"sg","source_fields":["tags","address/city","address/country"]}]

        index = SearchIndex(
            name=index_name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options,
            suggesters=suggester,
            semantic_search=semantic_search
        )

        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.create_index(index)
            logger.info(f"Index {result.name} created")
    except Exception as ex:
        logger.error(f"Error: {ex}")

def upload_document():

    try:

        DOCUMENT = {
            "@search.action":"upload",
            "hotelId":"1",
            "hotelName":"Secret Point Motel",
            "description":"The hotel is ideally located on the main commercial artery of the city in the heart of New York. A few minutes away is Time's Square and the historic centre of the city, as well as other places of interest that make New York one of America's most attractive and cosmopolitan cities.",
            "description_fr":"L'hôtel est idéalement situé sur la principale artère commerciale de la ville en plein cœur de New York. A quelques minutes se trouve la place du temps et le centre historique de la ville, ainsi que d'autres lieux d'intérêt qui font de New York l'une des villes les plus attractives et cosmopolites de l'Amérique.",
            "category":"Boutique",
            "Tags":["pool","air conditioning","concierge"],
            "parkingIncluded":False,
            "lastRenovationDate":"1970-01-18T00:00:00Z",
            "rating":3.60,
            "address":{
                "streetAddress":"677 5th Ave",
                "city":"New York",
                "stateProvince":"NY",
                "postalCode":"10022",
                "country":"USA"
            }
        }

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            result = search_client.upload_documents(documents=[DOCUMENT])
            logger.info(f"Upload result: {result}")
    except Exception as ex:
        logger.error(f"Error: {ex}")

def merge_document():

    try:
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            result = search_client.merge_documents(documents=[{"hotelId":"1","rating":9.5}])
            logger.info(f"Merge result: {result}")
    except Exception as ex:
        logger.error(f"Error: {ex}")

def run_a_semantic_query():

    try:
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type="semantic",
                semantic_configuration_name="my-semantic-config",
                search_text="What hotel has a good restaurant on sit?",
                select="hotelName,description,category",
                query_caption="extractive"
            )

            for result in results:
                for result_key,value in result.items():
                    print(f"{result_key}:{value}")
                print("\n")

                captions = result["@search.captions"]
                if captions:
                    caption = captions[0]
                    if caption.highlights:
                        print(f"Caption: {caption.highlights}\n")
                    else:
                        print(f"Caption: {caption.text}\n")

                print("\n\n")
    except Exception as ex:
        logging.error(f"Error: {ex}")

def run_semantic_answers():

    try:
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type="semantic",
                semantic_configuration_name="my-semantic-config",
                search_text="What hotel is in a historic building?",
                select="hotelName,description,category",
                query_caption="extractive",
                query_answer="extractive"
            )

            semantic_answers = results.get_answers()
            print("<answers start>\n")
            for answer in semantic_answers:
                if answer.highlights:
                    print(f"Semantic Answer highlights:{answer.highlights}")
                else:
                    print(f"Semantic Answer text:{answer.text}")

            print("<answers end>\n")
            for result in results:
                for result_key,value in result.items():
                    print(f"{result_key}:{value}")
                print("\n")
                captions = result["@search.captions"]
                if captions:
                    caption = captions[0]
                    if caption.highlights:
                        print(f"Caption highlights: {caption.highlights}\n")
                    else:
                        print(f"Caption text: {caption.text}\n")
            print("<results end>\n")
    except Exception as ex:
        logging.error(ex)



                


if __name__ == "__main__":
    # delete_index()
    # create_index()
    # upload_document()
    # merge_document()
    # run_a_semantic_query()
    run_semantic_answers()