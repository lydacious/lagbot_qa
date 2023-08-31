# Lagrange Q&A Chatbot

The Lagrange Q&A Chatbot is a specialized version of the Akcio assistant that focuses on providing accurate answers to user questions using predefined documentation chunks. Unlike a general-purpose AI, this chatbot operates within a well-defined scope and leverages existing information to respond to inquiries.
## Features

- Precision: The chatbot's responses are derived exclusively from predefined documentation chunks, ensuring that the information provided is accurate and aligned with the available knowledge.
- Limited Scope: The chatbot refrains from generating new responses or engaging in creative discussions. Instead, it concentrates on answering questions based on the provided documentation.
- User Interaction: Users can interact with the chatbot by sending questions. The chatbot searches its database of documentation chunks to offer relevant and informative responses.
- Open Source: The Lagrange Q&A Chatbot is an open-source project, enabling transparency and collaboration among developers.

## Deployment

1. Downloads
    ```shell
    $ git clone https://github.com/lydacious/lagbot_qa/
    $ cd lagbot_qa
    ```

2. Install dependencies
    ```shell
    $ pip install -r requirements.txt
    ```

3. Configure modules

    You can configure all arguments by modifying [config.py](./config.py) to set up your system with default modules.

    - LLM

        By default, the system will use **OpenAI** service as the LLM option.
        To set your OpenAI API key without modifying the configuration file, you can pass it as environment variable.

        ```shell
        $ export OPENAI_API_KEY=your_keys_here
        ```

        <details>

        <summary> Check how to <strong>SWITCH LLM</strong>. </summary>
         If you want to use another supported LLM service, you can change the LLM option and set up for it.
         Besides directly modifying the configuration file, you can also set up via environment variables.

        - For example, to use **Llama-2** at local which does not require any account, you just need to change the LLM option:
            ```shell
            $ export LLM_OPTION=llama_2
            ```

        - For example, to use **Ernie** instead of OpenAI, you need to change the option and set up Ernie API key & secret key:
            ```shell
            $ export LLM_OPTION=ernie
            $ export ERNIE_API_KEY=your_ernie_api_key
            $ export ERNIE_SECRET_KEY=your_ernie_secret_key
            ```
        </details>
        
    - Embedding

        By default, the embedding module uses methods from [Sentence Transformers](https://www.sbert.net/) to convert text inputs to vectors. Here are some information about the default embedding method:
        - model: [multi-qa-mpnet-base-cos-v1](https://huggingface.co/sentence-transformers/multi-qa-mpnet-base-cos-v1)(420MB)
        - dim: 768
        - normalization: True

    - Store

        Before getting started, all database services used for store must be running and be configured with write and create access.

        - Vector Store: You need to prepare the service of vector database in advance. For example, you can refer to [Milvus Documents](https://milvus.io/docs) or [Zilliz Cloud](https://zilliz.com/doc/quick_start) to learn about how to start a Milvus service.
        - Scalar Store (Optional): This is optional, only work when `USE_SCALAR` is true in [configuration](config.py). If this is enabled (i.e. USE_SCALAR=True), the default scalar store will use [Elastic](https://www.elastic.co/). In this case, you need to prepare the Elasticsearch service in advance.
        - Memory Store: You need to prepare the database for memory storage as well. By default, LangChain mode supports [Postgresql](https://www.postgresql.org/) and Towhee mode allows interaction with any database supported by [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/dialects/).

        The system will use default store configs.
        To set up your special connections for each database, you can also export environment variables instead of modifying the configuration file.

        For the Vector Store, set **MILVUS_URI**:
        ```shell
        $ export MILVUS_URI=https://localhost:19530
        ```

        For the Memory Store, set **SQL_URI**:
        ```shell
        $ export SQL_URI={database_type}://{user}:{password}@{host}/{database_name}
        ```
        > LangChain mode only supports [Postgresql](https://www.postgresql.org/) as database type.
 

        <details>
        <summary>By default, scalar store (elastic) is disabled.
        Click to check how to <strong>enable Elastic</strong>.</summary>

        The following commands help to connect your Elastic cloud.

        ```shell
        $ export USE_SCALAR=True
        $ export ES_CLOUD_ID=your_elastic_cloud_id
        $ export ES_USER=your_elastic_username
        $ export ES_PASSWORD=your_elastic_password
        ```

        To use host & port instead of cloud id, you can manually modify the `VECTORDB_CONFIG` in [config.py](./config.py).

        </details>

<br />

4. Start service

    The main script will run a FastAPI service with default address `localhost:8900`.

    - Option 1: using Towhee
        ```shell
        $ python main.py --towhee
        ```
    - Option 2: using LangChain
        ```shell
        $ python main.py --langchain
        ```

4. Access via browser
    
    You can open url https://localhost:8900/docs in browser to access the web service.

    <p align="center" width="100%">
        <img width="80%" src="./pics/fastapi.png">
    </p>

    > `/`: Check service status
    >
    > `/answer`: Generate answer for the given question, with assigned session_id and project
    >
    > `/project/add`: Add data to project (will create the project if not exist)
    >
    > `/project/drop`: Drop project including delete data in both vector and memory storages.
    
    Check [Online Operations](https://github.com/zilliztech/akcio/wiki/Online-Operations) to learn more about these APIs.


## Load data

The `insert` function in [operations](./src_langchain/operations.py) loads project data from url(s) or file(s).

There are 2 options to load project data:

### Option 1: Offline

We recommend this method, which loads data in separate steps.
There is also advanced options to load document, for example, generating and inserting potential questions for each doc chunk.
Refer to [offline_tools](./offline_tools) for instructions.

### Option 2. Online

When the [FastAPI service](#deployment) is up, you can use the POST request `http://localhost:8900/project/add` to load data.

Parameters:
```json
{
  "project": "project_name",
  "data_src": "path_to_doc",
  "source_type": "file"
}
```
or
```json
{
  "project": "project_name",
  "data_src": "doc_url",
  "source_type": "url"
}
```

This method is only recommended to load a small amount of data, but **not for a large amount of data**.


<br />


## LICENSE

Akcio is published under the [Server Side Public License (SSPL) v1](./LICENSE).
