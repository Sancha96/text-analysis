from parser import Parser
import json, io
from wordcloud import WordCloud
import collections
from datetime import datetime
from natasha import (
  NewsEmbedding,
  NewsMorphTagger,
  NewsSyntaxParser,
  NewsNERTagger,
  PER,
  LOC,
  Doc,
  Segmenter,
  MorphVocab,
  AddrExtractor,
  DatesExtractor,
  MoneyExtractor,
  NamesExtractor,
)

parser = Parser()
articles = parser.scraping("блокчейн")

countArticles = len(articles)

newsEmbedding = NewsEmbedding()
newsMorphTagger = NewsMorphTagger(newsEmbedding)
newsSyntaxParser = NewsSyntaxParser(newsEmbedding)
newsNERTagger = NewsNERTagger(newsEmbedding)
segmenter = Segmenter()
morphVocab = MorphVocab()
addrExtractor = AddrExtractor(morphVocab)
datesExtractor = DatesExtractor(morphVocab)
moneyExtractor = MoneyExtractor(morphVocab)
namesExtractor = NamesExtractor(morphVocab)

tags = []
persons = []

def getNames(text):
  doc = Doc(text)
  doc.segment(segmenter)
  doc.tag_morph(newsMorphTagger)
  doc.parse_syntax(newsSyntaxParser)
  doc.tag_ner(newsNERTagger)

  solves = []
  for token in doc.tokens:
    if (token.rel == "nsubj:pass" or token.rel == "amod" or token.rel == "nmod") and token.pos == "NOUN":
      token.lemmatize(morphVocab)
      solves.append(token.lemma)

  arr = collections.Counter(solves).most_common()
  articles_tags = [element[0] for element in arr if element[1] > 5]
  for i in articles_tags:
    tags.append(i)

  for span in doc.spans:
    if span.type == PER:
      span.normalize(morphVocab)
      span.extract_fact(namesExtractor)

  dict = {_.normal: _.fact.as_dict for _ in doc.spans if _.fact}
  name_dict = list(set(dict))
  for i in name_dict:
    persons.append(i)

def createTagsCloud(str_time):
  wordcloud = WordCloud(
    width = 1920,
    height = 1080,
    random_state=1,
    background_color='black',
    margin=10,
    colormap='Pastel1',
    collocations=False
  ).generate(" ".join(list(set(tags))))
  wordcloud.to_file(r"TagCloud - " + str_time + ".png")

def save(str_time):
  with io.open(r"Persons - " + str_time + ".json", 'w', encoding='utf-8') as f:
    json.dump(list(set(persons)), f, indent=4, ensure_ascii=False)

for article in articles:
  getNames(article["content"])

str_time = datetime.now().strftime('%m.%d.%y %H-%M-%S')
createTagsCloud(str_time)
save(str_time)

