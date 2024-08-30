import os,json,logging,sys
import openai
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
    HnswAlgorithmConfiguration,
    WebApiSkill
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
indexer_name = "shenghuai-indexer997"
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
search_index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
search_indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

def _delete_index():
    try:
        result = search_index_client.delete_index(index_name)
        print(f"Index {index_name} deleted")
    except Exception as ex:
        logging.error(ex)

def _get_index():
    try:
        result = search_index_client.get_index(index_name)
        print(f"{index_name} exists")
    except Exception as ex:
        logging.error(ex)

def _create_index():
    try:

        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="category", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=1536,
                vector_search_profile_name="myHnswProfile",
                hidden=True
            ),
            SearchableField(name="persons", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True),
            SearchableField(name="locations", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True),
            SearchableField(name="organizations", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True),
            SearchableField(name="quantities", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True),
            SearchableField(name="dateTimes", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True),
            SearchableField(name="urls", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True),
            SearchableField(name="emails", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True),
            SearchableField(name="personTypes", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True),
            SearchableField(name="events", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True),
            SearchableField(name="products", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True),
            SearchableField(name="skills", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True),
            SearchableField(name="addresses", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True),
            SearchableField(name="phoneNumbers", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True),
            SearchableField(name="ipAddresses", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True),
            SearchableField(name="keywords", type=SearchFieldDataType.String, filterable=True, facetable=True, collection=True)
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
        scoring_profile = ScoringProfile(name="MyProfile", text_weights=TextWeights(weights={"content":1.5}))
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        suggester = [{'name':'sg','source_fields':['title','category','content']}]

        vector_search = VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
            profiles=[VectorSearchProfile(name="myHnswProfile", algorithm_configuration_name="myHnsw")]
        )

        index = SearchIndex(
            name=index_name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options,
            semantic_search=semantic_search,
            suggesters=suggester,
            vector_search=vector_search
        )

        result = search_index_client.create_index(index)

        print(f"{result.name} created")

        return result

    except Exception as ex:
        logging.error(ex)

def _create_data_source():

    try:
        container = SearchIndexerDataContainer(name="shenghuaicontainer1")

        data_source_connection = SearchIndexerDataSourceConnection(
            name="shenghuai-datasource234",
            type="azureblob",
            connection_string=connection_string,
            container=container
        )

        data_source = search_indexer_client.create_data_source_connection(data_source_connection)

        return data_source
    except Exception as ex:
        logging.error(ex)

