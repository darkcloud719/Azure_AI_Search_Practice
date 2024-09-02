import os,json,logging,sys
import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType, QueryCaptionResult, QueryAnswerResult, VectorizedQuery, VectorizableTextQuery
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
    SearchField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    # AzureOpenAIVectorizer,
    # AzureOpenAIParameters
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
indexer_name = "shenghuai-indexer999"
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
search_index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
search_indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY NOT FOUND"
assert os.getenv("OPENAI_API_VERSION"), "OPENAI_API_VERSION NOT FOUND"
assert os.getenv("AZURE_OPENAI_ENDPOINT"), "AZURE_OPENAI_API_ENDPOINT NOT FOUND"
assert os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS"), "AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS NOT FOUND"

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_version = os.getenv("OPENAI_API_VERSION")
openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = "azure"

def _delete_index():

    try:
        result = search_index_client.delete_index(index_name)
        print(f"index {index_name} deleted")
    except Exception as ex:
        logging.error(ex)

def _get_index():
    
    try:
        result = search_index_client.get_index(index_name)
        print(f"index {index_name} exists")
    except Exception as ex:
        logging.error(ex)

def _create_index():

    try:
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="category", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchField(name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=1536,
                vector_search_profile_name="myHnswProfile",
                hidden=False
            )
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
        suggester = [{'name':'sg','source_fields':['category','content']}]

        vector_search = VectorSearch(
            # algorithm_configurations=[
            #     VectorSearchAlgorithmConfiguration(
            #         name="my-vector-config",
            #         kind="Hnsw",
            #         hnsw_parameters={
            #             "m":4,
            #             "efConstruction":400,
            #             "efSearch":500,
            #             "metric":"cosine"
            #         }
            #     )
            # ],
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="myHnsw"
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name="myHnswProfile",
                    algorithm_configuration_name="myHnsw"
                )
            ]
            # algorithms=[
            #     HnswAlgorithmConfiguration(
            #         name="myHnsw"
            #     ),
            # ],
            # profiles=[
            #     VectorSearchProfile(
            #         name="myHnswProfile",
            #         algorithm_configuration="myHnsw",
            #         vectorizer="myVectorizer"
            #     )
            # ],
            # vectorizers=[
            #     AzureOpenAIVectorizer(
            #         name="myVectorizer",
            #         azure_open_ai_parameters=AzureOpenAIParameters(
            #             resource_uri=os.getenv("OPENAI_API_ENDPOINT"),
            #             deployment_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_ENBEDDINGS"),
            #             model_name=os.getenv("AZURE_OPENAI_MODEL_NAME_FOR_EMBEDDINGS"),
            #             api_key=os.getenv("OPENAI_API_KEY")
            #         )
            #     )
            # ]
            
        )

        index = SearchIndex(
            name=index_name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options,
            vector_search=vector_search
            # suggesters=suggester,
            # semantic_search=semantic_search
        )        

        search_index_client.create_index(index)
        print(f"{index_name} created")
    
    except Exception as ex:
        logging.error(ex)

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(5))
def generate_embeddings(text):

    response = openai.embeddings.create(
        input=text,
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS")
    )

    embeddings = response.data[0].embedding
    return embeddings

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(5))
def _create_embeddings_with_retry(inputs):

    for attempt in range(len(inputs)-1):
        response = openai.embeddings.create(
            input=inputs,
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS"),
            dimensions=1536
        )

        print(f"Embedding created successfully on attempt {attempt}")

        return [item.embedding for item in response.data]
   

def _embed_text_data_from_json():

    try:
        path = os.path.join(os.path.dirname(__file__), "text-sample.json")
        with open(path,"r",encoding="utf-8") as file:
            input_data = json.load(file)

        contents = [item['content'] for item in input_data]

        content_embeddings = _create_embeddings_with_retry(contents)

        for i, item in enumerate(input_data):
            item['content_vector'] = content_embeddings[i]

        output_path = os.path.join('.','output','docVectors1.json')
        output_directory = os.path.dirname(output_path)
        print(f"output_directory: {output_directory}")
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        with open(output_path,"w",encoding="utf-8") as file:
            json.dump(input_data, file, indent=4, ensure_ascii=False)
        print(f"Embedding data saved to {output_path}")
    except Exception as ex:
        logging.error(ex)

def _upload_vector_data_to_index():

    path = os.path.join(os.path.dirname(__file__),"output","docVectors1.json")
    with open(path,"r",encoding="utf-8") as file:
        obj = json.load(file)

        try:
            result = search_client.upload_documents(documents=obj)
            # print(f"Upload result: {result} uploaded")
        except Exception as ex:
            logging.error(ex)

# def _get_text_vector():
#     embedding = openai.embeddings.create(input=["hello world"], model=os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS"))
#     pprint(embedding)

# def corssfield_vector_search():

#     vector_query = VectorizableTextQuery(text="",k_nearest_neighbors=3, fields=["contentVector,titleVector"])

#     results = search_client.search(
#         search_text=None,
#         vector_queries=[vector_query],
#         select=["title","content","category"],
#     )

#     for index, result in enumerate(results):
#         for key, value in result.items():
#             print(f"{key}:{value}")

if __name__ == "__main__":

    # _get_text_vector()
    _delete_index()
    _create_index()
    # _embed_text_data_from_json()
    _upload_vector_data_to_index()