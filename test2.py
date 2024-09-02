import os,json,logging,sys
import pandas as pd
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient, SearchIndexingBufferedSender
from azure.search.documents.models import QueryType, QueryCaptionResult, QueryAnswerResult, VectorizableTextQuery
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
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIParameters,
)
from dotenv import load_dotenv
from typing import List
from rich import print as pprint
from openai import AzureOpenAI

load_dotenv()

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is not set in .env file"
assert os.getenv("OPENAI_API_VERSION"), "OPENAI_API_VERSION is not set in .env file"
assert os.getenv("AZURE_SEARCH_API_KEY"), "AZURE_SEARCH_API_KEY is not set in .env file"
assert os.getenv("AZURE_OPENAI_ENDPOINT"), "AZURE_OPENAI_ENDPOINT is not set in .env file"
assert os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS"), "AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS is not set in .env file"
assert os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_FOUR"), "AZURE_OPENAI_DEPLOYMENT_FOR_FOUR is not set in .env file"

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
credential = AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
index_name = "test0902_2"
azure_openai_model = "gpt-4"
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_key = os.getenv("OPENAI_API_KEY")
azure_openai_embedding_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS")
azure_openai_api_version = os.getenv("OPENAI_API_VERSION")
azure_openai_chatgpt_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_FOR_FOUR")

# OPENAI_API_KEY="d3848815be05474ba298ee62f4850740"
# OPENAI_API_VERSION="2024-02-15-preview"
# AZURE_OPENAI_ENDPOINT="https://shenghuaiopenai2.openai.azure.com/"
# AZURE_OPENAI_DEPLOYMENT="gpt-35-turbo"
# AZURE_OPENAI_DEPLOYMENT_FOR_FOUR="gpt-4-turbo"
# AZURE_OPENAI_DEPLOYMENT_FOR_EMBEDDINGS = "text-embedding-ada-002"

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "test0902_2"

# search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
# search_index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
# search_indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
# searchIndexingBufferedSender = SearchIndexingBufferedSender(service_endpoint, index_name, AzureKeyCredential(key))

# print(azure_openai_key)

client = AzureOpenAI(
    api_version = azure_openai_api_version,
    azure_endpoint = azure_openai_endpoint,
    api_key = azure_openai_key,
    # azure_deployment = azure_openai_chatgpt_deployment
)

def delete_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.delete_index(index_name)
            print(f"Delete Index {index_name} successfully")
    except Exception as ex:
        logging.error(ex)

def get_index():
    try:
        # with search_index_client:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.get_index(index_name)
            print(f"Get Index {index_name} successfully")
    except Exception as ex:
        logging.error(ex)

    # result = search_index_client.get_index(index_name)


def create_index():
    try:
        fields = [
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
                        api_key=azure_openai_key,
                        # azure_openai_api_version=azure_openai_api_version
                    )
                )
            ]
        )

        scoring_profiles:List[ScoringProfile] = []
        scoring_profile = ScoringProfile(
            name="MyProfile",
            text_weights=TextWeights(weights={"title":1.5})
        )
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        suggester = [{'name':'sg','source_fields':['title','content']}]

        semantic_config = SemanticConfiguration(
            name="my-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="content")]
            )
        )

        # Create the semantic settings with the configuration
        semantic_search = SemanticSearch(configurations=[semantic_config])

        # Create the search index with the semantic settings

        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            index = SearchIndex(
                name=index_name,
                fields=fields,
                vector_search=vector_search,
                semantic_search=semantic_search,
                # cors_options=cors_options,
                # suggesters=suggester,
                # scoring_profiles=scoring_profiles
            )

            result = search_index_client.create_index(index)
            print(f"{result.name} created")
    
    except Exception as ex:
        logging.error(ex)

def upload_document():

    try:
        output_path = os.path.join('.','output','docVectors.json')
        output_directory = os.path.dirname(output_path)

        if not os.path.exists(output_path):
            os.makedirs(output_directory)
        with open(output_path,'r', encoding='utf-8') as file:
            documents = json.load(file)
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            result = search_client.upload_documents(documents=documents)
            print(f"Uploaded {len(documents)} documents")
    except Exception as ex:
        logging.error(ex)