def _create_skillset():
    try:
        search_indexer_client.delete_skillset("shenghuai-skillset234")

        inp = InputFieldMappingEntry(name="text", source="/document/content")
        name_output = OutputFieldMappingEntry(name="namedEntities", target_name="namedEntities")
        person_output = OutputFieldMappingEntry(name="persons", target_name="persons")
        locations_output = OutputFieldMappingEntry(name="locations", target_name="locations")
        organizations_output = OutputFieldMappingEntry(name="organizations", target_name="organizations")
        quantities_output = OutputFieldMappingEntry(name="quantities", target_name="quantities")
        dateTimes_output = OutputFieldMappingEntry(name="dateTimes", target_name="dateTimes")
        urls_output = OutputFieldMappingEntry(name="urls", target_name="urls")
        emails_output = OutputFieldMappingEntry(name="emails", target_name="emails")
        personTypes_output = OutputFieldMappingEntry(name="personTypes", target_name="personTypes")
        events_output = OutputFieldMappingEntry(name="events", target_name="events")
        products_output = OutputFieldMappingEntry(name="products", target_name="products")
        skills_output = OutputFieldMappingEntry(name="skills", target_name="skills")
        addresses_output = OutputFieldMappingEntry(name="addresses", target_name="addresses")
        ipAddresses_output = OutputFieldMappingEntry(name="ipAddresses", target_name="ipAddresses")

        merge_output = OutputFieldMappingEntry(name="mergedText", target_name="mergedKeywords")

        person_input = InputFieldMappingEntry(name="text", source="/document/persons")
        locations_input = InputFieldMappingEntry(name="locations", source="/document/locations")
        organizations_input = InputFieldMappingEntry(name="organizations", source="/document/organizations")
        quantities_input = InputFieldMappingEntry(name="quantities", source="/document/quantities")
        dateTimes_input = InputFieldMappingEntry(name="dateTimes", source="/document/dateTimes")
        urls_input = InputFieldMappingEntry(name="urls", source="/document/urls")
        emails_input = InputFieldMappingEntry(name="emails", source="/document/emails")
        personTypes_input = InputFieldMappingEntry(name="personTypes", source="/document/personTypes")
        events_input = InputFieldMappingEntry(name="events", source="/document/events")
        products_input = InputFieldMappingEntry(name="products", source="/document/products")
        skills_input = InputFieldMappingEntry(name="skills", source="/document/skills")
        addresses_input = InputFieldMappingEntry(name="addresses", source="/document/addresses")

        ipAddresses_input = InputFieldMappingEntry(name="ipAddresses", source="/document/ipAddresses")

        func_uri = "https://shcfunctionapp.azurewebsites.net/api/MergeTEst?"

        oai_ws = WebApiSkill(name="custom_web_api_skill",
                         inputs=[person_input, locations_input, organizations_input, quantities_input, dateTimes_input, urls_input, emails_input, personTypes_input, events_input, products_input, skills_input, addresses_input, ipAddresses_input],
                         outputs=[merge_output],
                         uri=func_uri,
                         timeout='PT230S')

        entityRecognitionSkill = EntityRecognitionSkill(
            name="entity-recognition-skill1",
            inputs=[inp],
            outputs=[person_output, locations_output, organizations_output, quantities_output, dateTimes_output, urls_output, emails_output, personTypes_output, events_output, products_output, skills_output, addresses_output, ipAddresses_output],
            default_language_code="zh-Hant"
        )

        skillset = SearchIndexerSkillset(name="my-skillset234", skills=[entityRecognitionSkill, oai_ws], description="Entity Recognition and Custom Web API Skillset")

        result = search_indexer_client.create_skillset(skillset)

        return result
        
    except Exception as ex:
        logging.error(ex)

def sample_indexer_workflow():

    _delete_index()

    skillset_name = _create_skillset().name
    print(f"{skillset_name} is created")

    datasource = _create_data_source().name
    print(f"{datasource} is created")

    ind_name = _create_index().name
    print(f"{ind_name} is created")

    configuration = IndexingParametersConfiguration(parsing_mode="jsonArray", query_timeout=None)

    parameters = IndexingParameters(configuration=configuration)

    indexer = SearchIndexer(
        name=indexer_name,
        data_source_name=datasource,
        target_index_name=ind_name,
        skillset_name=skillset_name,
        parameters=parameters,
        field_mappings=[
            FieldMapping(source_field_name="metadata_storage_path", target_field_name="url"),
            FieldMapping(source_field_name="metadata_storage_name", target_field_name="fileName")
        ],
        output_field_mappings=[
            FieldMapping(source_field_name="/document/persons", target_field_name="persons"),
            FieldMapping(source_field_name="/document/locations", target_field_name="locations"),
            FieldMapping(source_field_name="/document/organizations", target_field_name="organizations"),
            FieldMapping(source_field_name="/document/quantities", target_field_name="quantities"),
            FieldMapping(source_field_name="/document/dateTimes", target_field_name="dateTimes"),
            FieldMapping(source_field_name="/document/urls", target_field_name="urls"),
            FieldMapping(source_field_name="/document/emails", target_field_name="emails"),
            FieldMapping(source_field_name="/document/personTypes", target_field_name="personTypes"),
            FieldMapping(source_field_name="/document/events", target_field_name="events"),
            FieldMapping(source_field_name="/document/products", target_field_name="products"),
            FieldMapping(source_field_name="/document/skills", target_field_name="skills"),
            FieldMapping(source_field_name="/document/addresses", target_field_name="addresses"),
            FieldMapping(source_field_name="/document/ipAddresses", target_field_name="ipAddresses"),
            FieldMapping(source_field_name="/document/mergedKeywords", target_field_name="keywords")
        ]
    )

    search_indexer_client.create_indexer(indexer)

    result = search_indexer_client.get_indexer(indexer_name)

    search_indexer_client.run_indexer(indexer_name)

if __name__ == "__main__":
    # _delete_index()
    # _create_index()

    sample_indexer_workflow()




            