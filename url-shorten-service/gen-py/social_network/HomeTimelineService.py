#
# Autogenerated by Thrift Compiler (0.12.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec

import sys
import logging
from .ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport
all_structs = []


class Iface(object):
    def ReadHomeTimeline(self, req_id, user_id, start, stop, carrier):
        """
        Parameters:
         - req_id
         - user_id
         - start
         - stop
         - carrier

        """
        pass

    def WriteHomeTimeline(self, req_id, post_id, user_id, timestamp, user_mentions_id, carrier):
        """
        Parameters:
         - req_id
         - post_id
         - user_id
         - timestamp
         - user_mentions_id
         - carrier

        """
        pass


class Client(Iface):
    def __init__(self, iprot, oprot=None):
        self._iprot = self._oprot = iprot
        if oprot is not None:
            self._oprot = oprot
        self._seqid = 0

    def ReadHomeTimeline(self, req_id, user_id, start, stop, carrier):
        """
        Parameters:
         - req_id
         - user_id
         - start
         - stop
         - carrier

        """
        self.send_ReadHomeTimeline(req_id, user_id, start, stop, carrier)
        return self.recv_ReadHomeTimeline()

    def send_ReadHomeTimeline(self, req_id, user_id, start, stop, carrier):
        self._oprot.writeMessageBegin('ReadHomeTimeline', TMessageType.CALL, self._seqid)
        args = ReadHomeTimeline_args()
        args.req_id = req_id
        args.user_id = user_id
        args.start = start
        args.stop = stop
        args.carrier = carrier
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_ReadHomeTimeline(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = ReadHomeTimeline_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.success is not None:
            return result.success
        if result.se is not None:
            raise result.se
        raise TApplicationException(TApplicationException.MISSING_RESULT, "ReadHomeTimeline failed: unknown result")

    def WriteHomeTimeline(self, req_id, post_id, user_id, timestamp, user_mentions_id, carrier):
        """
        Parameters:
         - req_id
         - post_id
         - user_id
         - timestamp
         - user_mentions_id
         - carrier

        """
        self.send_WriteHomeTimeline(req_id, post_id, user_id, timestamp, user_mentions_id, carrier)
        self.recv_WriteHomeTimeline()

    def send_WriteHomeTimeline(self, req_id, post_id, user_id, timestamp, user_mentions_id, carrier):
        self._oprot.writeMessageBegin('WriteHomeTimeline', TMessageType.CALL, self._seqid)
        args = WriteHomeTimeline_args()
        args.req_id = req_id
        args.post_id = post_id
        args.user_id = user_id
        args.timestamp = timestamp
        args.user_mentions_id = user_mentions_id
        args.carrier = carrier
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_WriteHomeTimeline(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = WriteHomeTimeline_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.se is not None:
            raise result.se
        return


class Processor(Iface, TProcessor):
    def __init__(self, handler):
        self._handler = handler
        self._processMap = {}
        self._processMap["ReadHomeTimeline"] = Processor.process_ReadHomeTimeline
        self._processMap["WriteHomeTimeline"] = Processor.process_WriteHomeTimeline

    def process(self, iprot, oprot):
        (name, type, seqid) = iprot.readMessageBegin()
        if name not in self._processMap:
            iprot.skip(TType.STRUCT)
            iprot.readMessageEnd()
            x = TApplicationException(TApplicationException.UNKNOWN_METHOD, 'Unknown function %s' % (name))
            oprot.writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
            x.write(oprot)
            oprot.writeMessageEnd()
            oprot.trans.flush()
            return
        else:
            self._processMap[name](self, seqid, iprot, oprot)
        return True

    def process_ReadHomeTimeline(self, seqid, iprot, oprot):
        args = ReadHomeTimeline_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = ReadHomeTimeline_result()
        try:
            result.success = self._handler.ReadHomeTimeline(args.req_id, args.user_id, args.start, args.stop, args.carrier)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except ServiceException as se:
            msg_type = TMessageType.REPLY
            result.se = se
        except TApplicationException as ex:
            logging.exception('TApplication exception in handler')
            msg_type = TMessageType.EXCEPTION
            result = ex
        except Exception:
            logging.exception('Unexpected exception in handler')
            msg_type = TMessageType.EXCEPTION
            result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
        oprot.writeMessageBegin("ReadHomeTimeline", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_WriteHomeTimeline(self, seqid, iprot, oprot):
        args = WriteHomeTimeline_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = WriteHomeTimeline_result()
        try:
            self._handler.WriteHomeTimeline(args.req_id, args.post_id, args.user_id, args.timestamp, args.user_mentions_id, args.carrier)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except ServiceException as se:
            msg_type = TMessageType.REPLY
            result.se = se
        except TApplicationException as ex:
            logging.exception('TApplication exception in handler')
            msg_type = TMessageType.EXCEPTION
            result = ex
        except Exception:
            logging.exception('Unexpected exception in handler')
            msg_type = TMessageType.EXCEPTION
            result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
        oprot.writeMessageBegin("WriteHomeTimeline", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

# HELPER FUNCTIONS AND STRUCTURES


class ReadHomeTimeline_args(object):
    """
    Attributes:
     - req_id
     - user_id
     - start
     - stop
     - carrier

    """


    def __init__(self, req_id=None, user_id=None, start=None, stop=None, carrier=None,):
        self.req_id = req_id
        self.user_id = user_id
        self.start = start
        self.stop = stop
        self.carrier = carrier

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.I64:
                    self.req_id = iprot.readI64()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.I64:
                    self.user_id = iprot.readI64()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.I32:
                    self.start = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.I32:
                    self.stop = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.MAP:
                    self.carrier = {}
                    (_ktype172, _vtype173, _size171) = iprot.readMapBegin()
                    for _i175 in range(_size171):
                        _key176 = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                        _val177 = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                        self.carrier[_key176] = _val177
                    iprot.readMapEnd()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('ReadHomeTimeline_args')
        if self.req_id is not None:
            oprot.writeFieldBegin('req_id', TType.I64, 1)
            oprot.writeI64(self.req_id)
            oprot.writeFieldEnd()
        if self.user_id is not None:
            oprot.writeFieldBegin('user_id', TType.I64, 2)
            oprot.writeI64(self.user_id)
            oprot.writeFieldEnd()
        if self.start is not None:
            oprot.writeFieldBegin('start', TType.I32, 3)
            oprot.writeI32(self.start)
            oprot.writeFieldEnd()
        if self.stop is not None:
            oprot.writeFieldBegin('stop', TType.I32, 4)
            oprot.writeI32(self.stop)
            oprot.writeFieldEnd()
        if self.carrier is not None:
            oprot.writeFieldBegin('carrier', TType.MAP, 5)
            oprot.writeMapBegin(TType.STRING, TType.STRING, len(self.carrier))
            for kiter178, viter179 in self.carrier.items():
                oprot.writeString(kiter178.encode('utf-8') if sys.version_info[0] == 2 else kiter178)
                oprot.writeString(viter179.encode('utf-8') if sys.version_info[0] == 2 else viter179)
            oprot.writeMapEnd()
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(ReadHomeTimeline_args)
ReadHomeTimeline_args.thrift_spec = (
    None,  # 0
    (1, TType.I64, 'req_id', None, None, ),  # 1
    (2, TType.I64, 'user_id', None, None, ),  # 2
    (3, TType.I32, 'start', None, None, ),  # 3
    (4, TType.I32, 'stop', None, None, ),  # 4
    (5, TType.MAP, 'carrier', (TType.STRING, 'UTF8', TType.STRING, 'UTF8', False), None, ),  # 5
)


class ReadHomeTimeline_result(object):
    """
    Attributes:
     - success
     - se

    """


    def __init__(self, success=None, se=None,):
        self.success = success
        self.se = se

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 0:
                if ftype == TType.LIST:
                    self.success = []
                    (_etype183, _size180) = iprot.readListBegin()
                    for _i184 in range(_size180):
                        _elem185 = Post()
                        _elem185.read(iprot)
                        self.success.append(_elem185)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 1:
                if ftype == TType.STRUCT:
                    self.se = ServiceException()
                    self.se.read(iprot)
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('ReadHomeTimeline_result')
        if self.success is not None:
            oprot.writeFieldBegin('success', TType.LIST, 0)
            oprot.writeListBegin(TType.STRUCT, len(self.success))
            for iter186 in self.success:
                iter186.write(oprot)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        if self.se is not None:
            oprot.writeFieldBegin('se', TType.STRUCT, 1)
            self.se.write(oprot)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(ReadHomeTimeline_result)
ReadHomeTimeline_result.thrift_spec = (
    (0, TType.LIST, 'success', (TType.STRUCT, [Post, None], False), None, ),  # 0
    (1, TType.STRUCT, 'se', [ServiceException, None], None, ),  # 1
)


class WriteHomeTimeline_args(object):
    """
    Attributes:
     - req_id
     - post_id
     - user_id
     - timestamp
     - user_mentions_id
     - carrier

    """


    def __init__(self, req_id=None, post_id=None, user_id=None, timestamp=None, user_mentions_id=None, carrier=None,):
        self.req_id = req_id
        self.post_id = post_id
        self.user_id = user_id
        self.timestamp = timestamp
        self.user_mentions_id = user_mentions_id
        self.carrier = carrier

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.I64:
                    self.req_id = iprot.readI64()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.I64:
                    self.post_id = iprot.readI64()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.I64:
                    self.user_id = iprot.readI64()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.I64:
                    self.timestamp = iprot.readI64()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.LIST:
                    self.user_mentions_id = []
                    (_etype190, _size187) = iprot.readListBegin()
                    for _i191 in range(_size187):
                        _elem192 = iprot.readI64()
                        self.user_mentions_id.append(_elem192)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 6:
                if ftype == TType.MAP:
                    self.carrier = {}
                    (_ktype194, _vtype195, _size193) = iprot.readMapBegin()
                    for _i197 in range(_size193):
                        _key198 = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                        _val199 = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                        self.carrier[_key198] = _val199
                    iprot.readMapEnd()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('WriteHomeTimeline_args')
        if self.req_id is not None:
            oprot.writeFieldBegin('req_id', TType.I64, 1)
            oprot.writeI64(self.req_id)
            oprot.writeFieldEnd()
        if self.post_id is not None:
            oprot.writeFieldBegin('post_id', TType.I64, 2)
            oprot.writeI64(self.post_id)
            oprot.writeFieldEnd()
        if self.user_id is not None:
            oprot.writeFieldBegin('user_id', TType.I64, 3)
            oprot.writeI64(self.user_id)
            oprot.writeFieldEnd()
        if self.timestamp is not None:
            oprot.writeFieldBegin('timestamp', TType.I64, 4)
            oprot.writeI64(self.timestamp)
            oprot.writeFieldEnd()
        if self.user_mentions_id is not None:
            oprot.writeFieldBegin('user_mentions_id', TType.LIST, 5)
            oprot.writeListBegin(TType.I64, len(self.user_mentions_id))
            for iter200 in self.user_mentions_id:
                oprot.writeI64(iter200)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        if self.carrier is not None:
            oprot.writeFieldBegin('carrier', TType.MAP, 6)
            oprot.writeMapBegin(TType.STRING, TType.STRING, len(self.carrier))
            for kiter201, viter202 in self.carrier.items():
                oprot.writeString(kiter201.encode('utf-8') if sys.version_info[0] == 2 else kiter201)
                oprot.writeString(viter202.encode('utf-8') if sys.version_info[0] == 2 else viter202)
            oprot.writeMapEnd()
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(WriteHomeTimeline_args)
WriteHomeTimeline_args.thrift_spec = (
    None,  # 0
    (1, TType.I64, 'req_id', None, None, ),  # 1
    (2, TType.I64, 'post_id', None, None, ),  # 2
    (3, TType.I64, 'user_id', None, None, ),  # 3
    (4, TType.I64, 'timestamp', None, None, ),  # 4
    (5, TType.LIST, 'user_mentions_id', (TType.I64, None, False), None, ),  # 5
    (6, TType.MAP, 'carrier', (TType.STRING, 'UTF8', TType.STRING, 'UTF8', False), None, ),  # 6
)


class WriteHomeTimeline_result(object):
    """
    Attributes:
     - se

    """


    def __init__(self, se=None,):
        self.se = se

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRUCT:
                    self.se = ServiceException()
                    self.se.read(iprot)
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('WriteHomeTimeline_result')
        if self.se is not None:
            oprot.writeFieldBegin('se', TType.STRUCT, 1)
            self.se.write(oprot)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(WriteHomeTimeline_result)
WriteHomeTimeline_result.thrift_spec = (
    None,  # 0
    (1, TType.STRUCT, 'se', [ServiceException, None], None, ),  # 1
)
fix_spec(all_structs)
del all_structs

