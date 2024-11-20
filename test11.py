from googlesearch import search

query = "中華民國"

for result in search(query, num_results=3, lang='zh-TW', safe='off', advanced=True):
    print(result.title)
    print(result.description)
    print(result.url)
    print()



2024-11-14 11:06:41,342 - __main__ - INFO - Total count: 10
2024-11-14 11:06:41,374 - __main__ - INFO - content:Azure Cosmos DB is a globally distributed, multi-model database service that enables you to build and manage NoSQL applications in Azure. It provides features like automatic scaling, low-latency access, and multi-master replication. Cosmos DB supports various data models, such as key-value, document, graph, and column-family. You can use Azure Cosmos DB to build globally distributed applications, ensure high availability and performance, and manage your data at scale. It also integrates with other Azure services, such as Azure Functions and Azure App Service.
2024-11-14 11:06:41,375 - __main__ - INFO - category:Databases
2024-11-14 11:06:41,375 - __main__ - INFO - id:70
2024-11-14 11:06:41,375 - __main__ - INFO - title:Azure Cosmos DB
2024-11-14 11:06:41,375 - __main__ - INFO - @search.score:4.629068
2024-11-14 11:06:41,375 - __main__ - INFO - @search.reranker_score:None
2024-11-14 11:06:41,375 - __main__ - INFO - @search.highlights:None
2024-11-14 11:06:41,375 - __main__ - INFO - @search.captions:None



2024-11-14 11:06:41,376 - __main__ - INFO - content:Azure Cosmos DB is a fully managed, globally distributed, multi-model database service designed for building highly responsive and scalable applications. It offers turnkey global distribution, automatic and instant scalability, and guarantees low latency, high availability, and consistency. Cosmos DB supports popular NoSQL APIs, including MongoDB, Cassandra, Gremlin, and Azure Table Storage. You can build globally distributed applications with ease, without having to deal with complex configuration and capacity planning. Data stored in Cosmos DB is automatically indexed, enabling you to query your data with SQL, JavaScript, or other supported query languages.
2024-11-14 11:06:41,376 - __main__ - INFO - category:Databases
2024-11-14 11:06:41,376 - __main__ - INFO - id:6
2024-11-14 11:06:41,376 - __main__ - INFO - title:Azure Cosmos DB
2024-11-14 11:06:41,377 - __main__ - INFO - @search.score:4.105675
2024-11-14 11:06:41,377 - __main__ - INFO - @search.reranker_score:None
2024-11-14 11:06:41,377 - __main__ - INFO - @search.highlights:None
2024-11-14 11:06:41,377 - __main__ - INFO - @search.captions:None



2024-11-14 11:06:41,378 - __main__ - INFO - content:Azure Synapse Analytics is an integrated analytics service that brings together big data and data warehousing. It enables you to ingest, prepare, manage, and serve data for immediate business intelligence and machine learning needs. Synapse Analytics provides a unified workspace for data engineers, data scientists, and business analysts to collaborate and build solutions. It supports various data sources, including Azure Data Lake Storage, Azure Blob Storage, and Azure Cosmos DB. You can use Synapse Analytics with other Azure services, such as Azure Machine Learning and Power BI.      
2024-11-14 11:06:41,379 - __main__ - INFO - category:Analytics
2024-11-14 11:06:41,379 - __main__ - INFO - id:18
2024-11-14 11:06:41,379 - __main__ - INFO - title:Azure Synapse Analytics
2024-11-14 11:06:41,380 - __main__ - INFO - @search.score:1.9297134
2024-11-14 11:06:41,380 - __main__ - INFO - @search.reranker_score:None
2024-11-14 11:06:41,380 - __main__ - INFO - @search.highlights:None
2024-11-14 11:06:41,380 - __main__ - INFO - @search.captions:None



2024-11-14 11:06:41,380 - __main__ - INFO - content:Azure Databricks is an Apache Spark-based analytics platform optimized for the Azure cloud. It provides a collaborative workspace for data scientists, engineers, and business users to process, analyze, and visualize big data. Databricks supports multiple programming languages, including Python, Scala, R, and SQL. It offers built-in integration with Azure Blob Storage, Azure Data Lake Storage, and Azure Cosmos DB. You can also use Databricks to train and deploy machine learning models, and integrate with Azure Machine Learning.
2024-11-14 11:06:41,381 - __main__ - INFO - category:Analytics
2024-11-14 11:06:41,381 - __main__ - INFO - id:12
2024-11-14 11:06:41,381 - __main__ - INFO - title:Azure Databricks
2024-11-14 11:06:41,381 - __main__ - INFO - @search.score:1.9008987
2024-11-14 11:06:41,382 - __main__ - INFO - @search.reranker_score:None
2024-11-14 11:06:41,382 - __main__ - INFO - @search.highlights:None
2024-11-14 11:06:41,382 - __main__ - INFO - @search.captions:None



