# -*- coding: UTF-8 -*-
class AddWayCurvature(object):
    @classmethod
    def parse(cls, argv):
        return cls()

    def process(self, iterable):
        for collection in iterable:
            for way in collection:
                sum = 0
                for segment in way['segments']:
                    sum += segment['curvature']
                way['curvature'] = sum
            yield(collection)
