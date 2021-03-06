#!/bin/bash -eu
set -o pipefail
# This script is executed by `git@git.ruby-lang.org:ruby-commit-hook.git/hooks/pre-receive`.

# script parameters
ruby_git="/var/git/ruby.git"
hook_log="/tmp/pre-receive-pre.log"
ruby_commit_hook="$(cd "$(dirname $0)"; cd ..; pwd)"

$ruby_commit_hook/bin/check-email.rb $SVN_ACCOUNT_NAME $GIT_COMMITTER_EMAIL $* || exit 1
