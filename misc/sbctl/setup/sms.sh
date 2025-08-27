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
[[ -n ${LIB_SB_SETUP_SMS+defined} ]] && return; readonly LIB_SB_SETUP_SMS=1

###################################################################
#  Includes and Definitions
###################################################################

readonly UDEV_FILE=50-situationboard-udev.rules
readonly UDEV_SRC_FILE=$SBSETUP/$UDEV_FILE
readonly UDEV_DST_FILE=/etc/udev/rules.d/$UDEV_FILE

readonly MODESWITCH_FILE=12d1:1f01
readonly MODESWITCH_SRC_FILE=$SBSETUP/$MODESWITCH_FILE
readonly MODESWITCH_DST_FILE=/usr/share/usb_modeswitch/$MODESWITCH_FILE

readonly GAMMU_SRC_FILE=$SBSETUP/gammu-smsdrc
readonly GAMMU_DST_FILE=/etc/gammu-smsdrc

readonly SMS_DEFAULT_DEVICE=/dev/ttyUSB0
readonly SMS_DEFAULT_CONNECTION=at

# The following configuration parameters may be passed as
# environment variables for automatic installations:

# Modem settings used for GAMMU SMSD
SMS_DEVICE=${SMS_DEVICE:-$SMS_DEFAULT_DEVICE}
SMS_CONNECTION=${SMS_CONNECTION:-$SMS_DEFAULT_CONNECTION}

# PIN used for GAMMU SMSD (if required)
SMS_PIN=${SMS_PIN:-}

###################################################################
#  Functions
###################################################################

setup_ask_sms() {
  local FEATURE=$1

  if ask_yes_no "Install SMS support (requires a modem)?" $ASK_DEFAULT_NO; then
    setup_request_feature "$FEATURE"

    ask_text "Enter the modem device" $ASK_INPUT_COMPLETE "$SMS_DEFAULT_DEVICE" SMS_DEVICE
    if [[ ! "$SMS_DEVICE" =~ ^/dev/[^/]+$ || ( "$SMS_DEVICE" != "$SMS_DEFAULT_DEVICE" && ! -c "$SMS_DEVICE" ) ]]; then
      echo_error "Invalid device specified!"
      exit 1
    fi

    ask_text "Enter the modem connection" $ASK_INPUT_REGULAR "$SMS_DEFAULT_CONNECTION" SMS_CONNECTION

    ask_text "Enter your PIN (if required)" $ASK_INPUT_HIDDEN "" SMS_PIN # default: "" (none)
  fi
}

setup_install_sms() {
  setup_print_step "Install GAMMU"
  apt-get install --yes gammu libgammu-dev > /dev/null
  check_result_done $?

  setup_print_step "Install GAMMU config"
  if [[ ! -f "$GAMMU_DST_FILE" ]]; then
    if [ "$SMS_PIN" == "" ]; then
      sed -e "s,__SBDEVICE_LINE__,device = ${SMS_DEVICE},g" \
          -e "s,__SBCONNECTION_LINE__,connection = ${SMS_CONNECTION},g" \
          -e "s,__SBPIN_LINE__,#pin = <PIN>,g" \
          "$GAMMU_SRC_FILE" | tee "$GAMMU_DST_FILE" > /dev/null
      check_result_done $?
    else
      sed -e "s,__SBDEVICE_LINE__,device = ${SMS_DEVICE},g" \
          -e "s,__SBCONNECTION_LINE__,connection = ${SMS_CONNECTION},g" \
          -e "s,__SBPIN_LINE__,pin = ${SMS_PIN},g" \
          "$GAMMU_SRC_FILE" | tee "$GAMMU_DST_FILE" > /dev/null
      check_result_done $?
    fi
  else
    echo_ok "Already existed."
  fi

  setup_print_step "Install UDEV rules"
  local SBDEVICE="${SMS_DEVICE##/dev/}"
  sed -e "s,__SBDEVICE__,${SBDEVICE},g" \
      -e "s,__SBSERVICE__,${SBSERVICE},g" \
      "$UDEV_SRC_FILE" | tee "$UDEV_DST_FILE" > /dev/null
  check_result_done $?

  setup_print_step "Setup USB modeswitch (workaround for some E303 modems)"
  apt-get install --yes usb-modeswitch usb-modeswitch-data > /dev/null
  check_result $?
  install -m 644 "$MODESWITCH_SRC_FILE" "$MODESWITCH_DST_FILE"
  check_result_done $?

  setup_print_step "Install Python dependencies"
  sudo -u "$SBUSER" "$SBPIP" install --quiet python-gammu
  check_result_done $?

  return 0
}

setup_remove_sms() {
  # load and preserve settings for potential reinstall
  if [[ -f "$GAMMU_DST_FILE" ]]; then
    get_setting "$GAMMU_DST_FILE" "gammu" "device" "$SMS_DEFAULT_DEVICE" SMS_DEVICE
    get_setting "$GAMMU_DST_FILE" "gammu" "connection" "$SMS_DEFAULT_CONNECTION" SMS_CONNECTION
    get_setting "$GAMMU_DST_FILE" "smsd" "pin" "" SMS_PIN
    #echo "SMS_DEVICE: $SMS_DEVICE"
    #echo "SMS_CONNECTION: $SMS_CONNECTION"
    #echo "SMS_PIN: $SMS_PIN"
  fi

  setup_print_step "Remove GAMMU config file"
  rm -f "$GAMMU_DST_FILE"
  check_result_done $?

  setup_print_step "Remove UDEV rules"
  rm -f "$UDEV_DST_FILE"
  check_result_done $?

  setup_print_step "Remove USB modeswitch file"
  rm -f "$MODESWITCH_DST_FILE"
  check_result_done $?

  return 0
}
