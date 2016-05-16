# -*- coding: UTF-8 -*-
import argparse

class RemoveWayProperties(object):
    def __init__(self, properties):
        self.properties = properties

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(description='Strip certain properties from the ways in the data.')
        parser.add_argument('--properties', type=str, help='A comma-separated list of the keys to strip. Example --properties refs,coords')
        args = parser.parse_args(argv)
        if not args.properties:
            raise RuntimeError("Error:   --properties must be specified and contain at least 1 property.\n")
        to_strip = args.properties.split(',')
        return cls(to_strip)

    def process(self, iterable):
        for collection in iterable:
            for way in collection['ways']:
                for property in self.properties:
                    if property in way:
                        del way[property]
            yield(collection)
