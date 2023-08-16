import re

def nonewlines(s: str) -> str:
    return s.replace('\n', ' ').replace('\r', ' ')

def remove_html_tags(text_with_tags):
    clean_text = re.sub(r'<.*?>', '', text_with_tags)
    return clean_text