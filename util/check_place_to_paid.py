from time import sleep, time

import requests

def get_execution_time(start_time):
    diff = int(time() - start_time)
    return format_time(diff)

def format_time(time):
    hours = time // 3600 % 24
    minutes = time // 60 % 60
    seconds = time % 60
    return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)


if __name__ == '__main__':

    for i in range(10):
        start_request_time = time()
        session = requests.Session()
        session.auth = ("test", "Q8UtsemJHZEJxOnE")
        hostname = "https://place2paid-prediction.edusson-data-science.com"
        response = session.get(hostname + '/api/v1/orders/1')
        print("")
        print(response)
        print('Status code', response.status_code, 'Response', response.content)
        print(response.content)
        print('Request Time:', get_execution_time(start_request_time), 'Start Time', format_time(start_request_time), 'End Time', format_time(time()))
        sleep(1)

# curl --user edusson:'+vju7VwmhNXz]9(.' https://place2paid-prediction.edusson-data-science.com/api/v1/orders/1092872
# curl --insecure --user edusson:'+vju7VwmhNXz]9(.' https://dev.place2paid.edusson-data-science.com/api/v1/orders/1092872
# curl --insecure --user edusson:'+vju7VwmhNXz]9(.' http://0.0.0.0:5000/api/v1/orders/1092872
