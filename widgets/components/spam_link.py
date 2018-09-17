

class SpamLink:
    __slots__ = ('url', 'referer', 'count', 'is_redirect', 'status_code', 'redirect_to', 'original_count')

    def __init__(self, url, referer, count, original_count=None):
        self.url = url
        self.referer = referer
        self.count = count
        self.original_count = original_count or count
        self.is_redirect = False
        self.status_code = None
        self.redirect_to = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "{}, {}".format(self.url, self.status_code)

    def get_requests_count(self):
        return self.original_count - self.count