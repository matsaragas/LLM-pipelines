#Purpose
This repository is focused on building document ingestion pipelines that:

Index documents

Perform intelligent chunking

Generate embeddings

The goal is to make documents efficiently searchable and ready for downstream applications like semantic search and question answering.



## Installation & Set up

This project includes general LLM infrastructure suitable for production-scale applications.

###1. Install PostgreSQL and Dependencies

Use Homebrew (for Mac) to install the required packages:

```shell
brew install postgresql
brew install make
```

###2. Install PGVector Extension

Clone and build the pgvector extension:
```shell
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
make install
```

### 3. Set Up PostgreSQL with PGVector

Start PostgreSQL:

```shell
brew services start postgresql`
```
Create a new database:
```shell
createdb vectortutorial
```

Create a superuser (choose the appropriate path based on your system):

```shell
/opt/homebrew/bin/createuser -s postgres` 
#or 
/usr/local/opt/postgresql\@14/bin/createuser -s postgres`
```

Connect to your database:

```shell
psql --host localhost --username postgres --dbname vectortutorial
```

Inside the PostgreSQL terminal, enable the vector extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;`
```
You can now create tables capable of storing vector embeddings.




## OpenSearch Vector Store

To set up a local OpenSearch instance:

Refer to the official documentation:

[OpenSearch 1.0 Docs](https://opensearch.org/docs/1.0/)

If you encounter SSL issues, try this Docker command:

```shell
docker run -p 9200:9200 -p 9600:9600 -e "discovery.type=single-node" -e "plugins.security.disabled=true" opensearchproject/opensearch:1.0.1
```
`
`


## Node Parsers

They are simple abstractions that take a list of documents, and chunk them
into Node objects, such that each node is a specific chunk of the parent document. 
When a document is broken into nodes, all of it's attributes are inherited 
to the children nodes (i.e. metadata, text and metadata templates, etc)

Different Node Parsers:

1) MarkdownNodeParser: It splits a document into Nodes using Markdown header-based splitting logic. Each node contains its text content and the paths
of the headers leading to it.

## Ingestion Pipeline


![Alt text](images/Ingestion_Pipeline.png)