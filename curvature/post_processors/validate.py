# -*- coding: UTF-8 -*-
import sys

class Validate(object):
    @classmethod
    def parse(cls, argv):
        return cls()

    def process(self, iterable):
        try:
            for collection in iterable:
                errors = []
                previous = None
                i = 0
                total = len(collection['ways'])
                for way in collection['ways']:
                    i += 1
                    if previous == None:
                        previous = way
                    else:
                        # check that the first ref is the same as the last of the previous
                        if way['refs'][0] != previous['refs'][-1]:
                            errors.append('{} of {}. Way {} first refs {} != previous way {} last refs {}'.format(i, total, way['id'], way['refs'][0], previous['id'], previous['refs'][-1]))

                        # check that the first coord is the same as the last of the previous
                        if way['coords'][0] != previous['coords'][-1]:
                            errors.append('{} of {}. Way {} first coord {} != previous way {} last coord {}'.format(i, total, way['id'], way['coords'][0], previous['id'], previous['coords'][-1]))

                        # check that the start of our first segment matches the end of the last way's last segment.
                        if 'segments' in way and way['segments'][0]['start'] != previous['segments'][-1]['end']:
                            errors.append('{} of {}. Way {} first segment start {} != previous way {} last segment end {}'.format(i, total, way['id'], way['segments'][0]['start'], previous['id'], previous['segments'][-1]['end']))

                        # On the the next.
                        previous = way

            if len(errors):
                i = 0
                for way in collection['ways']:
                    i += 1
                    sys.stderr.write("{} of {}, id: {}, first_ref: {}, last_ref: {}\n".format(i, total, way['id'], way['refs'][0], way['refs'][-1]))
                sys.stderr.write("\n")
                for error in errors:
                    sys.stderr.write("Error: {}\n".format(error))
        except:
            e = sys.exc_info()[0]
            errors.append('Exception: {}\nCollection: {}'.format(e, collection))
        yield collection
