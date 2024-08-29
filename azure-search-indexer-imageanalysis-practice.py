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
index_name = "test0819i"
indexer_name = "shenghuai-indexer998"
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
        print(f"Index {index_name} exists")
    except Exception as ex:
        logging.error(ex)

def _create_index():
    try:
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True),
            SimpleField(name="file_name", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="url", type=SearchFieldDataType.String),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchableField(name="adult",
                fields=[
                    SimpleField(name="isAdultContent", type=SearchFieldDataType.Boolean, filterable=True, facetable=True),
                    SimpleField(name="isGoryContent", type=SearchFieldDataType.Boolean, filterable=True, facetable=True),
                    SimpleField(name="isRacyContent", type=SearchFieldDataType.Boolean, filterable=True, facetable=True),
                    SimpleField(name="adultScore", type=SearchFieldDataType.Double, filterable=True, facetable=True),
                    SimpleField(name="goreScore", type=SearchFieldDataType.Double),
                    SimpleField(name="racyScore", type=SearchFieldDataType.Double)
                ],
                collection=True
            ),
            ComplexField(name="brands",
                fields=[
                    SearchableField(name="name", type=SearchFieldDataType.String),
                    SimpleField(name="confidence", type=SearchFieldDataType.Double),
                    ComplexField(name="rectangle",
                        fields=[
                            SimpleField(name="x", type=SearchFieldDataType.Int32),
                            SimpleField(name="y", type=SearchFieldDataType.Int32),
                            SimpleField(name="w", type=SearchFieldDataType.Int32),
                            SimpleField(name="h", type=SearchFieldDataType.Int32)
                        ])
                ],
                collection=True
            ),
            ComplexField(name="categories",
                fields=[
                    SearchableField(name="name", type=SearchFieldDataType.String),
                    SimpleField(name="score", type=SearchFieldDataType.Double),
                    ComplexField(name="detail",
                        fields=[
                            ComplexField(name="celebrities",
                            fields=[
                                SearchableField(name="name", type=SearchFieldDataType.String),
                                ComplexField(name="faceBoundingBox",
                                    fields=[
                                        SimpleField(name="x", type=SearchFieldDataType.Int32),
                                        SimpleField(name="y", type=SearchFieldDataType.Int32)
                                    ],
                                    collection=True
                                ),
                                SimpleField(name="confidence", type=SearchFieldDataType.Double)
                            ],
                            collection=True
                            ),
                            ComplexField(name="landmarks",
                                fields=[
                                    SearchableField(name="name", type=SearchFieldDataType.String),
                                    SimpleField(name="confidence", type=SearchFieldDataType.Double)
                                ],
                                collection=True
                            )
                        ]
                    )
                ],
                collection=True
            ),
            ComplexField(name="description",
                fields=[
                    SearchableField(name="tags", type=SearchFieldDataType.String, collection=True),
                    ComplexField(name="captions",
                        fields=[
                            SearchableField(name="text", type=SearchFieldDataType.String),
                            SimpleField(name="confidence", type=SearchFieldDataType.Double)
                        ],
                        collection=True
                    )
                ],
                collection=True
            ),
            ComplexField(name="faces",
                fields=[
                    SimpleField(name="age", type=SearchFieldDataType.Int32),
                    SimpleField(name="gender", type=SearchFieldDataType.String),
                    ComplexField(name="faceBoundingBox",
                        fields=[
                            SimpleField(name="x", type=SearchFieldDataType.Int32),
                            SimpleField(name="y", type=SearchFieldDataType.Int32)
                        ],
                        collection=True
                    )
                ],
                collection=True
            ),
            ComplexField(name="objects",
                fields=[
                    SearchableField(name="object", type=SearchFieldDataType.String),
                    SimpleField(name="confidence", type=SearchFieldDataType.Double),
                    ComplexField(name="rectangle",
                        fields=[
                            SimpleField(name="x", type=SearchFieldDataType.Int32),
                            SimpleField(name="y", type=SearchFieldDataType.Int32),
                            SimpleField(name="w", type=SearchFieldDataType.Int32),
                            SimpleField(name="h", type=SearchFieldDataType.Int32)
                        ]
                    ),
                    ComplexField(name="parent",
                        fields=[
                            SearchableField(name="object", type=SearchFieldDataType.String),
                            SimpleField(name="confidence", type=SearchFieldDataType.String),
                        ]
                    )
                ],
                collection=True
            ),
            ComplexField(name="tags",
                fields=[
                    SearchableField(name="name", type=SearchFieldDataType.String),
                    SearchableField(name="hint", type=SearchFieldDataType.String),
                    SimpleField(name="confidence", type=SearchFieldDataType.Double)
                ],
                collection=True
            )
        ]

        semantic_config = SemanticConfiguration(
            name="my-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="file_name"),
                keywords_fields=[SemanticField(field_name="content")],
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
        suggester = [{'name':'sg','source_fields':['url','file_name']}]

        index = SearchIndex(
            name=index_name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options,
            # suggesters=suggester,
            # semantic_search=semantic_search
        )

        result = search_index_client.create_index(index)

        return result
    
    except Exception as ex:
        logging.error(ex)

def _create_data_source():

    try:
        search_indexer_client.delete_data_source_connection("shenghuai-datasource998")

        container = SearchIndexerDataContainer(name="shenghuaicontainer")

        data_source_connection = SearchIndexerDataSourceConnection(
            name="shenghuai-datasource998",
            type="azureblob",
            connection_string=connection_string,
            container=container
        )

        data_source = search_indexer_client.create_data_source_connection(data_source_connection)

        return data_source
    
    except Exception as ex:
        logging.error(ex)

def _create_skillset():

    search_indexer_client.delete_skillset(indexer_name)

    inp_image = InputFieldMappingEntry(name="image", source="/document/normalized_images/*")

    output_adult = OutputFieldMappingEntry(name="adult", target_name="adult")
    output_brands = OutputFieldMappingEntry(name="brands", target_name="brands")
    output_categories = OutputFieldMappingEntry(name="categories", target_name="categories")
    output_description = OutputFieldMappingEntry(name="description", target_name="description")
    output_faces = OutputFieldMappingEntry(name="faces", target_name="faces")
    output_objects = OutputFieldMappingEntry(name="objects", target_name="objects")
    output_tags = OutputFieldMappingEntry(name="tags", target_name="tags")

    imageAnalysisSkill = ImageAnalysisSkill(
        context="/document/normalized_images/*",
        name="shenghuai-image-analysis",
        inputs=[inp_image],
        outputs=[output_adult, output_brands, output_categories, output_description, output_faces, output_objects, output_tags],
        visual_features=[
            VisualFeature.ADULT,
            VisualFeature.BRANDS,
            VisualFeature.CATEGORIES,
            VisualFeature.DESCRIPTION,
            VisualFeature.FACES,
            VisualFeature.OBJECTS,
            VisualFeature.TAGS
        ],
        details=["celebrities", "landmarks"]
    )

    skillset = SearchIndexerSkillset(
        name="shenghuai-skillset998",
        skills=[imageAnalysisSkill],
        description="Image Analysis Skillset"
    )
    result = search_indexer_client.create_skillset(skillset)

    return result

def sample_indexer_workflow():

    _delete_index()


    skillset_name = _create_skillset().name
    print(f"{skillset_name} is created")

    datasource = _create_data_source().name
    print(f"{datasource} is created")

    ind_name = _create_index().name
    print(f"{ind_name} is created")

    configuration = IndexingParametersConfiguration(
        parsing_mode="default",
        data_to_extract="contentAndMetadata",
        image_action="generateNormalizedImages",
        query_timeout=None
    )

    parameters = IndexingParameters(configuration=configuration)

    indexer = SearchIndexer(
        name=indexer_name,
        data_source_name=datasource,
        target_index_name=ind_name,
        skillset_name=skillset_name,
        parameters=parameters,
        field_mappings=[
            FieldMapping(source_field_name="metadata_storage_path", target_field_name="url"),
            FieldMapping(source_field_name="metadata_storage_name", target_field_name="file_name")
        ],
        output_field_mappings=[
            FieldMapping(source_field_name="/document/normalized_images/*/adult", target_field_name="adult"),
            FieldMapping(source_field_name="/document/normalized_images/*/brands/*", target_field_name="brands"),
            FieldMapping(source_field_name="/document/normalized_images/*/categories/*", target_field_name="categories"),
            FieldMapping(source_field_name="/document/normalized_images/*/description", target_field_name="description"),
            FieldMapping(source_field_name="/document/normalized_images/*/faces/*", target_field_name="faces"),
            FieldMapping(source_field_name="/document/normalized_images/*/objects/*", target_field_name="objects"),
            FieldMapping(source_field_name="/document/normalized_images/*/tags/*", target_field_name="tags")
        ]
    )

    search_indexer_client.create_indexer(indexer)

    result = search_indexer_client.get_indexer(indexer_name)

    search_indexer_client.run_indexer(indexer_name)

if __name__ == "__main__":
    sample_indexer_workflow()