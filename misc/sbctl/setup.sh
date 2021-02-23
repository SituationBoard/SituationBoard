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
[[ -n ${LIB_SB_SETUP+defined} ]] && return; readonly LIB_SB_SETUP=1

###################################################################
#  Includes and Definitions
###################################################################

# SituationBoard environment
readonly SBUSER=$(stat -c '%U' "$SCRIPT_FILENAME")
readonly SBHOME=$(getent passwd "$SBUSER" | cut -d: -f6)

# Requested features
FEATURES=""

###################################################################
#  Include Features
###################################################################
# shellcheck source=misc/sbctl/setup/base.sh
source "$SCRIPT_PATH/misc/sbctl/setup/base.sh"
# shellcheck source=misc/sbctl/setup/gpio.sh
source "$SCRIPT_PATH/misc/sbctl/setup/gpio.sh"
# shellcheck source=misc/sbctl/setup/sms.sh
source "$SCRIPT_PATH/misc/sbctl/setup/sms.sh"
# shellcheck source=misc/sbctl/setup/autostart.sh
source "$SCRIPT_PATH/misc/sbctl/setup/autostart.sh"
# shellcheck source=misc/sbctl/setup/test.sh
source "$SCRIPT_PATH/misc/sbctl/setup/test.sh"

###################################################################
#  Helper Functions
###################################################################

setup_is_valid_feature() {
  local FEATURE=$1
  if echo "$ALL_FEATURES" | grep -q -w "$FEATURE"; then
    return 0 # TRUE
  fi
  return 1 # FALSE
}

setup_is_requested_feature() {
  local FEATURE=$1
  if echo "$FEATURES" | grep -q -w "$FEATURE"; then
    return 0 # TRUE
  fi
  return 1 # FALSE
}

setup_request_feature() {
  local FEATURE=""
  local RESULT=0
  for FEATURE in "$@"; do
    if setup_is_valid_feature "$FEATURE"; then
      if [[ "$FEATURES" == "" ]]; then
        FEATURES=$FEATURE
      elif ! setup_is_requested_feature "$FEATURE"; then
        FEATURES="$FEATURES $FEATURE"
      fi
    else
      RESULT=1
    fi
  done
  return $RESULT
}

setup_load_installed_features() {
  FEATURES=""
  if core_is_installed; then
    FEATURES=$(tr '\n' ' ' < "$SBINSTALLED")
  fi
}

setup_register_installed_feature() {
  local FEATURE=$1
  if ! core_is_installed "$FEATURE"; then
    echo "$FEATURE" >> "$SBINSTALLED"
  fi
}

