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
    SemanticSearch,
)
from dotenv import load_dotenv
from typing import List
from rich import print as pprint 

load_dotenv()

# logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
# https://www.youtube.com/watch?v=pxuXaaT1u3k
# log file highlighting
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    # filename="basic1.log"
)
# logging.debug("This is a debug message.")
# logging.info("This is an info message.")
# logging.warning("This is a warning message.")
# logging.error("This is an error message.")
# logging.critical("This is a critical message.")

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "test0819"

search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
search_index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
search_indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

def _get_index():

    try:
        result = search_index_client.get_index(index_name)
        print(f"Index {index_name} existed")
    except Exception as ex:
        logging.error(ex)
        pprint(ex)

def _delete_index():

    try:
        search_index_client.delete_index(index_name)
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
            SearchableField(name="category", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True),
            SearchableField(name="tags", type=SearchFieldDataType.String, facetable=True, filterable=True, collection=True),
            SimpleField(name="parkingIncluded", type=SearchFieldDataType.Boolean, facetable=True, filterable=True, sortable=True),
            SimpleField(name="LastRenovationDate", type=SearchFieldDataType.DateTimeOffset, facetable=True, filterable=True, sortable=True),
            SimpleField(name="rating", type=SearchFieldDataType.Double, facetable=True, filterable=True, sortable=True),
            ComplexField(name="address", fields=[
                SearchableField(name="streetAddress", type=SearchFieldDataType.String),
                SearchableField(name="city", type=SearchFieldDataType.String),
                SearchableField(name="stateProvince", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True),
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
        scoring_profile = ScoringProfile(
            name="MyProfile",
            text_weights=TextWeights(weights={"description":1.5}),
        )
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        suggester = [{"name":"sg","source_fields":{"tags","address/city","address/country"}}]

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

def _upload_documents():

    try:
        documents = [
            {
            "@search.action": "upload",
            "HotelId": "1",
            "HotelName": "Secret Point Motel",
            "Description": "The hotel is ideally located on the main commercial artery of the city in the heart of New York. A few minutes away is Time's Square and the historic centre of the city, as well as other places of interest that make New York one of America's most attractive and cosmopolitan cities.",
            "Description_fr": "L'hôtel est idéalement situé sur la principale artère commerciale de la ville en plein cœur de New York. A quelques minutes se trouve la place du temps et le centre historique de la ville, ainsi que d'autres lieux d'intérêt qui font de New York l'une des villes les plus attractives et cosmopolites de l'Amérique.",
            "Category": "Boutique",
            "Tags": [ "pool", "air conditioning", "concierge" ],
            "ParkingIncluded": "false",
            "LastRenovationDate": "1970-01-18T00:00:00Z",
            "Rating": 3.60,
            "Address": {
                "StreetAddress": "677 5th Ave",
                "City": "New York",
                "StateProvince": "NY",
                "PostalCode": "10022",
                "Country": "USA"
                }
            },
            {
            "@search.action": "upload",
            "HotelId": "2",
            "HotelName": "Twin Dome Motel",
            "Description": "The hotel is situated in a  nineteenth century plaza, which has been expanded and renovated to the highest architectural standards to create a modern, functional and first-class hotel in which art and unique historical elements coexist with the most modern comforts.",
            "Description_fr": "L'hôtel est situé dans une place du XIXe siècle, qui a été agrandie et rénovée aux plus hautes normes architecturales pour créer un hôtel moderne, fonctionnel et de première classe dans lequel l'art et les éléments historiques uniques coexistent avec le confort le plus moderne.",
            "Category": "Boutique",
            "Tags": [ "pool", "free wifi", "concierge" ],
            "ParkingIncluded": "false",
            "LastRenovationDate": "1979-02-18T00:00:00Z",
            "Rating": 3.60,
            "Address": {
                "StreetAddress": "140 University Town Center Dr",
                "City": "Sarasota",
                "StateProvince": "FL",
                "PostalCode": "34243",
                "Country": "USA"
                }
            },
            {
            "@search.action": "upload",
            "HotelId": "3",
            "HotelName": "Triple Landscape Hotel",
            "Description": "The Hotel stands out for its gastronomic excellence under the management of William Dough, who advises on and oversees all of the Hotel's restaurant services.",
            "Description_fr": "L'hôtel est situé dans une place du XIXe siècle, qui a été agrandie et rénovée aux plus hautes normes architecturales pour créer un hôtel moderne, fonctionnel et de première classe dans lequel l'art et les éléments historiques uniques coexistent avec le confort le plus moderne.",
            "Category": "Resort and Spa",
            "Tags": [ "air conditioning", "bar", "continental breakfast" ],
            "ParkingIncluded": "true",
            "LastRenovationDate": "2015-09-20T00:00:00Z",
            "Rating": 4.80,
            "Address": {
                "StreetAddress": "3393 Peachtree Rd",
                "City": "Atlanta",
                "StateProvince": "GA",
                "PostalCode": "30326",
                "Country": "USA"
                }
            },
            {
            "@search.action": "upload",
            "HotelId": "4",
            "HotelName": "Sublime Cliff Hotel",
            "Description": "Sublime Cliff Hotel is located in the heart of the historic center of Sublime in an extremely vibrant and lively area within short walking distance to the sites and landmarks of the city and is surrounded by the extraordinary beauty of churches, buildings, shops and monuments. Sublime Cliff is part of a lovingly restored 1800 palace.",
            "Description_fr": "Le sublime Cliff Hotel est situé au coeur du centre historique de sublime dans un quartier extrêmement animé et vivant, à courte distance de marche des sites et monuments de la ville et est entouré par l'extraordinaire beauté des églises, des bâtiments, des commerces et Monuments. Sublime Cliff fait partie d'un Palace 1800 restauré avec amour.",
            "Category": "Boutique",
            "Tags": [ "concierge", "view", "24-hour front desk service" ],
            "ParkingIncluded": "true",
            "LastRenovationDate": "1960-02-06T00:00:00Z",
            "Rating": 4.60,
            "Address": {
                "StreetAddress": "7400 San Pedro Ave",
                "City": "San Antonio",
                "StateProvince": "TX",
                "PostalCode": "78216",
                "Country": "USA"
                }
            }
        ]

        result = search_client.upload_documents(documents=documents)
        print(f"Uploaded of new document succeeded: {result[0].succeeded}")
    
    except Exception as ex:
        logging.error(ex)

def _run_first_query():

    try:
        results = search_client.search(
            query_type="simple",
            search_text="*",
            select="hotelName,description",
            include_total_count=True
        )      

        print(f"Total Documents Matching Querying {results.get_count()}")
        
        for result in results:
            for key, value in result.items():
                print(f"{key}:{value}")
            print("\n")
    except Exception as ex:
        logging.error(ex)

def _run_a_term_query():

    try:
        results = search_client.search(
            query_type="simple",
            search_text="wifi",
            select="hotelName,description,tags",
            include_total_count=True
        )

        print(f"Total Documents Matching Querying {results.get_count()}")
        for result in results:
            for key, value in result.items():
                print(f"{key}:{value}")
            print("\n")

    except Exception as ex:
        logging.error(ex)

def _run_a_filter_query():

    try:
        results = search_client.search(
            search_text="hotels",
            select="hotelId,hotelName,rating",
            fileter="rating gt 4",
            order_by=["rating desc"]
        )

        for result in results:
            for key, value in result.items():
                print(f"{key}:{value}")

    except Exception as ex:
        logging.error(ex)


def _run_a_specific():

    try:
        results = search_client.search(
            search_text="hotel",
            search_fields=["description"],
            select="hotelId,hotelName,description"
        )

        for result in results:
            for key, value in result.items():
                print(f"{key}:{value}")

    except Exception as ex:
        logging.error(ex)

def _run_a_facet_query():

    try:
        results = search_client.search(
            search_text="*",
            facets=["category"]
        )

        facets = results.get_facets()

        # pprint(facets)

        for facet in facets["category"]:
            for key, value in facet.items():
                print(f"{key}:{value}")
            print("\n")
            # print(facet)
    
    except Exception as ex:
        logging.error(ex)


def _run_look_up_document():

    try:

        result = search_client.get_document(key="3")

        for key, value in result.items():
            print(f"{key}:{value}")

    except Exception as ex:
        logging.error(ex)

def _run_a_suggest_query():

    try:

        search_suggestion = "sa"
        results = search_client.autocomplete(
            search_text=search_suggestion,
            suggester_name="sg",
            mode="twoTerms"
        )

        print(f"Autocomplete Suggestions: {search_suggestion}")

        for result in results:
            for key,value in result.items():
                print(f"{key}:{value}")
            print("\n")

    except Exception as ex:
        logging.error(ex)

# test
if __name__ == "__main__":
    # _get_index()
    # _delete_index()
    # _create_index()
    # _upload_documents()
    # _run_first_query()
    # _run_a_specific()
    # _run_a_facet_query()
    # _run_look_up_document()
    _run_a_suggest_query()