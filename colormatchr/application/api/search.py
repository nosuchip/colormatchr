# -*- coding: utf-8 -*-

import math
from bson.son import SON
from flask import request
from flask.views import MethodView
from application.common.decorators import api_result
from application.api.base import response_ok
from application.database import db
from application.config import settings


class SearchApiView(MethodView):
    decorators = [api_result]

    def get(self):
        color = request.args.get('color')
        if color.startswith('#'):
            color = color[1:]

        color = color.upper()

        try:
            page = int(request.args.get('page'))
        except:
            page = 1

        if not page:
            page = 1

        skip = (page-1) * settings.ITEMS_PER_PAGE
        limit = settings.ITEMS_PER_PAGE

        pipeline = [
            # Filter only records with that contains desired color in `colors` collection
            {'$match': {'colors.color': color}},

            # Filtering out all records in `colors` that does not match provided color
            # I.e. keep only one array item from `colors`
            {'$project': {
                'url': 1,
                'colors': {
                    '$filter': {
                        'input': '$colors',
                        'as': 'color',
                        'cond': {'$eq': ['$$color.color', color]}
                    }
                }
            }},

            # Flatten `colors` array to object
            {'$unwind': '$colors'},

            # Unwind `colors` object to one-level object
            {'$project': {
                'url': 1,
                'color': '$colors.color',
                'frequency': '$colors.frequency',
                'hue': '$colors.hue'
            }},

            # Sort result set
            {'$sort': SON([('frequency', -1)])}
        ]

        docs_count = db.images.aggregate(pipeline +  [{'$count': "total"}])
        total = -1

        try:
            total = docs_count.next().get('total')
        except:
            pass

        docs = db.images.aggregate(pipeline + [
            # Skip previous pages
            {'$skip': skip},

            # Take only items for one page
            {'$limit': limit}
        ])

        return response_ok(data={
            'images': [{'url': doc['url']} for doc in docs if 'url' in doc],
            'pages': math.ceil(total / settings.ITEMS_PER_PAGE),
            'page': page
        })
        #return response_ok(data=data)
