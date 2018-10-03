#http://astro.uson.mx/webalizer/usage_201706.html
#http://astro.uson.mx/webalizer/usage_201810.html#TOPREFS
#approx 755 + 290

import grequests

site = 'http://astro.uson.mx'

referer = 'https://designshack.net/member/teresamcallistermcallister'

grequests_results = []

c = 0
total = 800
def check_site_response_decorator(response, *args, **kwargs):
    global c
    c += 1
    print(c, 'of', total)

def exception_handler(request, exception):
    print(exception)


headers = {'referer': referer,
           'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

if __name__ == '__main__':
    for i in range(total):
        grequests_results.append(grequests.get(site, headers=headers, hooks={'response': check_site_response_decorator}, timeout=10))

    try:
        results = grequests.map(grequests_results, exception_handler=exception_handler, size=16)
    except Exception as e:
        print('Exception', str(e))

'''

Top 15 of 153 Total User Agents
#	Hits	User Agent
1	76	9.91%	Mozilla/5.0 (compatible; SemrushBot/2~bl; +http://www.semrush.com/bot.html)
2	34	4.43%	Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36
3	27	3.52%	Mozilla/5.0 (compatible; AhrefsBot/5.2; +http://ahrefs.com/robot/)
4	24	3.13%	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36 OPR/54.0.2
5	20	2.61%	Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36 OPR/54.0.29
6	19	2.48%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36
7	17	2.22%	Mozilla/5.0 (Linux; Android 6.0; ZTE BLADE V7 LITE Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100
8	16	2.09%	Mozilla/5.0 (Linux; Android 5.1.1; E6603 Build/32.0.A.6.152) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobi
9	16	2.09%	Mozilla/5.0 (Linux; Android 6.0; MYA-L13 Build/HUAWEIMYA-L13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mob
10	16	2.09%	Mozilla/5.0 (Linux; Android 7.0; HUAWEI VNS-L23 Build/HUAWEIVNS-L23) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.
11	16	2.09%	Mozilla/5.0 (Linux; Android 7.0; SM-A310M Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Sa
12	16	2.09%	Mozilla/5.0 (Linux; Android 7.1.1; Moto G (5S) Plus Build/NPSS26.116-26-18) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.
13	16	2.09%	Mozilla/5.0 (Linux; Android 8.0.0; F5121 Build/34.4.A.2.118) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobi
14	12	1.56%	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36 OPR/53.0.
15	12	1.56%	Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36 OPR/53.0.2
'''