import logging
import redis
import functools
from retrying import retry
from timeitd import timeit
import time 
import pymysql.cursors

#TODO replace Redis with MySQL for added safety
r = redis.Redis(host='localhost', port=6379, db=0)



class api_call:
    """
    A decorator that gets the number of API calls remaining from Redis. If there are no calls 
    remaining a ValueError will be raised saying so. Otherwise the number_of_calls_requested will be 
    substracted from the number_of_calls for the api in the Redis Key-Value Store. 
    """

    def __init__(self, api, max_attempts=3):
        """
        Class constructor that takes the api as a string, number_of_calls that will be run for the function
        and the max number of attempts to retry the function
        """
        self.api = api
        self.max_attempts = max_attempts
    
    def __call__(self, function, *args, **kwargs):
        """
        Python Magic Method that wraps the function so it can be retried and API calls can be checked.
        """
        @retry(stop_max_attempt_number=self.max_attempts, wait_random_min=1000, wait_random_max=2000)
        def wrapper(*args, **kwargs):
            if 'number_of_requests' not in kwargs:
                raise RuntimeError("Number of requests not found in the function kwargs")
            r.set_response_callback('GET', int)
            current_number_of_calls = r.get(self.api)
            print("There are " + str(current_number_of_calls) + " number of calls remaining for " + self.api)
            if current_number_of_calls - kwargs['number_of_requests'] < 0:
                raise ValueError("There are not enough API calls remaining for " + self.api)
            try:
                value = function(*args, **kwargs)
                r.mset({self.api: current_number_of_calls - kwargs['number_of_requests']})
            except ValueError as e:
                print("Non-200 status code received")
                raise ValueError("Non 200 status code received")
            print("There are now " + str(r.get(self.api)) + " number of calls remaining for " + self.api)
            return value
        return wrapper


def set_api_calls(api, calls):
    r.mset({api: calls})


@api_call(api="RPV")
def call_RPV(**kwargs):
    print("Trying")
    return True


if __name__ == '__main__':
    def run():
        for i in range(0, 10000):
            call_RPV(number_of_requests=1)
    times = []
    for i in range(0, 10):
        start = time.time()     
        run()
        end = time.time()
        runtime = end - start
        times.append(runtime)
        print(end - start)
    average = sum(times) / len(times)
    print("The average is " + str(average) )
