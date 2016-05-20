# -*- coding: UTF-8 -*-
import argparse
from curvature.collection_tools import CollectionSplitter
from curvature.match import And
from curvature.match import Or
from curvature.match import Not
from curvature.match import TagEmpty
from curvature.match import TagEquals

class FilterOutWays(CollectionSplitter):
    def __init__(self, match_expression):
        self.match_expression = eval(match_expression)
        try:
            if not callable(self.match_expression.match):
                raise ValueError('match expression must support a "match" method.')
        except AttributeError:
            raise ValueError('match expression must support a "match" method.')

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='filter_out_ways', description='Filter out ways based on a match expression.')
        parser.add_argument('--match', type=str, required=True, help='A match expression such as \'And(TagEmpty("name"), TagEmpty("ref"), TagEquals("highway", "residential"), TagEquals("tiger:reviewed", "no"))\'')
        args = parser.parse_args(argv)
        return cls(args.match)

    def process(self, iterable):
        for collection in iterable:
            result_collection = self.create_result_collection(collection)
            for way in collection['ways']:
                # If we've hit a matching way, yield any previous results and start a new collection.
                # No need to yield anything if we don't have any previous results.
                if self.match_expression.match(way):
                    if result_collection['ways']:
                        yield(result_collection)
                        result_collection = self.create_result_collection(collection)
                else:
                    result_collection['ways'].append(way)

            # Yield the remaining collection.
            if result_collection['ways']:
                yield(result_collection)
