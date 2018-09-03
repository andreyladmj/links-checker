from multiprocessing.pool import Pool
from random import shuffle

import grequests
import os

from check_links import iterate_by_batch

def get_links():
    urls = []
    with open('statistic-lab.txt', 'r') as file:
        for line in file.readlines():
            components = line.split(';')
            domain = components[0]
            site = components[1]
            count = int(components[2].rstrip())

            urls += [(domain, site)] * count

    shuffle(urls)
    return urls


def exception_handler(request, exception):
    print('Exception', request.url, exception)

def do_something(response, **kwargs):
    #  'apparent_encoding', 'close', 'connection', 'content', 'cookies', 'elapsed', 'encoding', 'headers', 'history', 'is_permanent_redirect', 'is_redirect', 'iter_content', 'iter_lines', 'json', 'links', 'next', 'ok', 'raise_for_status', 'raw', 'reason', 'request', 'status_code', 'text', 'url'
    print('GET', response.url, response.status_code, kwargs)

def get_urls(links):
    print(os.getpid(), len(links))
    chunk_count = 0
    chinking = 200

    chunking = iterate_by_batch(links, chinking, None)

    for chunk in chunking:
        chunk_count += 1
        print(os.getpid(), 'Chunk: ', chunk_count, 'of', len(links) / chinking)
        results = []

        for link_pair in chunk:
            domain = link_pair[0]
            url = link_pair[1]
            headers = {'referer': domain, 'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
            results.append(grequests.get(url, headers=headers, hooks = {'response' : do_something}))

        grequests.map(results, exception_handler=exception_handler)

        print('results', results)

def run():
    links = get_links()
    batch_size = len(links) // os.cpu_count() + 1
    print('Links: {}, Batch Size: {}'.format(len(links), batch_size))

    batches = iterate_by_batch(links, batch_size, None)

    with Pool(processes=os.cpu_count()) as pool:
        res = pool.map(get_urls, batches, 1)


if __name__ == '__main__':
    run()