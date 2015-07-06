# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: auth_user.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='auth_user.proto',
  package='grpc.testing',
  syntax='proto3',
  serialized_pb=_b('\n\x0f\x61uth_user.proto\x12\x0cgrpc.testing\"@\n\x17\x41uthenticateUserRequest\x12\x13\n\x0b\x63redentials\x18\x01 \x01(\x0c\x12\x10\n\x08username\x18\x02 \x01(\t\"3\n\x15\x41uthenticateUserReply\x12\x1a\n\x12is_unique_username\x18\x01 \x01(\x08\"\'\n\x12\x43onfirmUserRequest\x12\x11\n\thashed_id\x18\x01 \x01(\t\">\n\x10\x43onfirmUserReply\x12\x18\n\x10is_authenticated\x18\x01 \x01(\x08\x12\x10\n\x08username\x18\x02 \x01(\t2\xc5\x01\n\x0e\x41uthentication\x12`\n\x10\x41uthenticateUser\x12%.grpc.testing.AuthenticateUserRequest\x1a#.grpc.testing.AuthenticateUserReply\"\x00\x12Q\n\x0b\x43onfirmUser\x12 .grpc.testing.ConfirmUserRequest\x1a\x1e.grpc.testing.ConfirmUserReply\"\x00\x62\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_AUTHENTICATEUSERREQUEST = _descriptor.Descriptor(
  name='AuthenticateUserRequest',
  full_name='grpc.testing.AuthenticateUserRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='credentials', full_name='grpc.testing.AuthenticateUserRequest.credentials', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='username', full_name='grpc.testing.AuthenticateUserRequest.username', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=33,
  serialized_end=97,
)


_AUTHENTICATEUSERREPLY = _descriptor.Descriptor(
  name='AuthenticateUserReply',
  full_name='grpc.testing.AuthenticateUserReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='is_unique_username', full_name='grpc.testing.AuthenticateUserReply.is_unique_username', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=99,
  serialized_end=150,
)


_CONFIRMUSERREQUEST = _descriptor.Descriptor(
  name='ConfirmUserRequest',
  full_name='grpc.testing.ConfirmUserRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='hashed_id', full_name='grpc.testing.ConfirmUserRequest.hashed_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=152,
  serialized_end=191,
)


_CONFIRMUSERREPLY = _descriptor.Descriptor(
  name='ConfirmUserReply',
  full_name='grpc.testing.ConfirmUserReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='is_authenticated', full_name='grpc.testing.ConfirmUserReply.is_authenticated', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='username', full_name='grpc.testing.ConfirmUserReply.username', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=193,
  serialized_end=255,
)

DESCRIPTOR.message_types_by_name['AuthenticateUserRequest'] = _AUTHENTICATEUSERREQUEST
DESCRIPTOR.message_types_by_name['AuthenticateUserReply'] = _AUTHENTICATEUSERREPLY
DESCRIPTOR.message_types_by_name['ConfirmUserRequest'] = _CONFIRMUSERREQUEST
DESCRIPTOR.message_types_by_name['ConfirmUserReply'] = _CONFIRMUSERREPLY

AuthenticateUserRequest = _reflection.GeneratedProtocolMessageType('AuthenticateUserRequest', (_message.Message,), dict(
  DESCRIPTOR = _AUTHENTICATEUSERREQUEST,
  __module__ = 'auth_user_pb2'
  # @@protoc_insertion_point(class_scope:grpc.testing.AuthenticateUserRequest)
  ))
_sym_db.RegisterMessage(AuthenticateUserRequest)

AuthenticateUserReply = _reflection.GeneratedProtocolMessageType('AuthenticateUserReply', (_message.Message,), dict(
  DESCRIPTOR = _AUTHENTICATEUSERREPLY,
  __module__ = 'auth_user_pb2'
  # @@protoc_insertion_point(class_scope:grpc.testing.AuthenticateUserReply)
  ))
