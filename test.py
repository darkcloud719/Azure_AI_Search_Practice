import os,json,logging,sys
from openai import AzureOpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType, QueryCaptionResult, QueryAnswerResult, VectorizedQuery
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
    HnswAlgorithmConfiguration
)
from dotenv import load_dotenv
from typing import List
from rich import print as pprint 

load_dotenv()

assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is not set in .env file"
assert os.getenv("OPENAI_API_VERSION"), "OPENAI_API_VERSION is not set in .env file"
assert os.getenv("AZURE_OPENAI_ENDPOINT"), "AZURE_OPENAI_ENDPOINT is not set in .env file"
assert os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS"), "AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS is not set in .env file"
assert os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_FOUR"), "AZURE_OPENAI_DEPLOYMENT_FOR_FOUR is not set in .env file"


azure_openai_embedding_dimensions = 1536
client = AzureOpenAI(
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key = os.getenv("OPENAI_API_KEY"),
    api_version = os.getenv("OPENAI_API_VERSION"),
    # azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS")
)

path = os.path.join(os.path.dirname(__file__), "text-sample-vector.json")
with open(path, 'r', encoding="utf-8") as file:
    input_data = json.load(file)

titles = [item['title'] for item in input_data]
content = [item['content'] for item in input_data]
title_response = client.embeddings.create(input=titles, model= os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS"), dimensions=azure_openai_embedding_dimensions)
title_embeddings = [item.embedding for item in title_response.data]
content_response = client.embeddings.create(input=content, model=os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS"), dimensions=azure_openai_embedding_dimensions)
content_embeddings = [item.embedding for item in content_response.data]

for i, item in enumerate(input_data):
    title = item['title']
    content = item['content']
    item['titleVector'] = title_embeddings[i]
    item['contentVector'] = content_embeddings[i]

# output_path = os.path.join('..','output','docVectorstest.json')
# output_director