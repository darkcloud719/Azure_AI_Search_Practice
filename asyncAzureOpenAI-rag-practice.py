"""
AZURE AI OPENAI & AZURE SEARCH * RAG * EMBEDDING
"""

import os, logging, asyncio
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.aio import SearchClient
from openai import AsyncAzureOpenAI
from enum import Enum
from typing import List, Optional
from dotenv import load_dotenv
from rich import print as pprint
from azure.search.documents.models import QueryType, QueryCaptionType, QueryAnswerType
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
    SearchField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    VectorSearchProfile,
    HnswAlgorithmConfiguration
)

load_dotenv()

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

service_endpoint= os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "test0902"
indexer_name = "test0902-indexer"
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
search_index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
search_indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY must be set in .env file"
assert os.getenv("OPENAI_API_VERSION"), "OPENAI_API_VERSION must be set in .env file"
assert os.getenv("AZURE_OPENAI_ENDPOINT"), "AZURE_OPENAI_ENDPOINT must be set in .env file"
assert os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS"), "AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS must be set in .env file"
assert os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_FOUR"), "AZURE_OPENAI_DEPLOYMENT_FOR_FOUR must be set in .env file"

search_type = "text"
use_semantic_reranker = True
sources_to_include = 5

client = AsyncAzureOpenAI(
    api_key = os.getenv("OPENAI_API_KEY"),
    api_version = os.getenv("OPENAI_API_VERSION"),
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
)

class SearchType(Enum):
    TEXT = "text"
    VECTOR = "vector"
    HYBRID = "hybrid"

GROUNDED_PROMPT = """
You are a friendly assistant that recommends hotels based on activities and amentities.
Answer the query using only the sources provided below in a friendly and concise bulleted manner.
Answer only with the facts listed in the list of sources below.
If there isn't enough information below, say you don't know.
Do not generate answers that don't use the sources below.
Query:{query}\n
Sources:\n{sources}
"""



async def get_source(search_client:SearchClient, query:str, search_type:SearchType, use_semantic_reranker:bool=True, sources_to_include:int=5) -> List[str]:
    search_type = SearchType.TEXT

    print(f"query:{query}")
    response = await search_client.search(
        search_text=query,
        query_type="semantic" if use_semantic_reranker else "simple",
        # query_type=QueryType.SIMPLE,
        # query_caption=QueryCaptionType.NONE,
        # query_answer=QueryAnswerType.NONE,
        # # search_fields="*"
        include_total_count=True,
        # minimum_coverage=0.5,
        # search_mode="all",
        top=sources_to_include,
        select="description,hotelName,tags",
        semantic_configuration_name="my-semantic-config" if use_semantic_reranker else None,
    )

    pprint(f"response:{response}")

    # async for d in response:
    #     pprint(f"d:{d}")

    # a = []
    # async for document in response:
    #     a.append(document)
    #     pprint(document)

    # print(f"a:{a}")


#     第一次遍歷：

# 你使用 async for 迭代了 response，並打印出每個項目。
# 這次迭代已經耗盡了所有數據。
# 第二次遍歷：

# 你再次嘗試使用列表推導式 [document async for document in response] 來遍歷 response。
# 由於 response 在第一次迭代後已經被耗盡，第二次迭代將不會產生任何結果，因此返回的是一個空列表。
    return [document async for document in response]

    """
        [
            {
                'tags': ['concierge', 'view', '24-hour front desk service'],
                'description': 'Sublime Cliff Hotel is located in the heart of the historic center of Sublime in an extremely vibrant and lively area within short walking distance to the sites and landmarks of
                                the city and is surrounded by the extraordinary beauty of churches, buildings, shops and monuments. Sublime Cliff is part of a lovingly restored 1800 palace.',
                'hotelName': 'Sublime Cliff Hotel',
                '@search.score': 0.3185051,
                '@search.reranker_score': 1.673100471496582,
                '@search.highlights': None,
                '@search.captions': None
            },
            {
                'tags': ['pool', 'free wifi', 'concierge'],
                'description': 'The hotel is situated in a  nineteenth century plaza, which has been expanded and renovated to the highest architectural standards to create a modern, functional and first-class
                                hotel in which art and unique historical elements coexist with the most modern comforts.',
                'hotelName': 'Twin Dome Motel',
                '@search.score': 1.218107,
                '@search.reranker_score': 1.5735293626785278,
                '@search.highlights': None,
                '@search.captions': None
            },
            {
                'tags': ['air conditioning', 'bar', 'continental breakfast'],
                'description': "The Hotel stands out for its gastronomic excellence under the management of William Dough, who advises on and oversees all of the Hotel's restaurant services.",
                'hotelName': 'Triple Landscape Hotel',
                '@search.score': 1.2959795,
                '@search.reranker_score': 1.5513173341751099,
                '@search.highlights': None,
                '@search.captions': None
            },
            {
                'tags': ['pool', 'air conditioning', 'concierge'],
                'description': "The hotel is ideally located on the main commercial artery of the city in the heart of New York. A few minutes away is Time's Square and the historic centre of the city, as well
                                as other places of interest that make New York one of America's most attractive and cosmopolitan cities.",
                'hotelName': 'Secret Point Motel',
                '@search.score': 1.0247573,
                '@search.reranker_score': 1.4280023574829102,
                '@search.highlights': None,
                '@search.captions': None
            }
        ]
        """

