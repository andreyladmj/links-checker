import requests,time
from random import randint

with open('1.txt','r') as f:
   lines = f.readlines()
   for i in lines: #÷икл дл¤ выемки строк
       i.rstrip() #Cрез разделител¤ новой строки
       split_i=i.split(';') #—резаем по знаку ; получаем массив трЄх значений


       how_many_queries=split_i[2].rstrip()
       how_many_queries_int=int(how_many_queries)
       what_is_my_domain=split_i[1].rstrip()
       whats_domain_to_spam=split_i[0].rstrip()

       print('Start to Spam -> '+whats_domain_to_spam)
       print('By Reffer -> '+what_is_my_domain)
       print(how_many_queries+' Queries')


       domain = what_is_my_domain
       my_domain = whats_domain_to_spam
       how_many = how_many_queries_int-1
       counter = 0


       while counter <= how_many:
           try:

               s = requests.Session()
               s.headers.update({'referer': domain,
                             'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'})
               s.get(my_domain)
               counter += 1
           #сегмент задержки
           #delay = randint(0, 9) / 10

           #time.sleep(delay)

           #print('query #', counter,'with ', delay, 'sec. delay')
               print('query #', counter)

           except Exception:
               counter+=1999
               print("Time Out Error or some Exception")