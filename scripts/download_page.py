import requests, os, argparse
from bs4 import BeautifulSoup, Comment
from markdownify import markdownify

utf_8 = '<meta http-equiv="Content-type" content="text/html; charset=utf-8" />\n'
domain_name = 'http://ess-wiki.advantech.com.tw'
file_path = 'download/'

def download_not_web(url: str):
    path = file_path + 'not_web/' + url.split('/')[-1]
    with open(path, 'wb') as f:
        f.write(requests.get(url).content)

def download_page(url: str):
    domain_name = f"{url.split('/')[0]}//{url.split('/')[2]}"

    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')

        # file name
        file_name = soup.find('h1', class_='firstHeading').text.strip().replace(' ', '_').replace('/', '_').replace(':', '_')
        if file_name == 'Login_required':
            print('Cannot access this page')
            return

        # 內文
        page_content = soup.find('div', class_='mw-content-ltr')

        # remove contents(toc)
        if soup.find('div', id='toc'):
            soup.find('div', id='toc').extract()
        
        # remove comments
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for c in comments:
            c.extract()

        # remove useless tags
        retrieve_url = soup.find('div', class_='printfooter')
        for e in retrieve_url.find_all_next():
            e.extract()
        retrieve_url.extract()

        soup.find('div', {'id': 'siteSub'}).decompose(),  soup.find('div', {'id': 'contentSub'}).decompose(), soup.find('div', {'id': 'jump-to-nav'}).decompose()

        # images
        imgs = page_content.find_all('img')
        hrefs = page_content.find_all('a', href=True)

        # edit img src that start with '/'(relative path)
        if len(imgs) != 0:
            for img_link in imgs:
                if img_link['src'].startswith('/'):
                    img_link['src'] = domain_name + img_link['src']
        
        # edit href that start with '/'(relative path)
        if len(hrefs) != 0:
            for href in hrefs:
                if href['href'].startswith('/'):
                    href['href'] = domain_name + href['href']

        html = soup.find('div', class_='mw-content-ltr')

        if html.find('h1') != None:
            for heading in html.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                heading.name = 'h' + str(int(heading.name[1]) + 1)

        # add title h1
        head_tag = soup.new_tag('h1')
        head_tag.string = file_name
        head_tag['class'], head_tag['id'] = 'firstHeading', 'firstHeading'
        html.insert(0, head_tag)

        # edit retrieve url which is the real url of the page
        comment = Comment(f' URL: {url} ')
        html.insert(-1, comment)

        open(f'{file_path}{file_name}.html', 'w', encoding='utf-8').write(utf_8 + str(html))
        open(f'{file_path}{file_name}.md', 'w', encoding='utf-8').write(markdownify(str(html), heading_style='ATX').replace('\n\n', '\n'))
    except Exception as e:
        print(f'============= error: {e} =============')

    print(f'Download {file_name} successfully!')

def download_whole_page(url: str):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    md = markdownify(soup.get_text(), heading_style='ATX', keep_inline_images_in=['a']).replace('\n\n', '\n')
    open(f'{file_path}{url.split("/")[-1]}.md', 'w', encoding='utf-8').write(md)
    open(f'{file_path}{url.split("/")[-1]}.html', 'w', encoding='utf-8').write(utf_8 + soup.prettify())

def download_forum(url: str):
    forum_domain = "https:/"+"/".join(url.split("/")[1:3])
    topic_id = url.split("/")[-1]
    api_content = {
        "forum_domain": forum_domain,
        "topic_id": topic_id,
        "reply_nums" : [],
        "get_all": True
    }
    response = requests.get("https://adventech-webhook.azurewebsites.net/retrieve", json=api_content)
    open(f'{file_path}{url.split("/")[-2]}.md', 'w', encoding='utf-8').write(response.json().get('markdown'))
    open(f'{file_path}{url.split("/")[-2]}.html', 'w', encoding='utf-8').write(utf_8 + response.json().get('html'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download a single page from the url you provide, and we will save the page as html and markdown format in the folder you specify.",
        epilog="Example 1: python download_page.py --url 'http://ess-wiki.advantech.com.tw/view/WISE-Agent' --folder 'download/' --type 'wiki'\nExample 2: python download_page.py --url 'https://samm.discourse.group/t/question-on-epc-r7200/34' --folder 'download/' --type discourse --postnums 1 3"
    )
    parser.add_argument('--url', type=str, help='The url of the page you want to download')
    parser.add_argument('--folder', type=str, help='The folder where you want to save the file, if the folder doesn\'t exist, the program will create one for you')
    parser.add_argument('--type', type=str, required=False, help='The type indicates which class you want to download, e.g. wiki, forum, etc. If you didn\'t specify the type, the program will just download the whole page')
    parser.add_argument('--postnums', type=int, nargs='+', help="orders of the posts (starts from 1; 0 means to retrieve all)")
    args = parser.parse_args()

    # check folder
    file_path = args.folder if args.folder else file_path
    file_path += '/' if not file_path.endswith('/') else ''

    if not os.path.exists(file_path):
        os.mkdir(file_path)
    
    print(f'Start downloading {args.url}...')
    if args.type == None:
        download_whole_page(args.url)
    elif args.type == 'wiki':
        download_page(args.url)
    elif args.type == 'forum':
        download_forum(args.url)


# %%
"""
!!!!!!!!! Warning !!!!!!!!!
在使用前，請先前往markdownify的source code.
1. 在convert_a(self, el, text, convert_as_inline)的return前，加上href的判斷式，如下:
    if text.strip()[0] == '!':  href = False    # 如果是圖片，就不要加上href
   因為有些圖片的<img>還會再用<a>包起來，這樣會造成圖片的連結失效

如果其他的東西還有問題的話，請參考以下:
1. 請將chomp(text)中約第38行的 text = text.strip() 改為 text = text.replace("\n", " ").strip()
2. 將convert_hn(self, n, el, text, convert_as_inline)中約第 269 行中的 text = text.rstrip() 改為 text = text.replace('\n', ' ')
"""