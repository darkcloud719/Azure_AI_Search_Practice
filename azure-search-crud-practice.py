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

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "test0819"

search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
search_index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
search_indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

def _delete_index():

    try:
        result = search_index_client.delete_index(index_name)
        print(f"Index {index_name} deleted")
    except Exception as ex:
        logging.error(ex)
        pprint(ex)

def _create_index():

    try:
        fields = [
            SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
            SearchableField(name="hotelName", type=SearchFieldDataType.String, sortable=True),
            SearchableField(name="description", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
            SearchableField(name="description_fr", type=SearchFieldDataType.String, analyzer_name="fr.lucene"),
            SearchableField(name="category", type=SearchFieldDataType.String, filterable=True, sortable=True),
            SearchableField(name="tags", type=SearchFieldDataType.String, facetable=True, filterable=True, collection=True),
            SimpleField(name="parkingIncluded", type=SearchFieldDataType.Boolean, filterable=True, sortable=True),
            SimpleField(name="lastRenovationDate", type=SearchFieldDataType.DateTimeOffset, facetable=True, filterable=True, sortable=True),
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
        suggester = [{'name':'sg','source_fields':['tags','address/city','address/country']}]

        index = SearchIndex(
            name=index_name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options,
            suggesters=suggester,
            semantic_search=semantic_search
        )

        result = search_index_client.create_or_update_index(index)
        print(f"{result.name} created")

    except Exception as ex:
        logging.error(ex)

def _upload_document():

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

        result = search_client.upload_documents(documents=DOCUMENT)

        print(f"Uploaded document {result[0].succeeded}")

    except Exception as ex:
        logging.error(ex)


def _merge_document():

    try:
        result = search_client.merge_documents(documents=[{"hotelId":"1","rating":9.9}])

        print(f"Merge document {result[0].succeeded}")
    except Exception as ex:
        logging.error(ex)

def _run_a_semantic_query():

    try:
        # QueryType => simple, full, semantic
        results = search_client.search(
            query_type="semantic",
            semantic_configuration_name="my-semantic-config",
            search_text="What hotel has a good restaurant on sit.",
            select="hotelName,description,category",
            query_caption="extractive",
            # query_answer="extractive"
        )

        for result in results:
            for key,value in result.items():
                print(f"{key}:{value}")
            print("\n")
            
            captions = result["@search.captions"]
            if captions:
                caption= captions[0]
                if caption.highlights:
                    print(f"Caption highlights:{caption.highlights}\n")
                else:
                    print(f"Caption text:{caption.text}\n")

            print("\n\n")
    except Exception as ex:
        logging.error(ex)

def _run_semantic_answers():

    try:
        results = search_client.search(
            query_type="semantic",
            semantic_configuration_name="my-semantic-config",
            search_text="What hotel is in a historic building?",
            select="hotelName,description,category",
            query_caption="extractive",
            query_answer="extractive"
        )

        # with open("results.txt","w", encoding="utf-8") as file:
        #     for result in results:
        #         file.write(f"{json.dumps(result,indent=4,ensure_ascii=False)}\n\n")
        #         result_str = json.dumps(result, indent=4, ensure_ascii=False)
        #         file.write(result_str+"\n\n")
        #         file.write(f"{str(result)}\n\n")
                 

        semantic_answers = results.get_answers()
        print("<answers start>\n")
        for answer in semantic_answers:
            if answer.highlights:
                print(f"Semantic Answer highlights:{answer.highlights}")
            else:
                print(f"Semantic Answer text:{answer.text}")
        print("<answers end>\n")

        print("<results start>\n")
        for result in results:
            for key, value in result.items():
                print(f"{key}:{value}")
                captions = result["@search.captions"]
                if captions:
                    caption = captions[0]
                    if caption.highlights:
                        print(f"Caption highlights:{caption.highlights}\n")
                    else:
                        print(f"Caption text:{caption.text}\n")
        print("<results end>\n")

    except Exception as ex:
        logging.error(ex)

    

if __name__ == "__main__":

    # _delete_index()
    # _create_index()
    # _upload_document()
    # _merge_document()
    # _run_a_semantic_query()
    _run_semantic_answers()



        

