# -*- coding: UTF-8 -*-
import argparse
from curvature.match import And
from curvature.match import Or
from curvature.match import Not
from curvature.match import TagEmpty
from curvature.match import TagEquals
from curvature.match import TagContains
from curvature.match import TagRegex
from curvature.match import TagAndValueRegex
from curvature.match import Id

class SquashCurvatureForWays(object):
    def __init__(self, match_expression):
        self.match_expression = eval(match_expression)
        try:
            if not callable(self.match_expression.match):
                raise ValueError('match expression must support a "match" method.')
        except AttributeError:
            raise ValueError('match expression must support a "match" method.')

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='squash_curvature_for_tagged_ways', description='Squash the curvature on ways with certain properties.')
        parser.add_argument('--match', type=str, required=True, help='A match expression such as \'TagAndValueRegex("^junction$", "^(roundabout|circular)$")\'')
        args = parser.parse_args(argv)
        return cls(args.match)

    def process(self, iterable):
        for collection in iterable:
            for way in collection['ways']:
                # If we've hit a matching way, set its curvature to 0.
                if self.match_expression.match_way(way):
                    if 'curvature' in way:
                        way['curvature'] = 0
                    for segment in way['segments']:
                        if 'curvature' in segment:
                            segment['curvature'] = 0
                        if 'curvature_level' in segment:
                            segment['curvature_level'] = 0
            yield(collection)
