# Forum Bot & Chat Bot with Azure OpenAI

> If you want to clone this repository, please use:
> ```bash
> git clone --recurse-submodules <url>
> ```
> Remember to add `--recurse-submodules` while cloning.

###### modified from [ChatGPT + Enterprise data with Azure OpenAI and Cognitive Search](https://github.com/Azure-Samples/azure-search-openai-demo/)

Welcome to the **Azure OpenAI Chat Forum Bot** repository! This project demonstrates how to integrate OpenAI's powerful language model into a Discourse-based auto reply bot and a web chatbot using Microsoft Azure services. 

![Overview](/imgs/overview.png)

## Table of Contents

- [Introduction](#introduction)
- [Structure](#structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Prepare Data (upload)](#prepare-data-upload)
    - [Forum Bot](#forum-bot)
    - [Chat Bot](#chat-bot)
- [Resources](#resources)

## Introduction

The Azure OpenAI Chat Forum Bot leverages the capabilities of OpenAI's language model to create an interactive and engaging forum bot. With this bot, you can provide an enhanced user experience within your forum community by enabling dynamic and relevant discussions. This repository contains two parts, which are forum bot (on Discourse) and chat bot (on website).

## Structure

- `./chat_bot` contains the codes to add chat bot to a sample webpage
- `./data` is the folder where you should store the data you want to add to the bot knowledge base
- `./forum_bot` contains the codes to add autoresponder to your discourse website
- `requirements.txt` have all the required packages listed
- `./scripts` contains Python scripts which can prepare the data and upload it

## Getting Started

### Prerequisites

Before you begin, ensure you have the following:

- Python 3.9+
  - **Notice:** Python and the pip package manager must be in the path in Windows for the setup scripts to work.
- Git
- Azure account (with sufficient permissions to create and manage resources)
- Azure Developer CLI
- OpenAI API key

You also need to manually creates Azure Web Service, Azure OpenAI Service, and Azure Cognitive Search Service. If you don't have any pre-existing Azure services, create those services [here](https://portal.azure.com) and follow the guides:
  - [Azure Web Service](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python?tabs=flask%2Cwindows%2Cazure-cli%2Cvscode-deploy%2Cdeploy-instructions-azportal%2Cterminal-bash%2Cdeploy-instructions-zip-azcli)
  - [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource?pivots=web-portal)
  - [Azure Cognitive Search](https://learn.microsoft.com/en-us/azure/search/search-get-started-portal)
    - AZURE_KEY_CREDENTIAL can be found under your Search Service -> Settings -> Keys -> Primary admin key

You need to set the following environment variables in `./scripts/.env`:
- AZURE_SEARCH_SERVICE
- AZURE_SEARCH_INDEX
- AZURE_OPENAI_SERVICE
- AZURE_OPENAI_KEY
- AZURE_OPENAI_CHATGPT_DEPLOYMENT
- AZURE_OPENAI_CHATGPT_MODEL (need to be gpt-35-turbo or gpt-4)
- AZURE_SEARCH_KEY
- KB_FIELDS_CONTENT (optional)
- KB_FIELDS_CATEGORY (optional)
- KB_FIELDS_SOURCEPAGE (optional)
- FORUM_API_USERNAME
- FORUM_API_KEY
- FORUM_URL

---

### Installation

Clone this repository to your local machine:
```bash
git clone https://github.com/samuellee77/azure-openai-chat-forum-bot.git
cd azure-openai-chat-forum-bot
```

---
#### Prepare Data (upload)

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Change th environment variables in `set_env.sh` (in local) and run the following code:
```bash
source set_env.sh
```

3. If you want to download new data from wiki, forum, or other websites, you can run the following sample code:
- Download single page:
```bash
cd scripts
python download_single_page.py --url {target_url} --folder {folder_path} --type 'wiki'
```
- Download whole forum topics (you need to change `url` variable in the script):
```bash
python forum_scraper.py
```
- Download wiki data:
```bash
python download_wiki --url {root_url} --folder {folder_path}
```
  - **Note:** Remember to fill in correct url and folder path in the shell command
  - **Tips:** You can write a simple shell script to automatically download all urls you want at once

4. Move the data (should be in .md format) you want to add into `./data`. Then, run the following code to upload blob and index:
```bash
sh prepdocs.sh
```
---
#### Forum Bot

1. You need to have an admin user on your Discourse forum. You have to get your API key and username, and you also need to setup webhooks:
    - To get an API key, follow this [guide](https://meta.discourse.org/t/create-and-configure-an-api-key/230124)
    - To set up webhook, follow this [guide](https://meta.discourse.org/t/configure-webhooks-that-trigger-on-discourse-events-to-integrate-with-external-services/49045)
        - Payload URL: the web domain of your web service
        - Select individual event -> Topic Event
2. Deploy to your web service. (using Azure CLI, GitHub, local Git, etc.)
---

## Resources

- [Azure Search OpenAI Demo](https://github.com/Azure-Samples/azure-search-openai-demo)
- [Discourse API](https://docs.discourse.org)
