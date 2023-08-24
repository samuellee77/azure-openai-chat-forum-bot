import os
import requests 
import openai
from utils import *
from flask import Flask, request, jsonify
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from retrievethenread import RetrieveThenReadApproach
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient

AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER")
AZURE_STORAGE_KEY = os.getenv("AZURE_STORAGE_KEY")
AZURE_SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
AZURE_OPENAI_SERVICE = os.getenv("AZURE_OPENAI_SERVICE")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_CHATGPT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT")
AZURE_OPENAI_CHATGPT_MODEL = os.getenv("AZURE_OPENAI_CHATGPT_MODEL", "gpt-35-turbo")
AZURE_KEY_CREDENTIAL = os.getenv("AZURE_KEY_CREDENTIAL")
FORUM_API_USERNAME = os.getenv("FORUM_USERNAME")
FORUM_API_KEY = os.getenv("FORUM_API_KEY")
FORUM_URL = os.getenv("FORUM_URL")
KB_FIELDS_CONTENT = os.getenv("KB_FIELDS_CONTENT", "content")
KB_FIELDS_CATEGORY = os.getenv("KB_FIELDS_CATEGORY", "category")
KB_FIELDS_SOURCEFILE = os.getenv("KB_FIELDS_SOURCEFILE", "sourcefile")

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

blob_client = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net", 
    credential=AZURE_STORAGE_KEY)
blob_container = blob_client.get_container_client(AZURE_STORAGE_CONTAINER)

def get_blob(blob_name):
    try:
        # Get a reference to the blob
        blob_client = blob_container.get_blob_client(blob_name[:blob_name.rfind('.')] + ".pdf")
        if blob_client.exists():
        # Download the blob to a local file
            blob_data = blob_client.download_blob()
            return blob_data, "pdf"
        else:
            blob_client = blob_container.get_blob_client(blob_name)
            blob_data = blob_client.download_blob()
            return blob_data, "md"
    except Exception as e:
        print("\""+blob_name+"\"")
        print(str(e))
        return

# Function to upload a file and get the URL
def upload_file(blob_name):
    url = f"{FORUM_URL}/uploads.json"
    headers = {
        "Api-Key": FORUM_API_KEY,
        "Api-Username": FORUM_API_USERNAME,
    }
    content, mime_type = get_blob(blob_name)
    if mime_type == "pdf":
        response = requests.post(url,
                  files = {'files[]': (blob_name[:blob_name.rfind('.')] + ".pdf", content, 'application/pdf')},
                  data={'type':'composer'},
                  headers=headers)
    elif mime_type == "md":    
        response = requests.post(url,
                  files = {'files[]': (blob_name, content, 'text/markdown')},
                  data={'type':'composer'},
                  headers=headers)
    response_data = response.json()
    if 'url' in response_data:
        return response_data['url']
    else:
        return 

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
        impl = RetrieveThenReadApproach(search_client, AZURE_OPENAI_CHATGPT_DEPLOYMENT, AZURE_OPENAI_CHATGPT_MODEL, KB_FIELDS_SOURCEFILE, KB_FIELDS_CONTENT)
        r = jsonify(impl.run(f"Title: {topic_title}\n{topic_content}", {}))
        data_sources = list(map(lambda x : x.split(":")[0], r.json.get("data_points")))
        upload_urls = {x: upload_file(x) for x in data_sources}
        file_urls = [f"<a target='_blank' rel='noopener' href='{upload_urls[source]}'>{source[:source.rfind('.')]}</a>" for source in upload_urls if upload_urls[source]]
        md = """References:\n\n""" + "\n".join(file_urls)
        opening = "The following is the auto reply by GPT bot:"
        disclaimer = "*Note: Please remind that this auto reply might not be accurate. If you have any more questions, please reply to this post."
        dont_know_message = "Sorry, I cannot answer this question based on my data sources. Please wait for our experts to answer your question.\nThank You."
        answer = r.json.get('answer') if not r.json.get('answer').lower() == "false" else dont_know_message
        payload = {"raw": f"{opening}\n\n{answer}\n\n{md}\n\n{disclaimer}", "topic_id": topic_id} if not r.json.get('answer').lower() == "false" \
            else {"raw": f"{opening}\n\n{answer}\n\n{disclaimer}", "topic_id": topic_id}
        # next step: post directly to the forum
        forum_response = requests.post(f"{forum_domain}/posts.json", headers={"Api-Key": FORUM_API_KEY, "Api-Username": FORUM_API_USERNAME},
                                json=payload)
        return jsonify(success=True), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':  
    app.run() 
