import json
import re

import bs4


JSON_LOG_REGEX = re.compile(r'.*?({.*}).*', re.DOTALL)

def get_all_log_blobs(file):
    soup = bs4.BeautifulSoup(file, 'html.parser')

    for row in soup.find_all('div', attrs={'class': 'log-row'}):
        time_div = row.div.find('div', attrs={'class': 'time'})
        data_div = row.div.find('div', attrs={'class': 'header-text'})
        if data_div.string is None:
            continue

        match = JSON_LOG_REGEX.match(data_div.string)
        if not match:
            continue

        yield (time_div['title'], json.loads(f'[{match.group(1)}]'))


if __name__ == '__main__':
    with open('logs/mtga/sample.htm') as f:
        blobs = get_all_log_blobs(f)

        for (time, blob) in blobs:
            print(time)
            print(blob)
            print()