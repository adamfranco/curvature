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

class InflateCurvatureForWays(object):
    def __init__(self, curvature, match_expression):
        self.curvature = curvature
        self.match_expression = eval(match_expression)
        try:
            if not callable(self.match_expression.match):
                raise ValueError('match expression must support a "match" method.')
        except AttributeError:
            raise ValueError('match expression must support a "match" method.')

    @classmethod
    def parse(cls, argv):
        parser = argparse.ArgumentParser(prog='squash_curvature_for_tagged_ways', description='Squash the curvature on ways with certain properties.')
        parser.add_argument('--curvature', type=int, default=1, help='The ammount of curvature to inflate')
        parser.add_argument('--match', type=str, required=True, help='A match expression such as \'TagAndValueRegex("^junction$", "^(roundabout|circular)$")\'')
        args = parser.parse_args(argv)
        return cls(args.curvature, args.match)

    def process(self, iterable):
        for collection in iterable:
            for way in collection['ways']:
                # If we've hit a matching way, set its curvature to 0.
                if self.match_expression.match_way(way):
                    total_added = 0
                    for segment in way['segments']:
                        total_added = total_added + self.curvature
                        if 'curvature' in segment:
                            segment['curvature'] = segment['curvature'] + self.curvature
                        else:
                            segment['curvature'] = self.curvature
                        if 'curvature_level' in segment and segment['curvature_level'] < 4:
                            segment['curvature_level'] = segment['curvature_level'] + 1
                    total_added = max(total_added, self.curvature)
                    if 'curvature' in way:
                        way['curvature'] = way['curvature'] + total_added
                    else:
                        way['curvature'] = total_added
            yield(collection)