class ChatThread:
    def __init__(self):
        self.messages = []
        self.search_results = []

    def append_message(self, role:str, message:str):
        self.messages.append(({
            "role":role,
            "content":message
        }))

    async def append_grounded_message(self, search_client:SearchClient, query:str, search_type:SearchType, use_semantic_reranker:bool=True, sources_to_include:int=5):
        sources = await get_source(search_client, query, search_type, use_semantic_reranker, sources_to_include)
        print(f"sources: {sources}")
        sources_formatted = "\n".join([f'{document["hotelName"]}:{document["description"]}:{document["tags"]}' for document in sources])
        print(f"sources_formatted: {sources_formatted}")
        # prompt
        self.append_message(role="user", message=GROUNDED_PROMPT.format(query=query, sources=sources_formatted))
        # query
        self.search_results.append(
            {
                "message_index":len(self.messages)-1,
                "query":query,
                "sources":sources
            }
        )

        """ sources_formatted
        Sublime Cliff Hotel:Sublime Cliff Hotel is located in the heart of the historic center of Sublime in an extremely vibrant and lively area within short walking distance to the sites and landmarks of the
        city and is surrounded by the extraordinary beauty of churches, buildings, shops and monuments. Sublime Cliff is part of a lovingly restored 1800 palace.:['concierge', 'view', '24-hour front desk
        service']
        Twin Dome Motel:The hotel is situated in a  nineteenth century plaza, which has been expanded and renovated to the highest architectural standards to create a modern, functional and first-class hotel in
        which art and unique historical elements coexist with the most modern comforts.:['pool', 'free wifi', 'concierge']
        Triple Landscape Hotel:The Hotel stands out for its gastronomic excellence under the management of William Dough, who advises on and oversees all of the Hotel's restaurant services.:['air conditioning',
        'bar', 'continental breakfast']
        Secret Point Motel:The hotel is ideally located on the main commercial artery of the city in the heart of New York. A few minutes away is Time's Square and the historic centre of the city, as well as
        other places of interest that make New York one of America's most attractive and cosmopolitan cities.:['pool', 'air conditioning', 'concierge']
        """

        """ messages
        [
            {
                'role': 'user',
                'content': "\nYou are a friendly assistant that recommends hotels based on activities and amentities.\nAnswer the query using only the sources provided below in a friendly and concise bulleted
                manner.\nAnswer only with the facts listed in the list of sources below.\nIf there isn't enough information below, say you don't know.\nDo not generate answers that don't use the sources
                below.\nQuery:Can your recommend a few hotels near the ocean with branch access and good views\nSources:\nSublime Cliff Hotel:Sublime Cliff Hotel is located in the heart of the historic center of
                Sublime in an extremely vibrant and lively area within short walking distance to the sites and landmarks of the city and is surrounded by the extraordinary beauty of churches, buildings, shops and
                monuments. Sublime Cliff is part of a lovingly restored 1800 palace.:['concierge', 'view', '24-hour front desk service']\nTwin Dome Motel:The hotel is situated in a  nineteenth century plaza, which has
                been expanded and renovated to the highest architectural standards to create a modern, functional and first-class hotel in which art and unique historical elements coexist with the most modern
                comforts.:['pool', 'free wifi', 'concierge']\nTriple Landscape Hotel:The Hotel stands out for its gastronomic excellence under the management of William Dough, who advises on and oversees all of the
                Hotel's restaurant services.:['air conditioning', 'bar', 'continental breakfast']\nSecret Point Motel:The hotel is ideally located on the main commercial artery of the city in the heart of New York. A
                few minutes away is Time's Square and the historic centre of the city, as well as other places of interest that make New York one of America's most attractive and cosmopolitan cities.:['pool', 'air
                conditioning', 'concierge']\n"
            }
        ]
        """

        """ search_results
        [
            {
                'message_index': 0,
                'query': 'Can your recommend a few hotels near the ocean with branch access and good views',
                'sources': [
                    {
                        'hotelName': 'Sublime Cliff Hotel',
                        'description': 'Sublime Cliff Hotel is located in the heart of the historic center of Sublime in an extremely vibrant and lively area within short walking distance to the sites and
                                    landmarks of the city and is surrounded by the extraordinary beauty of churches, buildings, shops and monuments. Sublime Cliff is part of a lovingly restored 1800 palace.',
                        'tags': ['concierge', 'view', '24-hour front desk service'],
                        '@search.score': 0.3185051,
                        '@search.reranker_score': 1.673100471496582,
                        '@search.highlights': None,
                        '@search.captions': None
                    },
                    {
                        'hotelName': 'Twin Dome Motel',
                        'description': 'The hotel is situated in a  nineteenth century plaza, which has been expanded and renovated to the highest architectural standards to create a modern, functional and
                                    first-class hotel in which art and unique historical elements coexist with the most modern comforts.',
                        'tags': ['pool', 'free wifi', 'concierge'],
                        '@search.score': 1.218107,
                        '@search.reranker_score': 1.5735293626785278,
                        '@search.highlights': None,
                        '@search.captions': None
                    },
                    {
                        'hotelName': 'Triple Landscape Hotel',
                        'description': "The Hotel stands out for its gastronomic excellence under the management of William Dough, who advises on and oversees all of the Hotel's restaurant services.",
                        'tags': ['air conditioning', 'bar', 'continental breakfast'],
                        '@search.score': 1.2959795,
                        '@search.reranker_score': 1.5513173341751099,
                        '@search.highlights': None,
                        '@search.captions': None
                    },
                    {
                        'hotelName': 'Secret Point Motel',
                        'description': "The hotel is ideally located on the main commercial artery of the city in the heart of New York. A few minutes away is Time's Square and the historic centre of the city,
                                    as well as other places of interest that make New York one of America's most attractive and cosmopolitan cities.",
                        'tags': ['pool', 'air conditioning', 'concierge'],
                        '@search.score': 1.0247573,
                        '@search.reranker_score': 1.4280023574829102,
                        '@search.highlights': None,
                        '@search.captions': None
                    }
                ]
            }
        ]
        """

    async def get_openai_response(self, openai_client:AsyncAzureOpenAI, model:str):
        response = await openai_client.chat.completions.create(
            messages=self.messages,
            model=model
        )
        self.append_message(role="assistant", message=response.choices[0].message)


    def get_last_message(self) -> Optional[object]:
        return self.messages[-1] if len(self.messages) > 0 else None

    def get_last_message_source(self) -> Optional[List[object]]:
        return self.search_results[-1]["sources"] if len(self.search_results) > 0 else None

