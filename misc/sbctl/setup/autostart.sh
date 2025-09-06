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
[[ -n ${LIB_SB_SETUP_AUTOSTART+defined} ]] && return; readonly LIB_SB_SETUP_AUTOSTART=1

###################################################################
#  Includes and Definitions
###################################################################

readonly SERVICE_SRC_FILE=$SBSETUP/$SBSERVICE
readonly SERVICE_DST_FILE=/etc/systemd/system/$SBSERVICE

readonly FRONTEND_FILE=SituationBoardFrontend.desktop
readonly FRONTEND_SRC_FILE=$SBSETUP/$FRONTEND_FILE
readonly FRONTEND_DST_FOLDER=$SBHOME/.config/autostart
readonly FRONTEND_DST_FILE=$FRONTEND_DST_FOLDER/$FRONTEND_FILE

###################################################################
#  Functions
###################################################################

setup_ask_autostart() {
  local FEATURE=$1
  if ask_yes_no "Install autostart support (service and frontend)?" $ASK_DEFAULT_YES; then
    setup_request_feature "$FEATURE"
  fi
}

setup_install_autostart() {
  setup_print_step "Install CEC utils"
  apt-get install --yes cec-utils > /dev/null
  check_result_done $?

  setup_print_step "Install SituationBoard systemd service"
  if pidof systemd > /dev/null; then
    # system is using systemd
    if setup_is_requested_feature "$F_SMS"; then
      local SBDEVICE="dev-${SMS_DEVICE##/dev/}.device"
      sed -e "s,__SBPATH__,${SBPATH},g" \
          -e "s,__SBUSER__,${SBUSER},g" \
          -e "s,__SBDEVICE__,${SBDEVICE},g" \
          "$SERVICE_SRC_FILE" | tee "$SERVICE_DST_FILE" > /dev/null
      check_result $?
    else
      sed -e "s,__SBPATH__,${SBPATH},g" \
          -e "s,__SBUSER__,${SBUSER},g" \
          -e "s,__SBDEVICE__,,g" \
          "$SERVICE_SRC_FILE" | tee "$SERVICE_DST_FILE" > /dev/null
      check_result $?
    fi
    systemctl daemon-reload
    check_result_done $?
  else
    # system is not using systemd (e.g. docker / CI environment)
    echo_ok "Omitted."
  fi

  setup_print_step "Setup frontend autostart for current user" # autostart unclutter + chromium
  install -o "$SBUSER" -g "$SBUSER" -m 755 -d "$FRONTEND_DST_FOLDER"
  check_result $?
  install -o "$SBUSER" -g "$SBUSER" -m 644 "$FRONTEND_SRC_FILE" "$FRONTEND_DST_FILE"
  check_result_done $?

  return 0
}

setup_remove_autostart() {
  setup_print_step "Remove SituationBoard systemd service"
  if pidof systemd > /dev/null; then
    # system is using systemd
    systemctl stop "$SBSERVICE"
    check_result $?
    systemctl --quiet disable "$SBSERVICE"
    check_result $?
    rm -f "$SERVICE_DST_FILE"
    check_result $?
    systemctl daemon-reload
    check_result_done $?
  else
    # system is not using systemd (e.g. docker / CI environment)
    echo_ok "Omitted."
  fi

  setup_print_step "Remove frontend autostart"
  rm -f "$FRONTEND_DST_FILE"
  check_result_done $?

  return 0
}
