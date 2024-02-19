# GPT-Report-Generator

## Introduction

GPT-Report-Generator is an efficient AI tool that uses RAG (retrieval-augmented generation) methodology to generate reports on a specific topic. It uses lightweight yet powerful embedding model from HuggingFace sentence-transformers/all-MiniLM-L6-v2 to generate embeddings (dimensions: 384) and MongoDB Atlas Vector Search to store and perform vector search for most relevant documents from the collection based on query string. Later three most relevant documents with the question string are provided as a customized prompt to OpenAI’s gpt3.5 turbo text-generative model to generate response as answer to the question string, which is saved in a structured manner to complete the report.

`text-gen-model`:- `gpt-3.5 turbo`

`embedding-model`:- `sentence-transformers/all-MiniLM-L6-v2A`

`vector-database`:- mongodb-atlas-vector-search

## Installation

Clone this repo, start by making virtual environment to better manage python packages and not affect system-wide packages. Activate virutal environment install packages.

Steps-

`python -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

**Delete `data.csv` to work with updated data from web**

## Usage

The main script has two modes one to scrape latest data from the web and then generate report based on new data or use data already provided to generate report.

### Modes

`BUILD` Work with already existing data, this is only possible in case accurate `database` and `collection` name that has embedded data is provided to work with.

`SEARCH_AND_BUILD` Collect most updated data from web, create embeddings and perform vector search. `database` and `collection` name must be provided.

### Config.ini

Create `config.ini` add secrets and update parameters
