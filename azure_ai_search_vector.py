import os,json,logging,sys
from openai import AzureOpenAI
from dotenv import load_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient, SearchIndexingBufferedSender
from azure.search.documents.models import QueryType, QueryCaptionType, QueryAnswerType, QueryCaptionResult, QueryAnswerResult, VectorizableTextQuery, VectorizedQuery, VectorFilterMode
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
from rich import print as pprint

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

def update_index():

    try:
        # 如果沒有vectorizer，無法用VectorizableTextQuery
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


        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            index = search_index_client.get_index(index_name)
            index.vector_search = vector_search

            search_index_client.create_or_update_index(index)

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

def upload_documents_by_indexingbufferedsender():
    try:
        output_path = os.path.join('.','output','docVectors0905.json')
        with open(output_path,'r',encoding='utf-8') as file:
            documents = json.load(file)

        with SearchIndexingBufferedSender(
            endpoint=service_endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(key)
        ) as batch_client:
            batch_client.upload_documents(documents=documents)
        print(f"Uploaded {len(documents)} documents in total")
    except Exception as ex:
        logging.error(ex)

def search_documents_by_similarity():
    # Pure Vector Search
    try:
        query = "tools for software development"
        embedding = client.embeddings.create(input=query, model=azure_openai_embedding_deployment, dimensions=1536).data[0].embedding

        vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=3, fields="contentVector")
        # pprint(vector_query)
        # vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=3, fields="contentVector")
        pprint(vector_query)

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                select=["title","content","category"]
            )

            for result in results:
                for result_key,value in result.items():
                    print(f"{result_key}:{value}")
                print("\n\n")
    except Exception as ex:
        logging.error(ex)

# exact knn searc
def search_documents_by_knn():
    try:
        query = "tools for software development"

        vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=3, fields="contentVector", exhaustive=True)

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                select=["title","content","category"]
            )

            for result in results:
                for result_key,value in result.items():
                    print(f"{result_key}:{value}")
                print("\n\n")

    except Exception as ex:
        logging.error(ex)

def search_documents_by_cross_field():
    try:
        query = "tools for software development"

        vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=3, fields="contentVector, titleVector")

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type="simple",
                search_text=None,
                vector_queries=[vector_query],
                select=["title","content","category"]
            )

            for result in results:
                for result_key,value in result.items():
                    print(f"{result_key}:{value}")
                print("\n\n")

    except Exception as ex:
        logging.error(ex)

def search_documents_by_multi_vector():
    try:
        query = "tools for software development"

        vector_query_1 = VectorizableTextQuery(text=query, k_nearest_neighbors=1, fields="titleVector")
        vector_query_2 = VectorizableTextQuery(text=query, k_nearest_neighbors=3, fields="contentVector")

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type="simple",
                # search_text="devops",
                vector_queries=[vector_query_1, vector_query_2],
                select=["title","content","category"],
                # top=2
            )

            for result in results:
                for result_key, value in result.items():
                    print(f"{result_key}:{value}")
                print("\n\n")
    except Exception as ex:
        logging.error(ex)

def search_documents_by_weighted_multi_vector():
    try:
        query = "tools for software development"

        vector_query_1 = VectorizableTextQuery(text=query, k_nearest_neighbors=1, fields="titleVector", weight=2)
        vector_query_2 = VectorizableTextQuery(text=query, k_nearest_neighbors=3, fields="contentVector", weight=0.5)
        
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type="simple",
                vector_queries=[vector_query_1, vector_query_2],
                select=["title","content","category"]
            )

            for result in results:
                for result_key, value in result.items():
                    print(f"{result_key}:{value}")
                print("\n\n")

    except Exception as ex:
        logging.error(ex)

def search_documents_by_filter():
    try:
        query = "tools for software development"

        vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=3, fields="contentVector")

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                # vector_filter_mode=VectorFilterMode.PRE_FILTER,
                vector_filter_mode=VectorFilterMode.POST_FILTER,
                filter="category eq 'Developer Tools'",
                select=["title","content","category"]
            )

            for result in results:
                for result_key, value in result.items():
                    print(f"{result_key}:{value}")
                print("\n\n")

    except Exception as ex:
        logging.error(ex)

def hybrid_search():
    try:
        query = "scalable storage solution"

        vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=3, fields="contentVector")

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type="simple",
                search_text=query,
                vector_queries=[vector_query],
                select=["title","content","category"],
                top=3
            )

            for result in results:
                for result_key, value in result.items():
                    print(f"{result_key}:{value}")
    except Exception as ex:
        logging.error(ex)

