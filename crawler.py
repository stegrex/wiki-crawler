import time
import pprint
import json
import urllib.request
import urllib.parse
import random

class DataNode():

    def __init__(self, title, categories, links):
        self.title = title
        self.categories = categories
        self.links = links

    def dump(self):
        return {
            'title' : self.title,
            'categories' : self.categories,
            'links' : self.links
        }

class Crawler():

    def urlify_title(self, title):
        return urllib.parse.quote_plus(title)

    def extract_links(self, linksResponse):
        output = []
        if 'query' in linksResponse and 'pages' in linksResponse['query']:
            for el in linksResponse['query']['pages']:
                if 'links' in el:
                    for link in el['links']:
                        if 'title' in link:
                            output.append(link['title'])
        return output

    def extract_categories(self, categoriesResponse):
        output = []
        if 'query' in categoriesResponse and 'pages' in categoriesResponse['query']:
            for el in categoriesResponse['query']['pages']:
                if 'categories' in el:
                    for category in el['categories']:
                        if 'title' in category:
                            output.append(category['title'])
        return output

    def crawl_result(self, title):
        endpoint = (
            'https://en.wikipedia.org/w/api.php?' +
            'action=query&prop=links&titles=' + self.urlify_title(title) +
            '&redirects&format=json&formatversion=2'
        )
        linksResponse = urllib.request.urlopen(endpoint).read().decode('utf-8')
        linksResponseDict = json.loads(linksResponse)
        links = self.extract_links(linksResponseDict)
        endpoint = (
            'https://en.wikipedia.org/w/api.php?' +
            'action=query&prop=categories&titles=' + self.urlify_title(title) +
            '&redirects&format=json&formatversion=2'
        )
        categoriesResponse = urllib.request.urlopen(endpoint).read().decode('utf-8')
        categoriesResponseDict = json.loads(categoriesResponse)
        categories = self.extract_categories(categoriesResponseDict)
        if (
            'query' in linksResponseDict and
            'pages' in linksResponseDict['query'] and
            'title' in linksResponseDict['query']['pages'][0]
        ):
            title = linksResponseDict['query']['pages'][0]['title']
        node = DataNode(title, categories, links)
        return node

    def crawl_results(self, title, limit=10, bfs=False):
        global getRandom
        root = self.crawl_result(title)
        visited = {root.title : root}
        keys = [root.title]
        nodes = [root]
        count = 1
        while nodes and count <= limit:
            if bfs:
                node = nodes.pop(0)
            else:
                node = nodes.pop()
            for link in node.links:
                if link not in visited:
                    newNode = self.crawl_result(link)
                    visited[link] = newNode
                    keys.append(link)
                    nodes.append(newNode)
                    # TODO: Figure out why this doesn't work.
                    count += 1
                    if count >= limit:
                        break
        return (keys, visited)

start = time.time()

title = 'Fender Stratocaster'
limit = 10
bfs = True
#getRandom = True
crawler = Crawler()
keys, nodes = crawler.crawl_results(title, limit, bfs)
pp = pprint.PrettyPrinter()
for key in keys:
    pp.pprint(nodes[key].dump())

end = time.time()
print()
pp.pprint(keys)
print()
print('Nodes: ' + str(len(nodes)))
print('Execution time: ' + str(end - start))