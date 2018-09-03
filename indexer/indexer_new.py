import asyncio
import os
import random
import time
from multiprocessing.pool import Pool

import aiohttp
import requests

from check_links import iterate_by_batch


async def fetch_url(session, line):
    headers = {'referer': line['domain'], 'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
    print('get ', line['site'])
    async with session.get(line['site'], timeout=60 * 60, headers=headers) as response:
        return await response.text()


async def fetch_all_urls(session, urls, loop):
    results = await asyncio.gather(*[fetch_url(session, url) for url in urls],
                                   return_exceptions=True)
    return results


def get_htmls(urls):
    if len(urls) > 1:
        loop = asyncio.get_event_loop()
        connector = aiohttp.TCPConnector(limit=100)
        with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            htmls = loop.run_until_complete(fetch_all_urls(session, urls, loop))
        raw_result = dict(zip(urls, htmls))
    else:
        headers = {'referer': domain,
                   'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
        raw_result = requests.get(urls[0], headers=headers).text

    return raw_result


# result_dict = get_htmls(url_list)

def parse_line(line):
    components = line.split(';')
    domain = components[0]
    site = components[1]
    count = components[2].rstrip()
    print(os.getpid(), line)


def processes():
    with open('statistic-lab.txt', 'r') as file:
        with Pool(processes=os.cpu_count()) as pool:
            links = pool.map(parse_line, file.readlines(), 20)


def asyncio_loop():
    loop = asyncio.get_event_loop()
    connector = aiohttp.TCPConnector(limit=100)
    with open('statistic-lab.txt', 'r') as file:
        urls = file.readlines()

        headers = {'referer': domain,
                   'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

        with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            htmls = loop.run_until_complete(fetch_all_urls(session, urls, loop))
        raw_result = dict(zip(urls, htmls))
        print(raw_result)


def get_links():
    urls = []
    with open('statistic-lab.txt', 'r') as file:
        for line in file.readlines():
            components = line.split(';')
            domain = components[0]
            site = components[1]
            count = int(components[2].rstrip())

            for i in range(count):
                urls.append((domain, site))

    return urls


def tt(lines):
    print(os.getpid(), len(lines))
    #time.sleep(2 + random.randint(1,3))

    # loop = asyncio.get_event_loop()
    # connector = aiohttp.TCPConnector(limit=100)
    # with aiohttp.ClientSession(loop=loop, connector=connector) as session:
    #     htmls = loop.run_until_complete(fetch_all_urls(session, urls, loop))
    # raw_result = dict(zip(urls, htmls))


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(lines))

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def maind(lines):
    loop = asyncio.get_event_loop()
    connector = aiohttp.TCPConnector(limit=100)
    with aiohttp.ClientSession(loop=loop, connector=connector) as session:
        htmls = loop.run_until_complete(fetch_all_urls(session, lines, loop))
    raw_result = dict(zip(lines, htmls))
    print(raw_result)

async def main(lines):
    is_running = True
    current_iteration = 0

    loop = asyncio.get_event_loop()
    connector = aiohttp.TCPConnector(limit=5)
    async with aiohttp.ClientSession(loop=loop, connector=connector) as session:

        while is_running:
            print('current_iteration', current_iteration, 'PID', os.getpid())
            line = lines[current_iteration]
            #print(line)

            if line['count'] > 0:
                line['count'] -= 1

                headers = {'referer': line['domain'], 'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
                print('get site')
                async with session.get(line['site'], headers=headers) as response:
                    # await asyncio.sleep(0.2)
                    # pass
                    html = await response.text()
                    print(line['site'], response.status)

            current_iteration += 1

            if line['count'] == 0:
                print('filter lines')
                lines = list(filter(lambda x: x['count'] > 0, lines))

            try:
                line = lines[current_iteration]
            except IndexError:
                current_iteration = 0

            is_running = len(lines) != 0
            print('')



if __name__ == '__main__':
    links = get_links()
    batch_size = len(links) // os.cpu_count() + 1
    print('Links: {}, Batch Size: {}'.format(len(links), batch_size))

    batches = iterate_by_batch(links, batch_size, None)

    with Pool(processes=os.cpu_count()) as pool:
        res = pool.map(tt, batches, 1)
        print('RES')
