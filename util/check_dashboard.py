from time import sleep, time

import requests
from datetime import datetime


def get_execution_time(start_time):
    return strfdelta(datetime.utcnow(), start_time)

def format_time(time):
    return time.strftime("%H:%M:%S.%f")

def strfdelta(end, start):
    diff = end - start
    return "{}.{}s".format(diff.seconds, diff.microseconds)

if __name__ == '__main__':

    while True:

        start_request_time = datetime.utcnow()
        session = requests.Session()
        # hostname = "https://analytics.edusson-data-science.com/writers-dashboard/bidding_coefficient/users-encrypted/YFo4UxSYYQqkM2slgaf/kg=="
        hostname = "https://dev-analytics.edusson-data-science.com/writers-dashboard/bidding_coefficient/users-encrypted/YFo4UxSYYQqkM2slgaf/kg=="

        try:
            response = session.get(hostname, timeout=5)
            content = "OK"
            status_code = response.status_code
        except Exception as e:
            content = 'Request Timeout 5s'
            status_code = 405

        s = 'Response: {}, Code: {}, Start Time: {}, End Time: {}, Execution Time: {}'.format(content,
            status_code,
            format_time(start_request_time),
            format_time(datetime.utcnow()),
            get_execution_time(start_request_time))

        print(s)
        print(response.headers)
        print(len(response.content))

        with open('1.html', 'ab') as f:
            f.write(response.content)

        raise AttributeError
        sleep(0.75)

# curl --user edusson:'+vju7VwmhNXz]9(.' https://place2paid-prediction.edusson-data-science.com/api/v1/orders/1092872
# curl --insecure --user edusson:'+vju7VwmhNXz]9(.' https://dev.place2paid.edusson-data-science.com/api/v1/orders/1092872
# curl --insecure --user edusson:'+vju7VwmhNXz]9(.' http://0.0.0.0:5000/api/v1/orders/1092872
