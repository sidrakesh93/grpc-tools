# -*- ruby -*-
# encoding: utf-8

Pod::Spec.new do |s|
  s.name     = 'packager-unittest-v2'
  s.version  = '1.0.0'

  s.authors  = { 'Google Inc' => 'googleapis-packages@google.com' }
  s.ios.deployment_target = '6.0'
  s.osx.deployment_target = '10.8'
  s.license  = 'Apache'
  s.source   = {
    :git => 'https://github.com/google/packager-unittest',
    :tag => "#{s.version}"
  }
  s.summary  = 'a unittest api'

  # The --objc_out plugin generates a pair of .pbobjc.h/.pbobjc.m files for each .proto file.
  s.subspec "Messages" do |ms|
    ms.source_files = "*.pbobjc.{h,m}", "**/*.pbobjc.{h,m}"
    ms.header_mappings_dir = "."
    ms.requires_arc = false
    ms.dependency "Protobuf", "~> 3.0.0-alpha-3"
  end

  # The --objcgrpc_out plugin generates a pair of .pbrpc.h/.pbrpc.m files for each .proto file with
  # a service defined.
  s.subspec "Services" do |ss|
    ss.source_files = "*.pbrpc.{h,m}", "**/*.pbrpc.{h,m}"
    ss.header_mappings_dir = "."
    ss.requires_arc = true
    ss.dependency "gRPC", "~> 0.5.0"
    ss.dependency "#{s.name}/Messages"
  end
end
