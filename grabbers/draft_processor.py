# -*- coding: utf-8 -*-

import io
import os.path
import asyncio
import logging
import logging.config
import aiohttp
import pymongo
import colorsys
import statistics

from collections import Counter
from contextlib import closing
from PIL import Image


CONCURRENT_WORKES = 10


class ImageProcessor(object):
    LOGGING_CONFIG = {
        'version': 1,
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'filename': 'image_processor.log',
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'image-processor': {
                'level': 'DEBUG',
                'handlers': ['console', 'file']
            }
        }
    }

    COLORS_NUMBER = 100
    THUMB_WIDTH = 200
    THUMB_HEIGHT = 200

    def __init__(self):
        self.client = pymongo.MongoClient(os.getenv('MONGO_DB_URI'))
        self.db = self.client.colormatchr

        logging.config.dictConfig(self.LOGGING_CONFIG)
        self.logger = logging.getLogger('image-processor')

        self.db.images.create_index([('colors.color', pymongo.ASCENDING)])

    def analyse_image(self, buffer, draft):
        image = Image.open(buffer)
        thumb = image.resize((self.THUMB_WIDTH, self.THUMB_HEIGHT))
        filename = os.path.basename(draft['url'])

        self.logger.info('Begin image {} processing'.format(filename))

        freq = Counter([pixel for pixel in image.getdata()])
        most_common = freq.most_common(self.COLORS_NUMBER)

        doc = {
            'url': draft['url'],
            'colors': []
        }

        hues = []

        for pixel, freq in most_common:
            color = '{:02X}{:02X}{:02X}'.format(*pixel)
            hue, sat, value = colorsys.rgb_to_hsv(*pixel)
            hues.append(hue)

            doc['colors'].append({
                'color': color,
                'frequency': freq,
                'hue': hue
            })

        doc['hue_median'] = statistics.median(hues)

        self.db.images.insert(doc)
        self.db.drafts.update({'_id': draft['_id']}, {'$set': {'processed': True}})
        self.logger.info('Image {} processed'.format(filename))

    @asyncio.coroutine
    def download(self, doc, session, semaphore, chunk_size=1<<15):
        with (yield from semaphore):
            try:
                url = doc['url']
                filename = os.path.basename(url)

                self.logger.info('Downloading {}'.format(filename))

                response = yield from session.get(url)
                with closing(response):
                    buffer = io.BytesIO()
                    while True:
                        chunk = yield from response.content.read(chunk_size)
                        if not chunk:
                            break
                        buffer.write(chunk)
                    buffer.seek(0)

                    self.logger.info('Downloaded {}'.format(filename))
                    self.analyse_image(buffer, doc)
            except Exception as ex:
                self.logger.error('Exception occurs while downloading file "{}": {}'.format(url, ex))
                self.logger.exception(ex)
        return filename, (response.status, tuple(response.headers.items()))


    def process_all_items(self):
        documents = self.db.drafts.find({'processed': {'$ne': True}}, no_cursor_timeout=True).limit(300)

        with closing(asyncio.get_event_loop()) as loop, closing(aiohttp.ClientSession()) as session:
            semaphore = asyncio.Semaphore(CONCURRENT_WORKES)
            download_tasks = (self.download(doc, session, semaphore) for doc in documents)
            result = loop.run_until_complete(asyncio.gather(*download_tasks))


if __name__ == '__main__':
    processor = ImageProcessor()
    processor.process_all_items()
