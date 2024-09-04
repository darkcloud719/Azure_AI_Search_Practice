import os,json,logging,sys
from openai import AzureOpenAI
from dotenv import load_dotenv
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
    AzureOpenAIVectorizer,
    AzureOpenAIParameters
)
from typing import List

load_dotenv()

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is not set in .env file"
assert os.getenv("OPENAI_API_VERSION"), "OPENAI_API_VERSION is not set in .env file"
assert os.getenv("AZURE_SEARCH_API_KEY"), "AZURE_SEARCH_API_KEY is not set in .env file"
assert os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT"), "AZURE_SEARCH_SERVICE_ENDPOINT is not set in .env file"
assert os.getenv("AZURE_OPENAI_ENDPOINT"), "AZURE_OPENAI_ENDPOINT is not set in .env file"
assert os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_FOUR"), "AZURE_SEARCH_DEPLOYMENT_FOR_FOUR is not set in .env file"
assert os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS"), "AZURE_SEARCH_DEPLOYMENT_FOR_EMBEDDINGS is not set in .env file"

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
credential = AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
index_name = "test0905"
azure_openai_model = "gpt-4"
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_key = os.getenv("OPENAI_API_KEY")
azure_openai_embedding_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS")
azure_openai_api_version = os.getenv("OPENAPI_API_VERSION")
azure_openai_chatgpt_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_FOUR")

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "test0905"

client = AzureOpenAI(
    azure_endpoint=azure_openai_endpoint,
    api_key=azure_openai_key,
    api_version=azure_openai_api_version,
)


def create_index():
    try:
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchableField(name="category", type=SearchFieldDataType.String, filterable=True),
            SearchField(name="titleVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
            SearchField(name="contentVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile")
        ]

        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(name="myHnsw")
            ],
            profiles=[
                VectorSearchProfile(
                    name="myHnswProfile",
                    algorithm_configuration_name="myHnsw",
                    vectorizer="myVectorizer"
                )
            ],
            vectorizers=[
                AzureOpenAIVectorizer(
                    name="myVectorizer",
                    azure_open_ai_parameters=AzureOpenAIParameters(
                        resource_uri=azure_openai_endpoint,
                        deployment_id=azure_openai_embedding_deployment,
                        model_name=azure_openai_embedding_deployment,
                        api_key=azure_openai_key,
                        # azure_openai_api_version=azure_openai_api_version
                    )
                )
            ]
        )

        scoring_profiles:List[ScoringProfile] = []
        scoring_profile = ScoringProfile(name="MyProfile",text_weights=TextWeights(weights={"title":1.5}))
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        suggester = [{'name':'sg','source_fields':['title','content']}]

        semantic_config = SemanticConfiguration(
            name="my-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="title"),
                keywords_fields=[SemanticField(field_name="category")],
                content_fields=[SemanticField(field_name="content")]
            )
        )

        semantic_search = SemanticSearch(configurations=[semantic_config])

        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            index = SearchIndex(
                name=index_name,
                fields=fields,
                cors_otpions=cors_options,
                vector_search=vector_search,
                semantic_search=semantic_search
            )

            result = search_index_client.create_index(index)
            print(f"{result.name} created")

    except Exception as ex:
        logging.error(ex)


def export_embeddings_to_json():
    
    try:
        path = os.path.join(os.path.dirname(__file__),"text-sample.json")
        with open(path,"r",encoding="utf-8") as file:
            input_data = json.load(file)

        titles = [item['title'] for item in input_data]
        content = [item['content'] for item in input_data]
        title_response = client.embeddings.create(input=titles, model=azure_openai_embedding_deployment, dimensions=1536)
        title_embeddings = [item.embedding for item in title_response.data]
        content_response = client.embeddings.create(input=content, model=azure_openai_embedding_deployment, dimensions=1536)
        content_embeddings = [item.embedding for item in content_response.data]

        for i,item in enumerate(input_data):
            title = item['title']
            content = item['content']
            item['titleVector'] = title_embeddings[i]
            item['contentVector'] = content_embeddings[i]

        output_path = os.path.join('.','output','docVectors0905.json')
        output_directory = os.path.dirname(output_path)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        with open(output_path,"w",encoding="utf-8") as file:
            json.dump(input_data, file, indent=4, ensure_ascii=False)
    except Exception as ex:
        logging.error(ex)

def upload_documents():
    try:
        output_path = os.path.join('.','output','docVectors0905.json')
        output_directory = os.path.dirname(output_path)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        with open(output_path,'r',encoding='utf-8') as file:
            documents = json.load(file)
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            result= search_client.upload_documents(documents=documents)
            print(f"Uploaded {len(documents)} documents")
    except Exception as ex:
        logging.error(ex)



if __name__ == "__main__":
    # export_embeddings_to_json()
    # _delete_index()
    # create_index()
    upload_documents()