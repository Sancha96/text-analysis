from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote

baseUrl = 'https://habr.com'
url = baseUrl + '/ru/search'

class Parser:
  def scraping(self, theme):
    page = 1
    objArticles = []
    html = urlopen(url + '/?q=' + quote(theme))
    bs = BeautifulSoup(html, "html.parser")

    lastPage = bs.find_all('a', {'class': 'tm-pagination__page'})[-1]
    # countPages = int(lastPage.get_text().strip())
    countPages = 10

    for i in range(1, countPages+1):
      html = urlopen(url + '/page' + str(page) + '/?q=' + quote(theme))
      bs = BeautifulSoup(html, "html.parser")
      articles = bs.find_all('article', {'class': 'tm-articles-list__item'})

      for article in articles:
        link = article.find("a", {"class":"tm-article-snippet__title-link"})
        if link is not None:
          title = link.text
          href = link['href']
        articleHtml = urlopen(baseUrl + href)
        bs = BeautifulSoup(articleHtml, "html.parser")
        content = bs.find('div', {'id': 'post-content-body'}).get_text()
        objArticles.append({
          'href': href,
          'title': title,
          'content': content,
        })
        print({
          'href': href,
          'title': title,
          # 'content': content,
        })

      page += 1

    return objArticles
