from utils.utils import load_pickle

if __name__ == '__main__':
    data = load_pickle('find_comments.pkl')
    processed_links = data['processed_links']
    links_to_process = data['links_to_process']
    links_with_comments_form = data['links_with_comments_form']
    processed_domains = data['processed_domains']

    with open('processed_links.txt', 'w') as file:
        for link in data['processed_links']:
            file.write("{}\n".format(link))

    with open('links_to_process.txt', 'w') as file:
        for link in data['links_to_process']:
            file.write("{}\n".format(link))

    with open('links_with_comments_form.txt', 'w') as file:
        for link in data['links_with_comments_form']:
            file.write("{}\n".format(link))

    with open('processed_domains.txt', 'w') as file:
        for link in data['processed_domains']:
            file.write("{}\n".format(link))
