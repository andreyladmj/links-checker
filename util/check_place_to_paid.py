from time import sleep, time

import requests
from datetime import datetime


def get_execution_time(start_time):
    return strfdelta(datetime.now(), start_time)

def format_time(time):
    return time.strftime("%H:%M:%S.%f")

def strfdelta(end, start):
    diff = end - start
    return "{}.{}s".format(diff.seconds, diff.microseconds)

if __name__ == '__main__':

    while True:

        print('UTC hour', datetime.utcnow(), datetime.utcnow().hour)
        if (datetime.utcnow().hour >= 0 and datetime.utcnow().hour < 4) or datetime.utcnow().hour == 24:
            start_request_time = datetime.utcnow()
            session = requests.Session()
            session.auth = ("test", "Q8UtsemJHZEJxOnE")
            hostname = "https://place2paid-prediction.edusson-data-science.com"
            response = session.get(hostname + '/api/v1/orders/1092872')

            s = 'Get: {}, Code: {}, Request Time: {}, Start Time: {}, End Time: {}, Response: {}'.format(1092872,
                response.status_code,
                get_execution_time(start_request_time),
                format_time(start_request_time),
                format_time(datetime.utcnow()),
                response.content)

            print(s)

            with open('hour-{}.txt'.format(datetime.utcnow().hour), 'a+') as f:
                f.write(s + "\n")

            sleep(0.75)
        else:
            sleep(10)

# curl --user edusson:'+vju7VwmhNXz]9(.' https://place2paid-prediction.edusson-data-science.com/api/v1/orders/1092872
# curl --insecure --user edusson:'+vju7VwmhNXz]9(.' https://dev.place2paid.edusson-data-science.com/api/v1/orders/1092872
# curl --insecure --user edusson:'+vju7VwmhNXz]9(.' http://0.0.0.0:5000/api/v1/orders/1092872
