# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chord.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0b\x63hord.proto\"\"\n\x08NodeInfo\x12\n\n\x02id\x18\x01 \x01(\x05\x12\n\n\x02ip\x18\x02 \x01(\t\"\"\n\x14\x46indSuccessorRequest\x12\n\n\x02id\x18\x01 \x01(\x05\"A\n\x15\x46indSuccessorResponse\x12\n\n\x02id\x18\x01 \x01(\x05\x12\n\n\x02ip\x18\x02 \x01(\t\x12\x10\n\x08is_final\x18\x03 \x01(\x08\"4\n\x1a\x46indSuccessorsPredResponse\x12\n\n\x02id\x18\x01 \x01(\x05\x12\n\n\x02ip\x18\x02 \x01(\t\"\x82\x01\n\tDebugInfo\x12\x1e\n\x0bpredecessor\x18\x01 \x01(\x0b\x32\t.NodeInfo\x12\x1c\n\tsuccessor\x18\x02 \x01(\x0b\x32\t.NodeInfo\x12\x1c\n\tself_node\x18\x03 \x01(\x0b\x32\t.NodeInfo\x12\x19\n\x06\x66table\x18\x04 \x03(\x0b\x32\t.NodeInfo\"7\n\x18getSuccessorListResponse\x12\x1b\n\x08succList\x18\x01 \x03(\x0b\x32\t.NodeInfo\"\x07\n\x05\x45mpty\"4\n\rNotifyRequest\x12\x15\n\rpredecessorId\x18\x01 \x01(\x05\x12\x0c\n\x04\x61\x64\x64r\x18\x02 \x01(\t\"@\n\x04Pair\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x0b\n\x03len\x18\x02 \x01(\x05\x12\x0f\n\x07seq_num\x18\x03 \x01(\x05\x12\r\n\x05\x61\x64\x64rs\x18\x04 \x03(\t\" \n\x0eNotifyResponse\x12\x0e\n\x06result\x18\x01 \x01(\x05\"\x17\n\x05\x43hunk\x12\x0e\n\x06\x62uffer\x18\x01 \x01(\x0c\"D\n\x0eGetFileRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tsignature\x18\x02 \x01(\x0c\x12\x11\n\tpublickey\x18\x03 \x01(\x0c\"!\n\x0fPutFileResponse\x12\x0e\n\x06length\x18\x01 \x01(\x05\x32\xa9\x03\n\x0c\x43hordService\x12@\n\rfindSuccessor\x12\x15.FindSuccessorRequest\x1a\x16.FindSuccessorResponse\"\x00\x12;\n\x12\x66indSuccessorsPred\x12\x06.Empty\x1a\x1b.FindSuccessorsPredResponse\"\x00\x12\x1d\n\x05\x64\x65\x62ug\x12\x06.Empty\x1a\n.DebugInfo\"\x00\x12+\n\x06notify\x12\x0e.NotifyRequest\x1a\x0f.NotifyResponse\"\x00\x12$\n\x10\x63heckPredecessor\x12\x06.Empty\x1a\x06.Empty\"\x00\x12\x1e\n\ncheckAlive\x12\x06.Empty\x1a\x06.Empty\"\x00\x12\x37\n\x10getSuccessorList\x12\x06.Empty\x1a\x19.getSuccessorListResponse\"\x00\x12\'\n\x07putFile\x12\x06.Chunk\x1a\x10.PutFileResponse\"\x00(\x01\x12&\n\x07getFile\x12\x0f.GetFileRequest\x1a\x06.Chunk\"\x00\x30\x01\x32r\n\x10\x42ootstrapService\x12\x1e\n\x07getNode\x12\x06.Empty\x1a\t.NodeInfo\"\x00\x12\x1e\n\x07\x61\x64\x64Node\x12\t.NodeInfo\x1a\x06.Empty\"\x00\x12\x1e\n\nclearTable\x12\x06.Empty\x1a\x06.Empty\"\x00\x62\x06proto3')



