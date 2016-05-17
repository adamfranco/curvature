# -*- coding: UTF-8 -*-
class AddWayLength(object):
    @classmethod
    def parse(cls, argv):
        return cls()

    def process(self, iterable):
        for collection in iterable:
            for way in collection['ways']:
                segments = way['segments']
                sum = 0
                for segment in segments:
                    sum += segment['length']
                way['length'] = sum
            yield(collection)
