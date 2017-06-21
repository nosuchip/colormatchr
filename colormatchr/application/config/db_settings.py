# -*- coding: utf-8 -*-

import os

DATABASE_URI = os.getenv('MONGO_DB_URI')
DATABASE_NAME = os.getenv('MONGO_DB_NAME', 'colormatchr')
