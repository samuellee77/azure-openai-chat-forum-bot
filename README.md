# azure-openai-chat-forum-bot

###### modified from [ChatGPT + Enterprise data with Azure OpenAI and Cognitive Search](https://github.com/Azure-Samples/azure-search-openai-demo/)
Welcome to the **Azure OpenAI Chat Forum Bot** repository! This project demonstrates how to integrate OpenAI's powerful language model into a forum-based chatbot using Microsoft Azure services. The bot is designed to engage in natural and contextually relevant conversations with users on various topics within a forum setting.

## Table of Contents

- [Introduction](#introduction)
- [Structure](#structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)

## Introduction

The Azure OpenAI Chat Forum Bot leverages the capabilities of OpenAI's language model to create an interactive and engaging forum bot. With this bot, you can provide an enhanced user experience within your forum community by enabling dynamic and relevant discussions. Whether you're looking to add a touch of AI-powered assistance or spark insightful conversations, this bot has got you covered.

## Structure

- `/chat_bot` contains the codes to add chat bot to a sample webpage
- `/data` is the folder where you should store the data you want to add to the bot knowledge base
- `/forum_bot` contains the codes to add autoresponder to your discourse website
- `requirements.txt` have all the required packages listed
- `/scripts` contains Python scripts which can prepare the data and upload it

## Getting Started

### Prerequisites

Before you begin, ensure you have the following:

- Python 3.9+
  - Important: Python and the pip package manager must be in the path in Windows for the setup scripts to work.
- Git
- Azure account (with sufficient permissions to create and manage resources)
- Azure Developer CLI
- OpenAI API key

You also need to manually creates Azure Web Service, Azure OpenAI Service, and Azure Cognitive Search Service. If you don't have any pre-existing Azure services, create those services [here](https://portal.azure.com) and follow the guides
  - [Azure Web Service](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python?tabs=flask%2Cwindows%2Cazure-cli%2Cvscode-deploy%2Cdeploy-instructions-azportal%2Cterminal-bash%2Cdeploy-instructions-zip-azcli)
  - [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource?pivots=web-portal)
  - [Azure Cognitive Search](https://learn.microsoft.com/en-us/azure/search/search-get-started-portal)
    - AZURE_KEY_CREDENTIAL can be found under your search service -> Settings -> Keys -> Primary admin key

You need to set the following environment variables in `./scripts/.env`:
- AZURE_SEARCH_SERVICE
- AZURE_SEARCH_INDEX
- AZURE_OPENAI_SERVICE
- AZURE_OPENAI_KEY
- AZURE_OPENAI_CHATGPT_DEPLOYMENT
- AZURE_OPENAI_CHATGPT_MODEL (need to be gpt-35-turbo or gpt-4)
- AZURE_KEY_CREDENTIAL
- KB_FIELDS_CONTENT (optional)
- KB_FIELDS_CATEGORY (optional)
- KB_FIELDS_SOURCEPAGE (optional)
- FORUM_USERNAME
- FORUM_API_KEY

### Installation

1. Clone this repository to your local machine:

```bash
git clone https://github.com/samuellee77/azure-openai-chat-forum-bot.git
cd azure-openai-chat-forum-bot
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. You need to have an admin user on your Discourse forum. You have to get your API key and username, and you also need to setup webhooks:
  - To get an API key, follow this [guide](https://meta.discourse.org/t/create-and-configure-an-api-key/230124)
  - To set up webhook, follow this [guide](https://meta.discourse.org/t/configure-webhooks-that-trigger-on-discourse-events-to-integrate-with-external-services/49045)
    - Payload URL: the web domain of your web service
    - Select individual event -> Topic Event

4. Change the `.env_sample` to `.env` and set the environment variables mentioned above.

5. Run `./scripts/prepdocs.sh`.

6. Deploy to your web service.