_NODEINFO = DESCRIPTOR.message_types_by_name['NodeInfo']
_FINDSUCCESSORREQUEST = DESCRIPTOR.message_types_by_name['FindSuccessorRequest']
_FINDSUCCESSORRESPONSE = DESCRIPTOR.message_types_by_name['FindSuccessorResponse']
_FINDSUCCESSORSPREDRESPONSE = DESCRIPTOR.message_types_by_name['FindSuccessorsPredResponse']
_DEBUGINFO = DESCRIPTOR.message_types_by_name['DebugInfo']
_GETSUCCESSORLISTRESPONSE = DESCRIPTOR.message_types_by_name['getSuccessorListResponse']
_EMPTY = DESCRIPTOR.message_types_by_name['Empty']
_NOTIFYREQUEST = DESCRIPTOR.message_types_by_name['NotifyRequest']
_PAIR = DESCRIPTOR.message_types_by_name['Pair']
_NOTIFYRESPONSE = DESCRIPTOR.message_types_by_name['NotifyResponse']
_CHUNK = DESCRIPTOR.message_types_by_name['Chunk']
_GETFILEREQUEST = DESCRIPTOR.message_types_by_name['GetFileRequest']
_PUTFILERESPONSE = DESCRIPTOR.message_types_by_name['PutFileResponse']
NodeInfo = _reflection.GeneratedProtocolMessageType('NodeInfo', (_message.Message,), {
  'DESCRIPTOR' : _NODEINFO,
  '__module__' : 'chord_pb2'
  # @@protoc_insertion_point(class_scope:NodeInfo)
  })
_sym_db.RegisterMessage(NodeInfo)

FindSuccessorRequest = _reflection.GeneratedProtocolMessageType('FindSuccessorRequest', (_message.Message,), {
  'DESCRIPTOR' : _FINDSUCCESSORREQUEST,
  '__module__' : 'chord_pb2'
  # @@protoc_insertion_point(class_scope:FindSuccessorRequest)
  })
_sym_db.RegisterMessage(FindSuccessorRequest)

FindSuccessorResponse = _reflection.GeneratedProtocolMessageType('FindSuccessorResponse', (_message.Message,), {
  'DESCRIPTOR' : _FINDSUCCESSORRESPONSE,
  '__module__' : 'chord_pb2'
  # @@protoc_insertion_point(class_scope:FindSuccessorResponse)
  })
_sym_db.RegisterMessage(FindSuccessorResponse)

FindSuccessorsPredResponse = _reflection.GeneratedProtocolMessageType('FindSuccessorsPredResponse', (_message.Message,), {
  'DESCRIPTOR' : _FINDSUCCESSORSPREDRESPONSE,
  '__module__' : 'chord_pb2'
  # @@protoc_insertion_point(class_scope:FindSuccessorsPredResponse)
  })
_sym_db.RegisterMessage(FindSuccessorsPredResponse)

DebugInfo = _reflection.GeneratedProtocolMessageType('DebugInfo', (_message.Message,), {
  'DESCRIPTOR' : _DEBUGINFO,
  '__module__' : 'chord_pb2'
  # @@protoc_insertion_point(class_scope:DebugInfo)
  })
_sym_db.RegisterMessage(DebugInfo)

getSuccessorListResponse = _reflection.GeneratedProtocolMessageType('getSuccessorListResponse', (_message.Message,), {
  'DESCRIPTOR' : _GETSUCCESSORLISTRESPONSE,
  '__module__' : 'chord_pb2'
  # @@protoc_insertion_point(class_scope:getSuccessorListResponse)
  })
_sym_db.RegisterMessage(getSuccessorListResponse)

Empty = _reflection.GeneratedProtocolMessageType('Empty', (_message.Message,), {
  'DESCRIPTOR' : _EMPTY,
  '__module__' : 'chord_pb2'
  # @@protoc_insertion_point(class_scope:Empty)
  })