def upload_document_by_batch():
    try:
        output_path = os.path.join('.','output','docVectors.json')
        output_directory = os.path.dirname(output_path)

        if not os.path.exists(output_path):
            os.makedirs(output_directory)
            # Upload some documents to the index
        with open(output_path,'r', encoding='utf-8') as file:
            documents = json.load(file)

        with SearchIndexingBufferedSender(service_endpoint, index_name, AzureKeyCredential(key)) as batch_client:
            batch_client.upload_documents(documents=documents)

    except Exception as ex:
        logging.error(ex)
            

def export_embeddings_to_json():

    output_path = os.path.join('.','output','docVectors.json')

    if not os.path.exists(output_path):
        # Generate Document Embeddings using OpenAI Ada002
        # Read the text-sample.json
        
        path = os.path.join(os.path.dirname(__file__), "text-sample.json")
        with open(path,'r',encoding='utf-8') as file:
            input_data = json.load(file)

        titles = [item['title'] for item in input_data]
        content = [item['content'] for item in input_data]
        title_response = client.embeddings.create(input=titles, model=azure_openai_embedding_deployment)
        title_embeddings = [item.embedding for item in title_response.data]
        content_response = client.embeddings.create(input=content, model=azure_openai_embedding_deployment)
        content_embeddings = [item.embedding for item in content_response.data]

        for i,item in enumerate(input_data):
            title = item['title']
            content = item['content']
            item['titleVector'] = title_embeddings[i]
            item['contentVector'] = content_embeddings[i]

        # Output embeddings to decVectors.json file
        output_directory = os.path.dirname(output_path)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        with open(output_path, 'w', encoding="utf-8") as file:
            json.dump(input_data, file, indent=4, ensure_ascii=False)

def hybrid_search(search_client:SearchClient, query:str) -> pd.DataFrame:
    
    results = search_client.search(
        search_text=query,
        vector_queries=[
            VectorizableTextQuery(
                text=query,
                k_nearest_neighbors=50,
                fields="contentVector"
            ),
        ],
        top=3,
        select="id, title, content",
        search_fields=["content"]
    )

    data = [[result["id"], result["title"], result["content"], result["@search.score"]] for result in results]

    return pd.DataFrame(data, columns=["id","title","content","@search.score"])

def rewrite_query(openai_client:AzureOpenAI, query:str):

    REWRITE_PROMPT = """
    You are a helpful assistant. You help users search for the answers to their questions.
    You have access to Azure AI Search index with 100's of documents. Rewrite the following question into 3 useful search queries to find the most relevant documents.
    Always output a JSON object in the following format:
    ===
    Input: "scalable storage solution"
    Output: {"queires":["what is a scalable storage solution in Azure", "how to create a scalable storage solution", "steps to create a scalable storage solution"]}
    ===
    """

    response = openai_client.chat.completions.create(
        model=azure_openai_chatgpt_deployment,
        response_format={"type":"json_object"},
        messages=[
            {"role":"system","content":REWRITE_PROMPT},
            {"role":"user","content": f"Input:{query}"}
        ]
    )

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as ex:
        # log the error and raise an exception to the caller
        logging.error(f"JSON decoding error: {ex}")
        raise

def query_rewrite_manual_rrf(search_client: SearchClient, openai_client: AzureOpenAI, query:str) -> pd.DataFrame:
    rewritten_queries = rewrite_query(openai_client, query)

    results = pd.concat([hybrid_search(search_client,rewritten_query) for rewritten_query in rewritten_queries["queries"]], axis=0)
    def rrf_score(row: pd.Series) -> float:
        score = 0.0
        k = 60,
        for rank, df_row in results.iterrows():
            if df_row["id"] == row["id"]:
                score += 1.0 / (k + rank)
        return score
    
    results["rrf_score"] = results.apply(rrf_score, axis=1)
    return rewritten_queries, results.drop_duplicates(subset=["id"]).sort_values(by="rrf_score", ascending=False)


if __name__ == "__main__":
    # export_embeddings_to_json()
    # create_index()
    # upload_document()
    # get_index()
    # hybrid_search(search_client, "scalable storage solution")
    # delete_index()
    # create_index()
    # upload_document()
    # with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
    #     a = hybrid_search(search_client, "scalable storage solution")
    #     print(type(a))
    a = rewrite_query(client, "what is azure search?")
    print(a)

