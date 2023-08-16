import openai
from approaches.approach import Approach
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from utils import nonewlines

# Simple retrieve-then-read implementation, using the Cognitive Search and OpenAI APIs directly. It first retrieves
# top documents from search, then constructs a prompt with them, and then uses OpenAI to generate an completion 
# (answer) with that prompt.
class RetrieveThenReadApproach(Approach):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

    template = \
"You are an expert who only focuses on answering questions related to Advantech Corporation" + \
"to help users with issues they are experiencing with their Advantech devices or services." + \
"Keep your answer concise and use less than 5 sentences to answer the question" + \
"Answer the following question using only the data provided in the sources below. " + \
"For tabular information return it as an html table. Do not return markdown format. "  + \
"ONLY answer questions that are related to the products and services of Advantech." + \
"For example, if the questions are about politics, economies, ideologies, religions, countries, say 'I cannot answer this question'." + \
"Each source has a name followed by colon and the actual information, but do not include the source name for each fact you use in the response. " + \
"If you cannot answer using the sources below, say 'false'." + \
"""
Sources:
{sources}
"""
    
    def __init__(self, search_client: SearchClient, openai_deployment: str, chatgpt_model: str, sourcepage_field: str, content_field: str):
        self.search_client = search_client
        self.openai_deployment = openai_deployment
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        self.chatgpt_model = chatgpt_model

    def run(self, q: str, overrides: dict) -> any:
        use_semantic_captions = True if overrides.get("semantic_captions") else False
        top = overrides.get("top") or 3
        exclude_category = overrides.get("exclude_category") or None
        filter = "category ne '{}'".format(exclude_category.replace("'", "''")) if exclude_category else None

        if overrides.get("semantic_ranker"):
            r = self.search_client.search(q, 
                                          filter=filter,
                                          query_type=QueryType.SEMANTIC, 
                                          query_language="en-us", 
                                          query_speller="lexicon", 
                                          semantic_configuration_name="default", 
                                          top=top, 
                                          query_caption="extractive|highlight-false" if use_semantic_captions else None)
        else:
            r = self.search_client.search(q, filter=filter, top=top)
        if use_semantic_captions:
            results = [doc[self.sourcepage_field] + ": " + nonewlines(" . ".join([c.text for c in doc['@search.captions']])) for doc in r]
        else:
            results = [doc[self.sourcepage_field] + ": " + nonewlines(doc[self.content_field]) for doc in r]
        content = "\n".join(results)

        messages = [{'role': self.SYSTEM, 'content': self.template.format(sources=content)}, 
                    {'role': self.USER, 'content': f"Question: {q}"}]
        
        chat_completion = openai.ChatCompletion.create(
            deployment_id=self.openai_deployment,
            model=self.chatgpt_model,
            messages=messages, 
            temperature=0.7, 
            max_tokens=1024, 
            n=1)

        return {"data_points": results, "answer": chat_completion.choices[0].message.content}
