from compiler import decorators

@decorators.service
class CastInfo(object):
    def __init__(self):
        self.cast_infos = {} # type: Persistent[dict]

    def write_cast_infos(self, info):
        self.cast_infos.update([(info.CastInfoId, info)])

    def read_cast_infos(self, cast_ids: list):
        res = []
        for cast_id in cast_ids:
            res.append(self.cast_infos.get(cast_id))
        return res