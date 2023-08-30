import requests
from bs4 import BeautifulSoup

# change the forum url here
url = "https://forum.aim-linux.advantech.com/categories"

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

topic_lst = set()
category_lst = set()

infos = soup.find_all('a')
for info in infos:
    if 'href' in info.attrs:
        if '/c/' in info['href']:
            category_lst.add("https://forum.aim-linux.advantech.com" + info['href'])

for category in category_lst:
    count = 0
    response = requests.get(category)
    soup = BeautifulSoup(response.content, 'html.parser')
    infos = soup.find_all('a')
    for info in infos:
        if 'href' in info.attrs:
            if '/t/' in info['href']:
                topic_lst.add(info['href'])
num = 1
for post in topic_lst:
    with open(f"./data/post_{num}.html", 'wb') as f:
        response = requests.get(post)
        soup = BeautifulSoup(response.content, 'html.parser')
        f.write(response.content)
        num += 1