import json
import logging
import re

import bs4

import importer.draft_helper


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

        try:
            yield (importer.draft_helper.extract_time(time_div['title']), json.loads(f'[{match.group(1)}]'))
        except json.decoder.JSONDecodeError as e:
            logging.debug(f'Trouble parsing JSON: {match.group(0)}')
