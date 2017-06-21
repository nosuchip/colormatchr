# -*- coding: utf-8 -*-

import os
import pymongo
import requests

from pymongo.errors import DuplicateKeyError

SEARCH_TERMS = [
    'paris', 'nature', 'mountain', 'water', 'cabin', 'forest', 'elder', 'cave',
    'dive', 'insects', 'machinery', 'shoping', 'hiking', 'rooftop', 'flowers', 'plants', 'trees']
    'caperaoul', 'tasmania', 'discovertasmania', 'coast', 'view', 'hikingworking', 'workoutbuddy',
    'fitness', 'fitlife', 'fitfam', 'fitgirls', 'fit', 'fitnessgoals', 'healthandfitness', 'healthyliving',
    'healthandwellness', 'healthylife', 'healthylifestyle', 'hiking', 'fitspo', 'lamornings', 'happiness',
    'nature', 'hikingcanada', 'southmountain', 'phoenix', 'hikearizona', 'hikeaz', 'southmountaintrails',
    'arizona', 'liveauthentic', 'surfstyle', 'surflife', 'vanlifediaries', 'purenature', 'travelgram',
    'thefernwehcollective', 'morocco', 'surf', 'outdoors', 'oceanmy', 'walkingwales',
    'adventurer', 'dreamer', 'life', 'photooftheday', 'thursday', 'morningsun', 'sunshine', 'sunrise',
    'gratitude', 'travelphotography', 'selfie', 'outdoorlife', 'sunnyday',
    'instanature', 'likeforfollow', 'kaumkusam', 'mendaki', 'norhordland', 'manger', 'walking', 'forest',
    'muathai', 'bodylove', 'skinnyminny', 'thepresetfactory', 'winterscape', '1500ft', 'scotland', 'scottish',
    'highlands', 'privateisland', 'lochmoidart', 'landscapephotography', 'landscape', 'summer', 'camp',
    'mountains', 'love', 'a6000', 'outdoor', 'backpacking', 'fishing', 'friends',
    'roadtrip', 'thailand', 'folkscenery', 'kitesurf', 'kitesurfing', 'india'
]


FLICKR_URL = 'https://api.flickr.com/services/rest'
FLICKR_PARAMS = {
    'sort': 'relevance',
    'parse_tags': 1,
    'content_type': 'NaN',
    'extras': 'can_comment,count_comments,count_faves,description,isfavorite,license,media,needs_interstitial,owner_name,path_alias,realname,rotation,url_c,url_l,url_m,url_n,url_q,url_s,url_sq,url_t,url_z',
    'lan3': 'en-US',
    'license': '1,2,3,4,5,6,9',
    'viewerNSID': '',
    'method': 'flickr.photos.search',
    'csrf': '',
    'api_key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'format': 'json',
    'hermes': 1,
    'hermesClient': 1,
    'reqId': '387002a8',
    'nojsoncallback': 1,

    'page': 1,
    'text': 'paris',
    'per_page': '500',
}


class ImageParser(object):
    def __init__(self):
        self.client = pymongo.MongoClient(os.getenv('MONGO_DB_URI'))
        self.db = self.client.colormatchr
        self.last_downloaded = set()

    def make_json_request(self, data=None):
        params = FLICKR_PARAMS.copy()
        if data:
            params.update(data)

        resp = requests.get(FLICKR_URL, params=params)
        if resp.status_code == 200:
            try:
                return resp.json()
            except:
                pass

        return None

    def get_all_terms(self):
        for term in SEARCH_TERMS:
            print('>> get_all_terms:: processing term', term)

            self.get_all_json(term)


    def get_all_json(self, term, start_page=1):
        """Retrieve JSON from flickr, parse `photos.photo` get 'id', `url_l`, `url_l_cdn`, `height_l`, `width_l` and store as object to queue"""

        page = start_page
        while True:
            print('>> get_all_json:: processing page', page, 'of', term)

            if page > 500:
                return

            jsn = self.make_json_request(data={'text': term, 'page': page})

            if not jsn:
                return
            else:
                already_drafted = 0

                photos = jsn.get('photos', {}).get('photo', [])

                if not photos:
                    return

                for photo in photos:
                    draft = {
                        'id': str(photo.get('id')),
                        'url': photo.get('url_l_cdn') or photo.get('url_l'),
                        'width': photo.get('width_l'),
                        'height': photo.get('height_l')
                    }

                    try:
                        self.db.drafts.insert_one(draft)
                        print('>> get_all_json: page', photo['id'],'successfully drafted')
                    except DuplicateKeyError:
                        print('>> get_all_json:: image with same ID already drafted', photo['id'], already_drafted, 'of', len(photos))
                        already_drafted += 1

                        if already_drafted == len(photos):
                            print('>> get_all_json:: all photos in serie already drafted')
                            return

                page += 1

if __name__ == '__main__':
    parser = ImageParser()
    parser.get_all_terms()
