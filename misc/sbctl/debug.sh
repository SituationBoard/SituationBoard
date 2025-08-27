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
[[ -n ${LIB_SB_DEBUG+defined} ]] && return; readonly LIB_SB_DEBUG=1

###################################################################
#  Includes and Definitions
###################################################################

# Available tests
readonly T_PYLINT="pylint"
readonly T_MYPY="mypy"
readonly T_TIDY="tidy"
readonly T_ESLINT="eslint"
readonly T_SHELLCHECK="shellcheck"
readonly T_PYTEST="pytest"
readonly T_RUNTEST="runtest"

# Special ALL test (uppercase!)
readonly T_ALL="ALL"

# List of all available tests
readonly ALL_TESTS="$T_PYLINT $T_MYPY $T_TIDY $T_ESLINT $T_SHELLCHECK $T_PYTEST $T_RUNTEST"

###################################################################
#  Functions
###################################################################

debug_runf() {
  ("$SBPYTHON" -u "$SBBACKEND" "$@" 2>&1) | tee --ignore-interrupts "$SBLOG"
  return $?
}

debug_runb() {
  ("$SBPYTHON" -u "$SBBACKEND" "$@" 2>&1) | tee --ignore-interrupts "$SBLOG" &
  return 0
}

debug_kill() {
  core_kill
  return $?
}

debug_dummy_signal() {
  core_dummy_signal "$1"
  return $?
}

debug_frontend() {
  local MODE=$1 # "fullscreen" or "regular"
  local AUTOSTART_LOG=/tmp/situationboard_autostart.log

  if [[ "$MODE" == "fullscreen" ]]; then
    #sleep 5
    date > "$AUTOSTART_LOG"
    if ! core_service_is_active; then
      echo "SB backend is not running" >> "$AUTOSTART_LOG"
      echo_error "SituationBoard service is not running!"
      return 1
    fi
    echo "SB backend is running" >> "$AUTOSTART_LOG"
  fi

  local PORT
  core_get_port PORT
  local URL="http://localhost:$PORT"
  export DISPLAY="${DISPLAY:=:0}"
  if hash chromium-browser > /dev/null 2>&1; then
    if [[ "$MODE" == "fullscreen" ]]; then
      echo "Starting Chromium" >> "$AUTOSTART_LOG"
      xset s 0 # disable screen sleep (blank time)
      xset dpms 0 0 0 # disable screen sleep (dpms)
      unclutter > /dev/null 2>&1 & # hide cursor
      #chromium-browser --disable-features=TranslateUI --noerrdialogs --kiosk --incognito "$URL" > /dev/null 2>&1 &
      chromium-browser --disable-features=TranslateUI --noerrdialogs --start-fullscreen --incognito "$URL" > /dev/null 2>&1 &
    else
      chromium-browser --disable-features=TranslateUI "$URL" > /dev/null 2>&1 &
    fi
    return 0
  elif hash google-chrome > /dev/null 2>&1; then
    if [[ "$MODE" == "fullscreen" ]]; then
      echo "Starting Google Chrome" >> "$AUTOSTART_LOG"
      xset s 0 # disable screen sleep (blank time)
      xset dpms 0 0 0 # disable screen sleep (dpms)
      unclutter > /dev/null 2>&1 & # hide cursor
      #google-chrome --disable-features=TranslateUI --noerrdialogs --kiosk --incognito "$URL" > /dev/null 2>&1 &
      google-chrome --disable-features=TranslateUI --noerrdialogs --start-fullscreen --incognito "$URL" > /dev/null 2>&1 &
    else
      google-chrome --disable-features=TranslateUI "$URL" > /dev/null 2>&1 &
    fi
    return 0
  elif hash firefox > /dev/null 2>&1; then
    if [[ "$MODE" == "fullscreen" ]]; then
      echo "Starting Firefox" >> "$AUTOSTART_LOG"
      xset s 0 # disable screen sleep (blank time)
      xset dpms 0 0 0 # disable screen sleep (dpms)
      unclutter > /dev/null 2>&1 & # hide cursor
      firefox --kiosk "$URL" > /dev/null 2>&1 &
    else
      firefox "$URL" > /dev/null 2>&1 &
    fi
    return 0
  else
    if [[ "$MODE" == "fullscreen" ]]; then
      echo "No browser found!" >> "$AUTOSTART_LOG"
    fi
    echo_error "No browser found!"
    return 1
  fi
}