_sym_db.RegisterMessage(Empty)

NotifyRequest = _reflection.GeneratedProtocolMessageType('NotifyRequest', (_message.Message,), {
  'DESCRIPTOR' : _NOTIFYREQUEST,
  '__module__' : 'chord_pb2'
  # @@protoc_insertion_point(class_scope:NotifyRequest)
  })
_sym_db.RegisterMessage(NotifyRequest)

Pair = _reflection.GeneratedProtocolMessageType('Pair', (_message.Message,), {
  'DESCRIPTOR' : _PAIR,
  '__module__' : 'chord_pb2'
  # @@protoc_insertion_point(class_scope:Pair)
  })
_sym_db.RegisterMessage(Pair)

NotifyResponse = _reflection.GeneratedProtocolMessageType('NotifyResponse', (_message.Message,), {
  'DESCRIPTOR' : _NOTIFYRESPONSE,
  '__module__' : 'chord_pb2'
  # @@protoc_insertion_point(class_scope:NotifyResponse)
  })
_sym_db.RegisterMessage(NotifyResponse)

Chunk = _reflection.GeneratedProtocolMessageType('Chunk', (_message.Message,), {
  'DESCRIPTOR' : _CHUNK,
  '__module__' : 'chord_pb2'
  # @@protoc_insertion_point(class_scope:Chunk)
  })
_sym_db.RegisterMessage(Chunk)

GetFileRequest = _reflection.GeneratedProtocolMessageType('GetFileRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETFILEREQUEST,
  '__module__' : 'chord_pb2'
  # @@protoc_insertion_point(class_scope:GetFileRequest)
  })
_sym_db.RegisterMessage(GetFileRequest)

PutFileResponse = _reflection.GeneratedProtocolMessageType('PutFileResponse', (_message.Message,), {
  'DESCRIPTOR' : _PUTFILERESPONSE,
  '__module__' : 'chord_pb2'
  # @@protoc_insertion_point(class_scope:PutFileResponse)
  })
_sym_db.RegisterMessage(PutFileResponse)

_CHORDSERVICE = DESCRIPTOR.services_by_name['ChordService']
_BOOTSTRAPSERVICE = DESCRIPTOR.services_by_name['BootstrapService']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _NODEINFO._serialized_start=15
  _NODEINFO._serialized_end=49
  _FINDSUCCESSORREQUEST._serialized_start=51
  _FINDSUCCESSORREQUEST._serialized_end=85
  _FINDSUCCESSORRESPONSE._serialized_start=87
  _FINDSUCCESSORRESPONSE._serialized_end=152
  _FINDSUCCESSORSPREDRESPONSE._serialized_start=154
  _FINDSUCCESSORSPREDRESPONSE._serialized_end=206
  _DEBUGINFO._serialized_start=209
  _DEBUGINFO._serialized_end=339
  _GETSUCCESSORLISTRESPONSE._serialized_start=341
  _GETSUCCESSORLISTRESPONSE._serialized_end=396
  _EMPTY._serialized_start=398
  _EMPTY._serialized_end=405
  _NOTIFYREQUEST._serialized_start=407
  _NOTIFYREQUEST._serialized_end=459
  _PAIR._serialized_start=461
  _PAIR._serialized_end=525
  _NOTIFYRESPONSE._serialized_start=527
  _NOTIFYRESPONSE._serialized_end=559
  _CHUNK._serialized_start=561
  _CHUNK._serialized_end=584
  _GETFILEREQUEST._serialized_start=586
  _GETFILEREQUEST._serialized_end=654
  _PUTFILERESPONSE._serialized_start=656
  _PUTFILERESPONSE._serialized_end=689
  _CHORDSERVICE._serialized_start=692
  _CHORDSERVICE._serialized_end=1117
  _BOOTSTRAPSERVICE._serialized_start=1119
  _BOOTSTRAPSERVICE._serialized_end=1233
# @@protoc_insertion_point(module_scope)
