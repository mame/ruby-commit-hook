#!/usr/bin/env ruby
require 'cgi'
require 'json'
require 'logger'
require 'openssl'

class Webhook
  LOG_PATH = '/tmp/webhook.log'

  def initialize(payload:, signature:, secret:)
    @payload = payload
    @signature = signature
    @secret = secret
  end

  def process
    unless authorized_webhook?
      logger.info('Request was not an authorized webhook')
      return false
    end

    logger.info('Authorization success!')
    return true
  rescue => e
    logger.info("#{e.class}: #{e.message}")
    logger.info(e.backtrace.join("\n"))
    return false
  end

  private

  # See:
  # https://developer.github.com/webhooks/
  # https://developer.github.com/webhooks/securing/
  def authorized_webhook?
    return false if @payload.nil? || @signature.nil? || @secret.nil?

    signature = "sha1=#{OpenSSL::HMAC.hexdigest(OpenSSL::Digest.new('sha1'), @secret, @payload)}"
    Rack::Utils.secure_compare(@signature, signature)
  end

  def logger
    @logger ||= Logger.new(LOG_PATH)
  end
end

# The following `Rack::Util.secure_compare` is copied from:
# https://github.com/rack/rack/blob/2.0.7/lib/rack/utils.rb
=begin
The MIT License (MIT)

Copyright (C) 2007-2019 Leah Neukirchen <http://leahneukirchen.org/infopage.html>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
=end
module Rack
  module Utils
    # Constant time string comparison.
    #
    # NOTE: the values compared should be of fixed length, such as strings
    # that have already been processed by HMAC. This should not be used
    # on variable length plaintext strings because it could leak length info
    # via timing attacks.
    def secure_compare(a, b)
      return false unless a.bytesize == b.bytesize

      l = a.unpack("C*")

      r, i = 0, -1
      b.each_byte { |v| r |= v ^ l[i+=1] }
      r == 0
    end
    module_function :secure_compare
  end
end

webhook = Webhook.new(
  payload: STDIN.read, # must be done before CGI.new
  signature: ENV['HTTP_X_HUB_SIGNATURE'],
  secret: File.read(File.expand_path('~git/config/ruby-commit-hook-secret')).chomp,
)
print CGI.new.header
print "#{webhook.process}\r\n"