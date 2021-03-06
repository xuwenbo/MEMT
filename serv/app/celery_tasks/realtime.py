# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import requests
import json

from datetime import datetime
from datetime import timedelta

from celery.schedules import crontab
from celery.decorators import periodic_task

from bson.json_util import dumps
from flask import current_app as app

from app import socketio
from app import celery

from app.extensions import mongo

from app.common import rt_map_namespace
from app.common import rt_feed_namespace


@celery.task(name="app.celery_tasks.realtime.rt_feed", bind=True)
def rt_feed(self):
    print("FEED")
    feeds_collection = mongo.db.feed
    now = datetime.utcnow()
    from_ = now - timedelta(minutes=now.minute % 5 + app.config["FEED_REFRESH"], seconds=now.second, microseconds=now.microsecond)
    feeds = feeds_collection.find()
    socketio.emit("update", dumps(feeds), namespace=rt_feed_namespace)


@celery.task(name="app.celery_tasks.realtime.rt_map", bind=True)
def rt_map(self):
    print("MAP")
    assets_collection = mongo.db.assets
    now = datetime.utcnow()
    from_ = now - timedelta(minutes=now.minute % 5 + app.config["RTMAP_REFRESH"], seconds=now.second, microseconds=now.microsecond)
    assets = assets_collection.find({"ipmeta.country": {"$ne": "unknown"}}, {"ipmeta.iso_code": 1, "ipmeta.city": 1, "ipmeta.country": 1, "ipmeta.geo": 1})
    socketio.emit("update", dumps(assets), namespace=rt_map_namespace)


