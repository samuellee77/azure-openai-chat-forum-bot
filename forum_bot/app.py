import os
import requests 
import openai
from utils import *
from flask import Flask, request, jsonify
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from retrievethenread import RetrieveThenReadApproach
from azure.core.credentials import AzureKeyCredential

AZURE_SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
AZURE_OPENAI_SERVICE = os.getenv("AZURE_OPENAI_SERVICE")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_CHATGPT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT")
AZURE_OPENAI_CHATGPT_MODEL = os.getenv("AZURE_OPENAI_CHATGPT_MODEL", "gpt-35-turbo")
AZURE_KEY_CREDENTIAL = os.getenv("AZURE_KEY_CREDENTIAL")
FORUM_USERNAME = os.getenv("FORUM_USERNAME")
FORUM_API_KEY = os.getenv("FORUM_API_KEY")
KB_FIELDS_CONTENT = os.getenv("KB_FIELDS_CONTENT", "content")
KB_FIELDS_CATEGORY = os.getenv("KB_FIELDS_CATEGORY", "category")
KB_FIELDS_SOURCEPAGE = os.getenv("KB_FIELDS_SOURCEPAGE", "sourcepage")

azure_credential = DefaultAzureCredential(exclude_shared_token_cache_credential = True)
credential = AzureKeyCredential(AZURE_KEY_CREDENTIAL)

openai.api_base = f"https://{AZURE_OPENAI_SERVICE}.openai.azure.com"
openai.api_version = "2023-05-15"
openai.api_type = "azure"
openai.api_key = AZURE_OPENAI_KEY

# Set up clients for Cognitive Search and Storage
search_client = SearchClient(
    endpoint=f"https://{AZURE_SEARCH_SERVICE}.search.windows.net",
    index_name=AZURE_SEARCH_INDEX,
    credential=credential)

app = Flask(__name__)  

@app.route("/", methods=['GET'])
def index():
    return "<h1>Hello World!<h1>"

@app.route('/webhook', methods=['POST'])  
def webhook():
    if not request.headers.get('X-Discourse-Event') == "topic_created":
        return jsonify(success=False), 403
    forum_domain = request.headers.get('X-Discourse-Instance')
    topic_id = request.json["topic"]["id"]
    received = requests.get(f"{forum_domain}/t/{topic_id}.json").json().get("post_stream").get("posts")[0]
    topic_title = received.get("topic_slug").replace("-", " ")
    topic_content = received.get("cooked")
    try:
        impl = RetrieveThenReadApproach(search_client, AZURE_OPENAI_CHATGPT_DEPLOYMENT, AZURE_OPENAI_CHATGPT_MODEL, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
        r = jsonify(impl.run(f"Title: {topic_title}\n{topic_content}", {}))
        opening = "The following is the auto reply by GPT bot:"
        disclaimer = "*Note: Please remind that this auto reply might not be accurate. If you have any more questions, please reply to this post."
        dont_know_message = "Sorry, I cannot answer this question based on my data sources. Please wait for our experts to answer your question.\nThank You."
        answer = r.json.get('answer') if not r.json.get('answer').lower() == "false" else dont_know_message
        # next step: post directly to the forum
        forum_response = requests.post(f"{forum_domain}/posts.json", headers={"Api-Key": FORUM_API_KEY, "Api-Username": FORUM_USERNAME},
                                json={"raw": f"{opening}\n\n{answer}\n\n{disclaimer}",
                                "topic_id": topic_id})
        if forum_response.status_code == 200:
            return jsonify(success=True), 200
        else:
            raise Exception(forum_response.json().get('error'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':  
    app.run() 
