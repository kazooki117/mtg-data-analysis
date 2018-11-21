import os

import importer.mtga_log_helper

from db.connector import get_session


LOG_FOLDER = os.path.join('logs', 'mtga')

if __name__ == '__main__':
    session = get_session()
    for filename in os.listdir(LOG_FOLDER):
        with open(os.path.join(LOG_FOLDER, filename)) as f:
            print(filename)
            blobs = importer.mtga_log_helper.get_all_log_blobs(f)

            for (time, blob) in blobs:
                pass
                # print(time)
                # print(blob)
                # print()