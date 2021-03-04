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
[[ -n ${LIB_SB_CORE+defined} ]] && return; readonly LIB_SB_CORE=1

###################################################################
#  Includes and Definitions
###################################################################

# SituationBoard directories
readonly SBPATH=$SCRIPT_PATH
readonly SBSETUP=$SBPATH/misc/setup
readonly SBVENV=$SBPATH/venv
readonly SBBIN=$SBVENV/bin
readonly SBTEMP=$SBPATH/.temp

# SituationBoard files
readonly SBVERSION=$SBPATH/VERSION
readonly SBINSTALLED=$SBPATH/.installed
readonly SBSERVICE=situationboard.service
readonly SBPYTHON=$SBBIN/python
readonly SBPIP=$SBBIN/pip3
readonly SBBACKEND=$SBPATH/SituationBoard.py
readonly SBDATABASE=$SBPATH/situationboard.sqlite
readonly SBCONFIG=$SBPATH/situationboard.conf
readonly SBLOG=$SBPATH/situationboard.log

# SituationBoard variables
readonly SBDEFAULTPORT=5000
readonly SBRELEASEBRANCH=main

# Dummy source events (and their signals)
readonly DUMMY_ALARM=14   # SIGALRM
readonly DUMMY_BINARY=10  # SIGUSR1
readonly DUMMY_SETTING=12 # SIGUSR2

# Available features
readonly F_BASE="base"
readonly F_GPIO="gpio"
readonly F_SMS="sms"
readonly F_AUTOSTART="autostart"
readonly F_TEST="test"

# Special ALL feature (uppercase!)
readonly F_ALL="ALL"

# List of all available features
readonly ALL_FEATURES="$F_BASE $F_GPIO $F_SMS $F_AUTOSTART $F_TEST"

###################################################################
#  Functions
###################################################################

core_is_installed() {
  if [[ ! -f "$SBINSTALLED" ]]; then
    return 1 # FALSE
  fi

  if [[ $# -gt 0 ]]; then
    for FEATURE in "$@"; do
      if ! grep -q -x "$FEATURE" "$SBINSTALLED"; then
        return 1 # FALSE
      fi
    done
  fi

  return 0 # TRUE
}

core_runf() {
  "$SBPYTHON" -u "$SBBACKEND" "$@"
  return $?
}

core_runb() {
  "$SBPYTHON" -u "$SBBACKEND" "$@" &
  return 0
}

core_kill() {
  killall "$SBPYTHON" 2> /dev/null
  wait 2> /dev/null
  return $?
}

core_dummy_signal() {
  local SIGNAL=$1
  # send signal to generate dummy source event
  if ! killall -s "$SIGNAL" "$SBPYTHON" 2> /dev/null; then
    echo_error "The SituationBoard backend is not running."
    return 1
  fi
  return 0
}

core_get_version() {
  local -n VERSION_REF_=$1
  local VERSION_ RESULT_

  if [[ -f "$SBVERSION" ]]; then
    # shellcheck disable=SC2002
    VERSION_=$(cat "$SBVERSION" 2>/dev/null | tr -d "\n\t "); RESULT_=$?
    if [[ $RESULT_ -eq 0 && "$VERSION_" != "" ]]; then
      VERSION_REF_=$VERSION_
      return 0;
    fi
  fi

  VERSION_REF_="0.0"
  return 1
}

core_get_git_info() {
  local -n INFO_REF_=$1
  local GIT_BRANCH_ GIT_HASH_
  GIT_BRANCH_="$(git -C "$SBPATH" symbolic-ref --short HEAD 2>/dev/null)"
  GIT_HASH_="$(git -C "$SBPATH" describe --always --dirty=+ 2>/dev/null)"
  INFO_REF_="$GIT_BRANCH_ $GIT_HASH_"
  return 0
}

core_service_operation() {
  local OPERATION=$1
  if [[ "$OPERATION" == "status" ]]; then
    systemctl status --all "$SBSERVICE"
    return $?
  else
    sudo systemctl "$OPERATION" "$SBSERVICE"
    return $?
  fi
}

core_service_is_active() {
  systemctl --quiet is-active "$SBSERVICE"
  return $?
}

core_service_suspend() {
  if core_is_installed "$F_AUTOSTART"; then
    core_service_is_active
    local WAS_ACTIVE=$?

    if [[ $WAS_ACTIVE -eq 0 ]]; then
      core_service_operation stop
    fi

    return $WAS_ACTIVE
  else
    return 1
  fi
}

core_service_resume() {
  if core_is_installed "$F_AUTOSTART"; then
    local WAS_ACTIVE=$1
    if [[ $WAS_ACTIVE -eq 0 ]]; then
      core_service_operation start
    fi
  fi
}

core_export() {
  local CSV_FILE=$1

  core_service_suspend; local SERVICE_WAS_ACTIVE=$?

  echo_bold "Exporting CSV data..."
  core_runf -e "$CSV_FILE"
  local RESULT=$?

  core_service_resume $SERVICE_WAS_ACTIVE

  return $RESULT
}

core_get_port() {
  local -n PORT_REF_=$1
  get_setting "$SBCONFIG" "backend" "server_port" "$SBDEFAULTPORT" PORT_REF_
  return $?
}

core_require_installed() {
  if ! core_is_installed; then
    echo_error "SituationBoard is not installed."
    echo_error "Run \"sbctl install\" to perform the installation."
    exit 1
  fi

  if ! core_is_installed "$@"; then
    echo_error "This command requires features that are not installed!"
    echo_error "The following features are required: $*"
    echo_error "Run \"sbctl install\" to perform the installation of these features."
    exit 1
  fi

  return 0
}