_sym_db.RegisterMessage(AuthenticateUserReply)

ConfirmUserRequest = _reflection.GeneratedProtocolMessageType('ConfirmUserRequest', (_message.Message,), dict(
  DESCRIPTOR = _CONFIRMUSERREQUEST,
  __module__ = 'auth_user_pb2'
  # @@protoc_insertion_point(class_scope:grpc.testing.ConfirmUserRequest)
  ))
_sym_db.RegisterMessage(ConfirmUserRequest)

ConfirmUserReply = _reflection.GeneratedProtocolMessageType('ConfirmUserReply', (_message.Message,), dict(
  DESCRIPTOR = _CONFIRMUSERREPLY,
  __module__ = 'auth_user_pb2'
  # @@protoc_insertion_point(class_scope:grpc.testing.ConfirmUserReply)
  ))
_sym_db.RegisterMessage(ConfirmUserReply)


import abc
from grpc.early_adopter import implementations
from grpc.framework.alpha import utilities
class EarlyAdopterAuthenticationServicer(object):
  """<fill me in later!>"""
  __metaclass__ = abc.ABCMeta
  @abc.abstractmethod
  def AuthenticateUser(self, request, context):
    raise NotImplementedError()
  @abc.abstractmethod
  def ConfirmUser(self, request, context):
    raise NotImplementedError()
class EarlyAdopterAuthenticationServer(object):
  """<fill me in later!>"""
  __metaclass__ = abc.ABCMeta
  @abc.abstractmethod
  def start(self):
    raise NotImplementedError()
  @abc.abstractmethod
  def stop(self):
    raise NotImplementedError()
class EarlyAdopterAuthenticationStub(object):
  """<fill me in later!>"""
  __metaclass__ = abc.ABCMeta
  @abc.abstractmethod
  def AuthenticateUser(self, request):
    raise NotImplementedError()
  AuthenticateUser.async = None
  @abc.abstractmethod
  def ConfirmUser(self, request):
    raise NotImplementedError()
  ConfirmUser.async = None
def early_adopter_create_Authentication_server(servicer, port, private_key=None, certificate_chain=None):
  import auth_user_pb2
  import auth_user_pb2
  import auth_user_pb2
  import auth_user_pb2
  method_service_descriptions = {
    "AuthenticateUser": utilities.unary_unary_service_description(
      servicer.AuthenticateUser,
      auth_user_pb2.AuthenticateUserRequest.FromString,
      auth_user_pb2.AuthenticateUserReply.SerializeToString,
    ),
    "ConfirmUser": utilities.unary_unary_service_description(
      servicer.ConfirmUser,
      auth_user_pb2.ConfirmUserRequest.FromString,
      auth_user_pb2.ConfirmUserReply.SerializeToString,
    ),
  }
  return implementations.server("grpc.testing.Authentication", method_service_descriptions, port, private_key=private_key, certificate_chain=certificate_chain)
def early_adopter_create_Authentication_stub(host, port, metadata_transformer=None, secure=False, root_certificates=None, private_key=None, certificate_chain=None, server_host_override=None):
  import auth_user_pb2
  import auth_user_pb2
  import auth_user_pb2
  import auth_user_pb2
  method_invocation_descriptions = {
    "AuthenticateUser": utilities.unary_unary_invocation_description(
      auth_user_pb2.AuthenticateUserRequest.SerializeToString,
      auth_user_pb2.AuthenticateUserReply.FromString,
    ),
    "ConfirmUser": utilities.unary_unary_invocation_description(
      auth_user_pb2.ConfirmUserRequest.SerializeToString,
      auth_user_pb2.ConfirmUserReply.FromString,
    ),
  }
  return implementations.stub("grpc.testing.Authentication", method_invocation_descriptions, host, port, metadata_transformer=metadata_transformer, secure=secure, root_certificates=root_certificates, private_key=private_key, certificate_chain=certificate_chain, server_host_override=server_host_override)
# @@protoc_insertion_point(module_scope)
