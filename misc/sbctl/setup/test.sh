#!/usr/bin/env bash

# SituationBoard - Alarm Display for Fire Departments
# Copyright (C) 2017-2021 Sebastian Maier
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

###################################################################
#  Direct Execution Detection and Include Guard
###################################################################

# Detect if this script was called directly (instead of being sourced)
[[ "${BASH_SOURCE[0]}" == "${0}" ]] && { echo "This script is part of sbctl." >>/dev/stderr; exit 1; }

# Include guard
[[ -n ${LIB_SB_SETUP_TEST+defined} ]] && return; readonly LIB_SB_SETUP_TEST=1

###################################################################
#  Includes and Definitions
###################################################################

# none

###################################################################
#  Functions
###################################################################

setup_ask_test() {
  local FEATURE=$1
  if ask_yes_no "Install test support (for development)?" $ASK_DEFAULT_YES; then # 1 -> default: false
    setup_request_feature "$FEATURE"
  fi
}

setup_install_test() {
  setup_print_step "Install test tools"
  apt-get install --yes tidy shellcheck > /dev/null
  check_result_done $?

  setup_print_step "Install Python dependencies"
  sudo -u "$SBUSER" "$SBPIP" install --quiet -r "$SBSETUP/dev-requirements.txt"
  check_result_done $?

  setup_print_step "Install JavaScript dependencies"
  sudo -u "$SBUSER" npm install --silent --no-progress --only=development --prefix "$SBPATH/frontend/" > /dev/null
  check_result_done $?

  return 0
}

setup_remove_test() {
  setup_print_step "Remove temporary test folders"
  rm -rf "$SBPATH/.mypy_cache" "$SBPATH/.pytest_cache"
  check_result_done $?

  return 0
}
