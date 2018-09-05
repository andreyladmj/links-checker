from xmlrpc.client import Transport, ServerProxy

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost, EditPost


class SpecialTransport(Transport):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'


if __name__ == '__main__':
    #authenticate
    wp_url = "http://ryanbradley.com/xmlrpc.php"
    wp_username = "test123123213@gmail.com"
    wp_password = "qweqweqwe"
    # wp_url = "https://colorlib.com/wp/xmlrpc.php"
    # wp_username = "test123123213@gmail.com"
    # wp_password = "qweqweqwe"

    #wp = Client('http://blog.blog.com/xmlrpc.php', 'normal_username', 'normal_password', transport=SpecialTransport())

    wp = Client(wp_url, wp_username, wp_password, transport=SpecialTransport())
    #wp = ServerProxy(wp_url, transport=SpecialTransport(), verbose=True, allow_none=True)

    print(wp.call(GetPosts()))

