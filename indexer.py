from multiprocessing.pool import Pool
from os.path import dirname, join
from random import shuffle

import grequests
import os

from check_links import iterate_by_batch


def get_links():
    urls = []
    with open(join(dirname(__file__), 'statistic-lab.txt'), 'r') as file:
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


def check_site_response(response, **kwargs):
    print('GET', response.url, 'Status:', response.status_code, end=', ')

    if response.status_code == 301:
        print('redirected to', response.headers.get('Location'), end=', ')

    # print('kwargs:', kwargs)
    print('')


def get_urls(links):
    print('Process', os.getpid(), 'got links:', len(links))
    chunk_count = 0
    chinking = 200

    chunking = iterate_by_batch(links, chinking, None)

    for chunk in chunking:
        chunk_count += 1
        print('Process', os.getpid(), 'Chunk: ', chunk_count, 'of', len(links) / chinking)
        results = []

        for link_pair in chunk:
            if link_pair:
                domain = link_pair[0]
                url = link_pair[1]
                headers = {'referer': domain,
                           'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
                results.append(grequests.get(url, headers=headers, hooks={'response': check_site_response}))

        grequests.map(results, exception_handler=exception_handler, size=16, gtimeout=12)

    print('Finished: ', os.getpid())


def run():
    links = get_links()
    batch_size = len(links) // os.cpu_count() + 1
    print('Links: {}, Batch Size: {}'.format(len(links), batch_size))

    batches = iterate_by_batch(links, batch_size, None)

    with Pool(processes=os.cpu_count()) as pool:
        res = pool.map(get_urls, batches, 1)


if __name__ == '__main__':
    run()
