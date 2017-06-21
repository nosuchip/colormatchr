# -*- coding: utf-8 -*-

import os
import pymongo
from application.config import db_settings


pymongo_client = pymongo.MongoClient(db_settings.DATABASE_URI)
db = pymongo_client[db_settings.DATABASE_NAME]