chat_thread = ChatThread()
chat_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_FOUR")


def _delete_index():
    try:
        result = search_index_client.delete_index(index_name)
        print(f"Index {index_name} deleted")
    except Exception as ex:
        logging.error(ex)

def _get_index():
    try:
        result = search_index_client.get_index(index_name)
        print(f"Index {index_name} exists")
    except Exception as ex:
        logging.error(ex)

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
            SimpleField(name="lastRenovationDate", type=SearchFieldDataType.DateTimeOffset, facetable=True, filterable=True, sortable=True),
            SimpleField(name="rating", type=SearchFieldDataType.Double, facetable=True, filterable=True, sortable=True),
            ComplexField(name="address", fields=[
                SearchableField(name="streetAddress", type=SearchFieldDataType.String),
                SearchableField(name="city", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True),
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
            text_weights=TextWeights(weights={"description":1.5})
        )
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        suggester = [{'name':'sg','source_fields':['tags','address/city','address/country']}]

        index = SearchIndex(
            name=index_name,
            fields=fields,
            suggesters=suggester,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options,
            semantic_search=semantic_search
        )

        result = search_index_client.create_index(index)
        print(f"{result.name} created")

    except Exception as ex:
        logging.error(ex)

async def _upload_document():

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

    try:
        result = await search_client.upload_documents(documents=documents)
        print(f"Upload of new document succeeded: {result[0].succeeded}")
    except Exception as ex:
        logging.error(ex)

async def main():

    async with search_client:
        await chat_thread.append_grounded_message(
            search_client=search_client,
            query="Can your recommend a few hotels near the sublime",
            search_type=SearchType.TEXT,
            use_semantic_reranker=use_semantic_reranker,
            sources_to_include=sources_to_include
        )

    async with client:
        await chat_thread.get_openai_response(openai_client=client, model=chat_deployment)

    pprint(chat_thread.get_last_message())

    pprint(chat_thread.messages)



async def main2():

    _delete_index()
    _create_index()
    async with search_client:
        await _upload_document()

if __name__ == "__main__":
    # asyncio.run(main())
    # _delete_index()
    # _create_index()
    # await _upload_document()

    # asyncio.run(main2())
    asyncio.run(main())