debug_test_pylint() {
  echo_bold "Validating Python code with pylint..."
  rm -rf "$SBTEMP" && mkdir -p "$SBTEMP"
  "$SBBIN/pylint" "--rcfile=$SBPATH/test/pylintrc" \
                  "$SBBACKEND" "$SBPATH/backend" "$SBPATH/test"
  check_result_done $?
}

debug_test_mypy() {
  echo_bold "Validating Python code with mypy..."
  rm -rf "$SBTEMP" && mkdir -p "$SBTEMP"
  "$SBBIN/mypy" "--config-file=$SBPATH/test/mypy.conf" "--cache-dir=$SBPATH/.mypy_cache" --strict \
                "$SBBACKEND" "$SBPATH/backend" "$SBPATH/test"
  check_result_done $?
}

debug_test_tidy() {
  echo_bold "Validating HTML with tidy..."
  rm -rf "$SBTEMP" && mkdir -p "$SBTEMP"
  tidy -errors "$SBPATH/frontend/index.html"
  check_result_done $?
}

debug_test_eslint() {
  echo_bold "Validating JavaScript with eslint..."
  npm run eslint --prefix="$SBPATH/frontend"
  check_result_done $?
}

debug_test_shellcheck() {
  echo_bold "Validating sbctl with shellcheck..."
  shellcheck --external-sources --check-sourced --source-path "$SBPATH" "$SBPATH/sbctl"
  check_result_done $?
}

debug_test_pytest() {
  echo_bold "Running Python unit tests..."
  rm -rf "$SBTEMP" && mkdir -p "$SBTEMP"
  (
  cd "$SBPATH" || exit 1
  "$SBBIN/pytest" "--cov-config=$SBPATH/test/coverage.conf" "--rootdir=$SBPATH" "--cov=$SBPATH" \
                  "$SBBACKEND" "$SBPATH/backend" "$SBPATH/test"
  )
  check_result_done $?
}

debug_test_runtest() {
  echo_bold "Running alarm test..."
  rm -rf "$SBTEMP" && mkdir -p "$SBTEMP"
  local SBTESTCONF="$SBTEMP/situationboard.conf"
  local SBTESTDB="$SBTEMP/situationboard.sqlite"
  local SBTESTFILE="$SBTEMP/alarm.txt"
  cp "$SBSETUP/situationboard_default.conf" "$SBTESTCONF"
  check_result $?
  sed -i -e 's/source =.*/source = dummy/g' \
         -e 's/actions =.*/actions = update_database,update_settings,update_frontend,update_calendar,write_file/g' \
         "$SBTESTCONF"
  check_result $?
  core_runb -c "$SBTESTCONF" -d "$SBTESTDB"
  sleep 10
  core_dummy_signal "$DUMMY_ALARM"
  sleep 5
  core_kill
  if [[ -e "$SBTESTFILE" ]]; then
    echo "Alarm detected:"
    cat "$SBTESTFILE"
    rm "$SBTESTFILE"
    check_result_done 0 # OK
  else
    echo "No alarm detected!"
    check_result_done 1 # ERROR
  fi
}

debug_test() {
  local TESTS=$ALL_TESTS
  if [[ $# -gt 0 ]]; then
    TESTS=""
    local T
    for T in "$@"; do
      if [[ "${T^^}" == "${T_ALL^^}" ]]; then
        TESTS=$ALL_TESTS
      elif echo "$ALL_TESTS" | grep -q -w "$T"; then
        if [[ "$TESTS" == "" ]]; then
          TESTS=$T
        elif ! echo "$TESTS" | grep -q -w "$T"; then
          TESTS="$TESTS $T"
        fi
      else
        #echo_error "Invalid test: $T\n"
        #print_usage; exit 1
        echo_error "Invalid test: $T"
        echo_error "Available tests: $ALL_TESTS"
        exit 1
      fi
    done
  fi

  local TEST=""
  for TEST in $TESTS; do
    if [[ "$TEST" == "$T_PYLINT" ]]; then
      debug_test_pylint
    elif [[ "$TEST" == "$T_MYPY" ]]; then
      debug_test_mypy
    elif [[ "$TEST" == "$T_TIDY" ]]; then
      debug_test_tidy
    elif [[ "$TEST" == "$T_ESLINT" ]]; then
      debug_test_eslint
    elif [[ "$TEST" == "$T_SHELLCHECK" ]]; then
      debug_test_shellcheck
    elif [[ "$TEST" == "$T_PYTEST" ]]; then
      debug_test_pytest
    elif [[ "$TEST" == "$T_RUNTEST" ]]; then
      debug_test_runtest
    fi
  done

  return 0
}
