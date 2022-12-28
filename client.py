import requests
import re

from datetime import datetime

from urllib.parse import urlparse
from urllib.parse import urljoin

from bs4 import BeautifulSoup

metadata_re = re.compile('\s*(\d{1,2}\-\w{3}-\d{1,5} \d{2}:\d{2})\s*(\d+)\s*')


class HTTPFileBrowser(object):
    sort_by_defaults = {
        'date': datetime.fromordinal(1),
        'size': 0,
    }
    def __init__(self, url):
        self.base_url = url
        self._dirs = {}

    def ls(self, path='.', sort_by='date'):
        path_data = self._get_path_data(path)
        sorted_path_date = sorted(
            path_data.items(),
            key=lambda item: self.sort_by_defaults[sort_by] if not sort_by in item[1] else item[1][sort_by]
        )
        return sorted_path_date

    def _get_path_data(self, path):
        url = self._make_url(path)
        url_data = urlparse(url)

        if url_data.path in self._dirs:
            return self._dirs[url_data.path]

        res = requests.get(url)
        soup = BeautifulSoup(res.content)
        body = soup.find('body')
        pre = body.find('pre')

        dir_data = {}

        # iterate every two elements in the directory list
        for a_el, metadata in zip(*[iter(pre.children)]*2):
            file_data = {}

            match = metadata_re.match(metadata)
            if match:
                file_data['date'] = datetime.strptime(match[1], '%d-%b-%Y %H:%M')
                file_data['size'] = int(match[2])

            file_key = a_el.attrs['href']
            dir_data[file_key] = file_data

        self._dirs[url_data.path] = dir_data
        return self._dirs[url_data.path]

    def _make_url(self, path):
        return urljoin(self.base_url, path)


# if __name__ == '__main__':
#     db_export_url = 'https://url/to/index_of/'
#     client = HTTPFileBrowser(url=db_export_url)
#     client.ls('.')
#     import ipdb; ipdb.set_trace()
#     pass