2024-11-14 11:06:41,382 - __main__ - INFO - content:Azure Functions is a serverless compute service that enables you to run event-driven code without managing the underlying infrastructure. It provides features like automatic scaling, triggers, and bindings. Functions supports various programming languages, such as C#, Java, and Python. You can use Azure Functions to build microservices, integrate with other Azure services, and process and transform data. It also integrates with other Azure services, such as Azure Event Hubs, Azure Storage, and Azure Cosmos DB.
2024-11-14 11:06:41,383 - __main__ - INFO - category:Compute
2024-11-14 11:06:41,383 - __main__ - INFO - id:63
2024-11-14 11:06:41,383 - __main__ - INFO - title:Azure Functions
2024-11-14 11:06:41,383 - __main__ - INFO - @search.score:1.8221349
2024-11-14 11:06:41,383 - __main__ - INFO - @search.reranker_score:None
2024-11-14 11:06:41,383 - __main__ - INFO - @search.highlights:None
2024-11-14 11:06:41,383 - __main__ - INFO - @search.captions:None


---

(env) PS C:\Users\10706030\Desktop\flaskintroduction\temporary_practice1104> python app13.py
2024-11-14 11:27:23,881 - __main__ - INFO - Total count: 108
2024-11-14 11:27:23,913 - __main__ - INFO - category:Analytics
2024-11-14 11:27:23,913 - __main__ - INFO - content:Azure Data Factory is a cloud-based data integration service that enables you to create, schedule, and manage your data workflows. It provides features like data movement, data transformation, and integration with Azure Machine Learning. Data Factory supports various data sources, such as Azure Blob Storage, Azure Data Lake Storage, and Azure SQL Database. You can use Azure Data Factory to build data pipelines, develop big data analytics solutions, and migrate your data to Azure. It also integrates with other Azure services, such as Azure Synapse Analytics and Azure Data Lake Analytics.
2024-11-14 11:27:23,913 - __main__ - INFO - id:106
2024-11-14 11:27:23,913 - __main__ - INFO - title:Azure Data Factory
2024-11-14 11:27:23,913 - __main__ - INFO - @search.score:4.1833234
2024-11-14 11:27:23,913 - __main__ - INFO - @search.reranker_score:None
2024-11-14 11:27:23,913 - __main__ - INFO - @search.highlights:None
2024-11-14 11:27:23,913 - __main__ - INFO - @search.captions:None



2024-11-14 11:27:23,913 - __main__ - INFO - category:Storage
2024-11-14 11:27:23,913 - __main__ - INFO - content:Azure Data Box is a family of data transfer devices that enables you to securely and efficiently transfer your data to Azure. It provides features like offline data transfer, data encryption, and chain of custody. Data Box supports various data types, such as files, databases, and virtual machines. You can use Azure Data Box to migrate your data, build data lakes, and perform data backup and archiving. It also integrates with other Azure services, such as Azure Storage and Azure Synapse Analytics.
2024-11-14 11:27:23,913 - __main__ - INFO - id:54
2024-11-14 11:27:23,913 - __main__ - INFO - title:Azure Data Box
2024-11-14 11:27:23,913 - __main__ - INFO - @search.score:3.7056415
2024-11-14 11:27:23,913 - __main__ - INFO - @search.reranker_score:None
2024-11-14 11:27:23,913 - __main__ - INFO - @search.highlights:None
2024-11-14 11:27:23,913 - __main__ - INFO - @search.captions:None



2024-11-14 11:27:23,913 - __main__ - INFO - category:Analytics
2024-11-14 11:27:23,913 - __main__ - INFO - content:Azure Data Catalog is a fully managed metadata service that enables you to discover, understand, and use your data sources. It provides features like data asset registration, metadata discovery, and data lineage. Data Catalog supports various data sources, such as Azure SQL Database, Azure Blob Storage, and on-premises file systems. You can use Data Catalog to build a unified data catalog, improve data governance, and streamline your data discovery process. It also integrates with other Azure services, such as Azure Synapse Analytics and Azure Data Factory.
2024-11-14 11:27:23,917 - __main__ - INFO - id:35
2024-11-14 11:27:23,917 - __main__ - INFO - title:Azure Data Catalog
2024-11-14 11:27:23,917 - __main__ - INFO - @search.score:3.6396973
2024-11-14 11:27:23,917 - __main__ - INFO - @search.reranker_score:None
2024-11-14 11:27:23,917 - __main__ - INFO - @search.highlights:None
2024-11-14 11:27:23,917 - __main__ - INFO - @search.captions:None