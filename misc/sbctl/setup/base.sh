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
[[ -n ${LIB_SB_SETUP_BASE+defined} ]] && return; readonly LIB_SB_SETUP_BASE=1

###################################################################
#  Includes and Definitions
###################################################################

readonly SBNMOD=$SBPATH/frontend/node_modules
readonly SBNPLJ=$SBPATH/frontend/package-lock.json

readonly SBCTL_FILE=$SBPATH/sbctl
readonly SBCTL_BIN_SYMLINK_FILE=/usr/bin/sbctl
readonly SBCTL_BC_SYMLINK_FILE=/usr/share/bash-completion/completions/sbctl

readonly SBCONF_SRC_FILE=$SBSETUP/situationboard_default.conf
readonly SBCONF_DST_FILE=$SBCONFIG

readonly SBMANPAGE_FILE=$SBSETUP/sbctl.1
readonly SBMANPAGE_MAN1_PATH=/usr/local/share/man/man1
readonly SBMANPAGE_SYMLINK_FILE=$SBMANPAGE_MAN1_PATH/sbctl.1

###################################################################
#  Functions
###################################################################

setup_ask_base() {
  local FEATURE=$1
  setup_request_feature "$FEATURE"
}

setup_install_base() {
  setup_print_step "Upgrade all packages"
  if [[ $CI_ACTIVE -eq 0 ]]; then
    apt-get update --yes > /dev/null
    #check_result $?
    apt-get upgrade --yes > /dev/null
    check_result_done $?
  else
    apt-get update --yes > /dev/null
    #check_result $?
    echo_ok "Omitted."
  fi

  setup_print_step "Install Python and JavaScript tools"
  apt-get install --yes python3-dev python3-pip python3-venv npm fonts-noto-color-emoji > /dev/null
  check_result_done $?

  setup_print_step "Install sbctl tool"
  ln -sf "$SBCTL_FILE" "$SBCTL_BIN_SYMLINK_FILE"
  check_result $?
  ln -sf "$SBCTL_FILE" "$SBCTL_BC_SYMLINK_FILE"
  check_result_done $?

  setup_print_step "Install sbctl man page"
  if hash mandb > /dev/null 2>&1; then
    install -m 775 -d "$SBMANPAGE_MAN1_PATH"
    check_result $?
    ln -sf "$SBMANPAGE_FILE" "$SBMANPAGE_SYMLINK_FILE"
    check_result $?
    sudo mandb --quiet
    check_result_done $?
  else
    echo_ok "Omitted."
  fi

  setup_print_step "Setup Python environment"
  sudo -u "$SBUSER" python3 -m venv "$SBVENV"
  check_result $?
  sudo -u "$SBUSER" "$SBPIP" install --quiet --upgrade pip setuptools wheel
  check_result_done $?

  setup_print_step "Install Python dependencies"
  sudo -u "$SBUSER" "$SBPIP" install --quiet -r "$SBSETUP/requirements.txt"
  check_result_done $?

  setup_print_step "Install JavaScript dependencies"
  sudo -u "$SBUSER" npm install --silent --no-progress --only=production --prefix "$SBPATH/frontend/" > /dev/null
  check_result_done $?

  setup_print_step "Install SituationBoard default config"
  if [[ ! -f "$SBCONF_DST_FILE" ]]; then # do not overwrite an existing config
    install -o "$SBUSER" -g "$SBUSER" -m 644 "$SBCONF_SRC_FILE" "$SBCONF_DST_FILE"
    check_result_done $?
  else
    echo_ok "Already existed."
  fi

  return 0
}

setup_remove_base() {
  setup_print_step "Remove sbctl tool"
  rm -f "$SBCTL_BIN_SYMLINK_FILE"
  check_result $?
  rm -f "$SBCTL_BC_SYMLINK_FILE"
  check_result_done $?

  setup_print_step "Remove sbctl man page"
  if hash mandb > /dev/null 2>&1; then
    rm -f "$SBMANPAGE_SYMLINK_FILE"
    check_result $?
    sudo mandb --quiet
    check_result_done $?
  else
    echo_ok "Not existing."
  fi

  setup_print_step "Remove Python environment and packages"
  rm -rf "$SBVENV"
  check_result_done $?

  setup_print_step "Remove JavaScript packages"
  rm -rf "$SBNMOD" "$SBNPLJ"
  check_result_done $?

  setup_print_step "Remove temporary folder"
  rm -rf "$SBTEMP"
  check_result_done $?

  return 0
}
