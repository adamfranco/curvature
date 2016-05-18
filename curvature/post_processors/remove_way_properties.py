# -*- coding: UTF-8 -*-
import argparse

class RemoveWayProperties(object):
    def __init__(self, properties):
        self.properties = properties

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='remove_way_properties', description='Strip certain properties from the ways in the data.')
        parser.add_argument('--properties', type=str, required=True, help='A comma-separated list of the keys to strip. Example --properties refs,coords')
        args = parser.parse_args(argv)
        to_strip = args.properties.split(',')
        return cls(to_strip)

    def process(self, iterable):
        for collection in iterable:
            for way in collection['ways']:
                for property in self.properties:
                    if property in way:
                        del way[property]
            yield(collection)
