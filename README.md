# azure-openai-chat-forum-bot

Welcome to the **Azure OpenAI Chat Forum Bot** repository! This project demonstrates how to integrate OpenAI's powerful language model into a forum-based chatbot using Microsoft Azure services. The bot is designed to engage in natural and contextually relevant conversations with users on various topics within a forum setting.

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)

## Introduction

The Azure OpenAI Chat Forum Bot leverages the capabilities of OpenAI's language model to create an interactive and engaging forum bot. With this bot, you can provide an enhanced user experience within your forum community by enabling dynamic and relevant discussions. Whether you're looking to add a touch of AI-powered assistance or spark insightful conversations, this bot has got you covered.

## Structure

- `chat_bot/` contains the codes to add chat bot to a sample webpage
- `data/` is the folder where you should store the data you want to add to the bot knowledge base
- `forum_bot/` contains the codes to add autoresponder to your discourse website
- `requirements.txt` have all the required packages listed
- `scripts/` contains Python scripts which can prepare the data and upload it

## Getting Started

### Prerequisites

Before you begin, ensure you have the following:

- Azure account (with sufficient permissions to create and manage resources)
- OpenAI API key

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

3. Configure the bot by adding your OpenAI API key and adjusting settings in the `config.js` file.

4. Deploy the bot to Azure using your preferred deployment method (Azure CLI, Azure DevOps, etc.).
