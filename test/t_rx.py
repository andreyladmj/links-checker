from rx import Observable, Observer
from rx.subjects import Subject

#tornado

# class PrintObserver(Observer):
class PrintObserver(Subject):
    """https://auth0.com/blog/reactive-programming-in-python/"""

    def on_next(self, value):
        print("Received {0}".format(value))

    def on_completed(self):
        print("Done!")

    def on_error(self, error):
        print("Error Occurred: {0}".format(error))

    def on_close(self):
        self.combine_latest_sbs.dispose()
        print("WebSocket closed")



if __name__ == '__main__':
    source = Observable.from_list([1,2,3,4,5,6])

    s = source.subscribe(PrintObserver())
    s.dispose()

    # source = Observable.from_list([1,2,3,4,5,6])
    #
    # source.subscribe(lambda value: print("Received {0}".format(value)))