def hybrid_search_with_weights():
    try:
        query = "scalable storage solution"

        vector_query = VectorizableTextQuery(text=query, k_nearest_neightbors=3, fields="contentVector", weight=0.2)

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type="simple",
                search_text=query,
                vector_queries=[vector_query],
                select=["title","content","category"],
                top=3
            )

            for result in results:
                for result_key, value in result.items():
                    print(f"{result_key}:{value}")
    
    except Exception as ex:
        logging.error(ex)

def semantic_hybrid_search():
    try:
        query = "what is azure search?"

        vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=3, fields="contentVector")

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type=QueryType.SEMANTIC,
                semantic_configuration_name="my-semantic-config",
                query_caption=QueryCaptionType.EXTRACTIVE, 
                query_answer=QueryAnswerType.EXTRACTIVE,
                search_text=query,
                vector_queries=[vector_query],
                top=3
            )
            
            # 一組
            semantic_answers = results.get_answers()
            for answer in semantic_answers:
                if answer.highlights:
                    print(f"Semantic Answer: {answer.highlights}")
                else:
                    print(f"Semantic Answer: {answer.text}")
                print(f"Semantic Answer Score: {answer.score}\n")

            for result in results:
                for result_key, value in result.items():
                    print(f"{result_key}:{value}")

                # 每個top都有
                captions = result["@search.captions"]
                if captions:
                    caption = captions[0]
                    if caption.highlights:
                        print(f"Caption: {caption.highlights}\n")
                    else:
                        print(f"Caption: {caption.text}\n")

    except Exception as ex:
        logging.error(ex)
            

if __name__ == "__main__":
    # export_embeddings_to_json()
    # _delete_index()
    # create_index()
    # upload_documents()
    # search_documents_by_similarity()
    # search_documents_by_knn()
    # search_documents_by_cross_field()
    # search_documents_by_multi_vector()
    # search_documents_by_weighted_multi_vector()
    # search_documents_by_filter()    
    # hybrid_search()
    # hybrid_search_with_weights()
    semantic_hybrid_search()
    # update_index()


#     其實兩種 VectorizableTextQuery 查詢中，都使用了 KNN（k-Nearest Neighbors）搜索算法，只不過它們的處理方式不同。

# VectorizableTextQuery(text=query, k_nearest_neighbors=3, fields="contentVector")

# 這個查詢使用了近似 KNN 搜索，也就是依賴像 HNSW（Hierarchical Navigable Small World）等算法進行快速搜索。它根據相似性來查找最近的3個結果，但並不保證找到最精確的鄰居，因為它使用了近似搜索來優化速度。
# VectorizableTextQuery(text=query, k_nearest_neighbors=3, fields="contentVector", exhaustive=True)

# 加上 exhaustive=True，表示執行完全 KNN 搜索。這會遍歷索引中的所有向量，確保找到最精確的3個鄰居，而不是僅依賴於加速的近似算法。這樣搜索結果會更加精確，但會更耗時。
# 所以，exhaustive=True 是在進行更精確的搜索，而不加 exhaustive 會使用加速但相對不那麼精確的近似搜索​(
# MS Learn
# )​(
# MS Learn
# )​(
# MS Learn
# )。



# 近似 KNN（Approximate KNN） 和 完全 KNN（Exact KNN） 都是用來查找與查詢向量最相似的向量，但它們的處理方式和性能有很大差異：

# 近似 KNN (Approximate KNN):

# 代表：它使用加速算法（例如 HNSW）來快速找到與查詢向量最接近的 K 個鄰居。這種方法在大數據集上能顯著提高查詢速度。
# 特點：雖然速度快，但結果並不一定是最精確的。它在犧牲一點精度的情況下提供性能提升，特別適合大規模數據集，因為它避免了逐一比較所有向量。
# 應用場景：通常用於搜索速度要求高但精度可以稍微妥協的場景，比如即時搜索或推薦系統。
# 完全 KNN (Exact KNN):

# 代表：這是一種逐一比較所有索引向量的方式，確保找到與查詢向量最相似的 K 個結果。
# 特點：這種方法保證結果的精確性，但由於需要遍歷所有數據，性能較差，特別是在數據量大的情況下可能變得非常慢。
# 應用場景：適合需要高精度的場景，如精確的數據分析或驗證模型效果，當結果的精度比速度更重要時會使用。
# 總結來說，近似 KNN 是在性能與精度之間取得平衡，適合大規模數據搜索；而 完全 KNN 保證精度，但會帶來更高的計算開銷​(
# MS Learn
# )​(
# MS Learn
# )​(
# MS Learn
# )。