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
[[ -n ${LIB_SB_SETUP_GPIO+defined} ]] && return; readonly LIB_SB_SETUP_GPIO=1

###################################################################
#  Includes and Definitions
###################################################################

# none

###################################################################
#  Functions
###################################################################

setup_ask_gpio() {
  local FEATURE=$1
  is_raspbian; IS_RASPBERRY_PI=$?
  if ask_yes_no "Install GPIO support (requires Raspberry Pi)?" $IS_RASPBERRY_PI; then # default: $IS_RASPBERRY_PI
    setup_request_feature "$FEATURE"
  fi
}

setup_install_gpio() {
  setup_print_step "Install Python dependencies"
  sudo -u "$SBUSER" "$SBPIP" install --quiet RPi.GPIO
  check_result_done $?

  return 0
}

setup_remove_gpio() {
  # nothing to do here...
  return 0
}
