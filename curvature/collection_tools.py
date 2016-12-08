
class CollectionSplitter(object):

    def create_result_collection(self, collection):
      result_collection = dict((key,value) for key, value in collection.items() if key != 'ways')
      result_collection['ways'] = []
      return result_collection
