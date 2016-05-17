# -*- coding: UTF-8 -*-

class AddSegments(object):

    @classmethod
    def parse(cls, argv):
        return cls()

    def process(self, iterable):
        for collection in iterable:
            for way in collection['ways']:
                way['segments'] = []
                i = 0
                for coord in way['coords']:
                    i = i + 1
                    if i < len(way['coords']):
                        way['segments'].append({
                            'start': coord,
                            'end': way['coords'][i]
                        })
            yield(collection)
