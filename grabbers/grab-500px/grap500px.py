# -*- coding: utf-8 -*-

import os
import pymongo
import requests

from pymongo.errors import DuplicateKeyError

URL = 'https://webapi.500px.com/licensing'

PARAMS = {
    'q': None,
    'page': None,

    'type': 'market',
    'availability': 'prime,subprime,editorial,subeditorial,presubmitted,submitted',
    'image_size': ['31', '32', '33', '34', '35', '36', '2048'],
    'include_states': False,
    'formats': 'jpeg,lytro',
    'include_tags': False,
    'exclude_nude': False,
    'rpp': '500'
}

SEARCH_TERMS = [
    'paris', 'nature', 'mountain', 'water', 'cabin', 'forest', 'elder', 'cave',
    'dive', 'insects', 'machinery', 'shoping', 'hiking', 'rooftop', 'flowers', 'plants', 'trees'
    'caperaoul', 'tasmania', 'discovertasmania', 'coast', 'view', 'hikingworking', 'workoutbuddy',
    'fitness', 'fitlife', 'fitfam', 'fitgirls', 'fit', 'fitnessgoals', 'healthandfitness', 'healthyliving',
    'healthandwellness', 'healthylife', 'healthylifestyle', 'hiking', 'fitspo', 'lamornings',
    'happiness', 'nature',
    'hikingcanada', 'southmountain', 'phoenix', 'hikearizona', 'hikeaz', 'southmountaintrails',
    'arizona', 'liveauthentic', 'surfstyle', 'surflife', 'vanlifediaries', 'purenature', 'travelgram',
    'thefernwehcollective', 'morocco', 'surf', 'outdoors', 'oceanmy', 'walkingwales',
    'adventurer', 'dreamer', 'life', 'photooftheday', 'thursday', 'morningsun', 'sunshine', 'sunrise',
    'gramtitude', 'travelphotography', 'selfie', 'outdoorlife', 'sunnyday',
    'instanature', 'likeforfollow', 'kaumkusam', 'mendaki', 'norhordland', 'manger', 'walking', 'forest',
    'muathai', 'bodylove', 'skinnyminny', 'thepresetfactory', 'winterscape', '1500ft', 'scotland', 'scottish',
    'highlands', 'privateisland', 'lochmoidart', 'landscapephotography', 'landscape', 'summer', 'camp',
    'mountains', 'love', 'a6000', 'outdoor', 'backpacking',
    'fishing', 'friends', 'girls', 'canyon', 'pinup', 'backpack',
    'roadtrip', 'thailand', 'folkscenery', 'kitesurf', 'kitesurfing', 'india', 'fireplace'
    'Woman', 'Mother', 'Mom', 'Mum', 'Parent',
    'Adult', 'Child', 'Baby', 'Family',
    'Happy', 'Happiness', 'Bonding', 'Closeness', 'Togetherness', 'Embrace', 'Hug',
    'Love', 'Smile', 'Smiling',
    'Summer', 'Sunset', 'Sunshine', 'Golden', 'Warm Light',
    'Backlit', 'Outside', 'Toronto', 'Ontario', 'Canada', 'North America',
    'City', 'Cityscape', 'Skyline', 'Architecture', 'Building', 'Skyscraper',
    'Office Tower', 'High Rise', 'Dusk', 'Dawn', 'Twilight', 'Modern',
    'Contemporary', 'Design', 'Business', 'Finance', 'Illuminated', 'Travel',
    'Travel and Tourism', 'Travel Destination', 'City Life', 'Urban', 'Sprawling',
    'Elevated View', 'High Angle View', 'Blue', 'Blue Hour', 'NYC', 'New York City',
    'New York', 'USA', 'United States', 'America', 'North America', 'City', 'Capital City',
    'Manhattan', 'Empire State Building', 'One World Trade Centre', 'Freedom Tower',
    'Skyscraper', 'Buildings', 'Office Tower', 'High Rise', 'Skyline',
    'Cityscape', 'Sky', 'Clouds', 'Morning', 'Dawn', 'Sunrise', 'Bird', 'Seagull',
    'Bird\'s Eye View', 'Elevated View', 'Freedom', 'Travel', 'Travel and Tourism',
    'Travel Destination', 'Famous Place', 'Tourist Attraction', 'International Landmark',
    'Bagan', 'Myanmar', 'Burma', 'Mandalay', 'Asia', 'Southeast Asia',
    'Hot Air Balloon', 'Field', 'Trees', 'Sunset', 'Sunrise', 'Pagoda', 'Temple',
    'Buddhist Temple', 'Building', 'Architecture', 'Traditional', 'Ancient',
    'Historic', 'Historical', 'Heritage', 'Buddhism', 'Sacred', 'Holy Place',
    'Spiritual', 'Religious', 'Atmospheric', 'Backlit', 'Silhouette', 'Fog', 'Haze',
    'Warm Tone', 'Golden Hour', 'Golden', 'Scenic', 'Landscape', 'View', 'Vista',
    'Breathtaking', 'Tranquil', 'Tranquility', 'Serene', 'Serenity', 'Elevated View',
    'Adventure', 'Freedom', 'Travel', 'Tourism', 'Travel Destination', 'Upper Antelope Canyon',
    'Arizona', 'USA', 'United States', 'North America', 'Antelope Canyon',
    'Slot Canyon', 'Navajo', 'Sandstone', 'Erosion', 'Geology', 'Sand',
    'Rock', 'Rock Formation', 'Sunlight', 'Long Exposure', 'Orange', 'Red',
    'Vibrant', 'Natural Landmark', 'Travel', 'Tourism', 'Travel Destination',
    'Tranquil', 'Serene', 'Arid'
]


class ImageParser(object):
    def __init__(self):
        self.client = pymongo.MongoClient(os.getenv('MONGO_DB_URI'))
        self.db = self.client.colormatchr

    def make_json_request(self, data=None):
        params = PARAMS.copy()
        if data:
            params.update(data)
        resp = requests.get(URL, params=params)
        if resp.status_code == 200:
            try:
                return resp.json()
            except:
                pass

        return None

    def get_all_terms(self, start_page=1):
        for term in SEARCH_TERMS:
            print('>> get_all_terms:: processing term', term)

            self.get_all_json(term, start_page)

    def get_all_json(self, term, start_page=1):
        """Retrieve JSON from flickr, parse `photos[]` get 'id',  and store as object to queue"""

        page, start_page = start_page, 1


        while True:
            print('>> get_all_json:: processing page', page, 'of', term)

            if page > 1000:
                return

            jsn = self.make_json_request(data={'q': term, 'page': page})

            if not jsn:
                return
            else:
                already_drafted = 0

                photos = jsn.get('photos', {})

                if not photos:
                    return

                for photo in photos:
                    img = max(photo.get('images', []), key=lambda x: x['size'])

                    if img:
                        draft = {
                            'id': str(photo.get('id')),
                            'url': img.get('url') or img.get('https_url'),
                            'width': None,
                            'height': None,
                            'source': '500px'
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
    parser.get_all_terms(1)