setup_print_header() {
  if [[ $# -eq 0 ]]; then
    echo_bold "=== SituationBoard Setup ==="
  else
    local HEADER=$1
    echo_bold "=== $1 ==="
  fi
}

setup_print_info() {
  local INFO=$1
  echo "$INFO"
}

setup_print_features() {
  echo -e "Selected Features: ${OUTPUT_BOLD}$FEATURES${OUTPUT_RESET}"
}

setup_print_step() {
  local TEXT=$1
  printf "%s... " "$TEXT"
}

setup_require_installed() {
  if ! core_is_installed; then
    echo_error "No existing installation found."
    exit 1
  fi
}

setup_require_not_installed() {
  if core_is_installed; then
    echo_error "SituationBoard is already installed."
    exit 1
  fi
}

setup_install_if_requested() {
  local FEATURE=$1
  local FUNCTION=$2
  if setup_is_requested_feature "$FEATURE"; then
    setup_print_header "Install ${FEATURE^^} feature"
    $FUNCTION
    setup_register_installed_feature "$FEATURE"
  fi
}

setup_remove_if_installed() {
  local FEATURE=$1
  local FUNCTION=$2
  if core_is_installed "$FEATURE"; then
    #setup_print_header "Removing $FEATURE feature"
    $FUNCTION
  fi
}

###################################################################
#  Actual Setup Functions
###################################################################

setup_perform_uninstall() {
  setup_print_header "Remove existing installation"

  # remove all installed features
  setup_remove_if_installed $F_GPIO setup_remove_gpio
  setup_remove_if_installed $F_SMS setup_remove_sms
  setup_remove_if_installed $F_AUTOSTART setup_remove_autostart
  setup_remove_if_installed $F_TEST setup_remove_test

  setup_remove_base
  rm -f "$SBINSTALLED"
}

setup_perform_install() {
  setup_print_header "Base installation"
  setup_install_base
  touch "$SBINSTALLED"
  setup_register_installed_feature $F_BASE

  # install all requested features
  setup_install_if_requested $F_GPIO setup_install_gpio
  setup_install_if_requested $F_SMS setup_install_sms
  setup_install_if_requested $F_AUTOSTART setup_install_autostart
  setup_install_if_requested $F_TEST setup_install_test
}

setup_print_next_steps() {
  local PORT
  core_get_port PORT

  echo ""
  echo "Next Steps:"
  echo ""
  echo " 1. Adjust settings by editing the file \"situationboard.conf\""
  echo " 2. Test your configuration by running the server with \"sbctl run\"."
  echo "    The frontend should now be available under: http://localhost:$PORT"
  echo "    You can kill the running server with \"sbctl kill\"."
  if setup_is_requested_feature $F_AUTOSTART; then
  echo " 3. Once your configuration is correct and your tests successful,"
  echo "    enable the service permanently with \"sbctl enable\""
  echo "    and start it with \"sbctl start\""
  fi
  echo ""
  echo "See \"README.md\" and \"docs/Configuration.md\" for more details."
  echo ""
}

###################################################################
#  Exported Setup Operations (for sbctl)
###################################################################

setup_install() {
  setup_print_header
  setup_print_info "Performing interactive installation"
  setup_require_not_installed
  setup_request_feature $F_BASE

  setup_ask_base $F_BASE
  setup_ask_gpio $F_GPIO
  setup_ask_sms $F_SMS
  setup_ask_autostart $F_AUTOSTART
  setup_ask_test $F_TEST

  setup_print_features
  if ! ask_yes_no "Is your selection correct?"; then # continue installation ?
    echo_error "Canceled installation."
    exit 1
  fi

  if core_is_installed; then
    setup_perform_uninstall
    setup_perform_install
    setup_print_header "Reinstallation successful"
  else
    setup_perform_install
    setup_print_header "Installation successful"
  fi

  setup_print_next_steps
  return 0
}

setup_ainstall() {
  setup_print_header
  setup_print_info "Performing automatic installation"
  setup_require_not_installed
  setup_request_feature $F_BASE

  if [[ $# -gt 0 ]]; then
    for FEATURE in "$@"; do
      if [[ "${FEATURE^^}" == "${F_ALL^^}" ]]; then
        FEATURES=$ALL_FEATURES
      elif ! setup_request_feature "$FEATURE"; then
        #echo_error "Invalid feature: $FEATURE\n"
        #print_usage; exit 1
        echo_error "Invalid feature: $FEATURE"
        echo_error "Available features: $ALL_FEATURES"
        exit 1
      fi
    done
  fi

  setup_print_features
  setup_perform_install
  setup_print_header "Installation successful"
  return 0
}

setup_reinstall() {
  setup_print_header
  setup_print_info "Performing reinstallation (of existing installation)"
  setup_require_installed
  setup_load_installed_features
  setup_print_features
  setup_perform_uninstall
  setup_perform_install
  setup_print_header "Reinstallation successful"
  return 0
}

setup_uninstall() {
  setup_print_header
  setup_print_info "Performing auto uninstall (remove existing installation)"
  setup_require_installed
  setup_perform_uninstall
  setup_print_header "Uninstallation successful"
  return 0
}
