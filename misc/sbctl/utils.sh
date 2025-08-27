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
[[ -n ${LIB_SB_UTILS+defined} ]] && return; readonly LIB_SB_UTILS=1

###################################################################
#  Includes and Definitions
###################################################################

# Output formatting
readonly OUTPUT_RESET="\e[0m"   # regular output
readonly OUTPUT_BOLD="\e[1m"    # bold/bright
readonly OUTPUT_UNDER="\e[4m"   # underlined
readonly OUTPUT_RED="\e[31m"    # fatal error
readonly OUTPUT_GREEN="\e[32m"  # important messages (startup, ...)
readonly OUTPUT_YELLOW="\e[33m" # error
readonly OUTPUT_BLUE="\e[34m"   # debug output

# Options for ask_yes_no
readonly ASK_DEFAULT_NONE=-1
readonly ASK_DEFAULT_YES=0
readonly ASK_DEFAULT_NO=1

# Options for ask_text
readonly ASK_INPUT_HIDDEN=0   # hidden text (e.g. passwords)
readonly ASK_INPUT_COMPLETE=1 # regular text with autocompletion
readonly ASK_INPUT_REGULAR=2  # regular text without autocompletion

###################################################################
#  Functions
###################################################################

echo_error() {
  echo -e "${OUTPUT_BOLD}${OUTPUT_RED}$*${OUTPUT_RESET}" >>/dev/stderr
}

echo_ok() {
  echo -e "${OUTPUT_BOLD}${OUTPUT_GREEN}$*${OUTPUT_RESET}"
}

echo_bold() {
  echo -e "${OUTPUT_BOLD}$*${OUTPUT_RESET}"
}

check_result() {
  local RESULT=$1
  if [[ $RESULT -ne 0 ]]; then
    echo_error "Failed. Fatal error."
    exit "$RESULT"
  else
    return 0
  fi
}

check_result_done() {
  local RESULT=$1
  if [[ $RESULT -ne 0 ]]; then
    echo_error "Failed. Fatal error."
    exit "$RESULT"
  else
    echo_ok "Done."
    return 0
  fi
}

get_setting() {
  local CONFIGFILE_=$1
  local SECTION_=$2
  local KEY_=$3
  local DEFAULT_=$4
  local -n VALUE_REF_=$5

  # check if config file exists
  if [[ -f "$CONFIGFILE_" ]]; then
    local VALUE_
    VALUE_=$(awk -v SECTION="$SECTION_" -v KEY="$KEY_" '
    function trim(s) { gsub(/^[[:space:]]+|[[:space:]]+$/, "", s); return s }

    BEGIN { found = 0; active_section = "" }    # initialize state variables
    {
      line=$0
      sub(/^[[:space:]]*[;#].*$/, "", line)     # remove lines that only consist of a comment
      # sub(/[;#].*$/, "", line)                  # remove trailing comments (optional)
      line = trim(line)                         # remove leading and trailing whitespace

      if(line == "")                            # ignore empty lines
        next

      if(line ~ /^\[.+\]$/){                    # handle sections -> change active section
        active_section = substr(line, 2, length(line)-2) # extract section name and set active section
        next
      }

      if(active_section != SECTION)             # wrong section ? -> ignore line
        next

      pos = match(line, /=/)                    # search for equal sign (=)
      if(pos <= 0)                              # no key=value line ? -> ignore line
        next

      current_key=trim(substr(line, 1, pos-1))  # extract key and remove remaining whitespace
      if(current_key != KEY)                    # wrong key ? -> ignore line
        next

      # found correct key in correct section
      current_value=trim(substr(line, pos+1))   # extract value and remove remaining whitespace
      print current_value                       # print/return the value
      found = 1                                 # mark operation as successful
      exit                                      # terminate input processing
    }
    END { exit !found }                         # exit and return whether the value could be retrieved
    ' "$CONFIGFILE_")
    local RESULT_=$?

    if [[ $RESULT_ -eq 0 ]]; then
      # use retrieved value from config
      VALUE_REF_=$VALUE_
      return 0
    fi
  fi

  # use default value
  VALUE_REF_=$DEFAULT_
  return 1
}

is_raspberry_pi() {
  local MODEL_FILE=/proc/device-tree/model # /sys/firmware/devicetree/base/model
  if [[ ! -f $MODEL_FILE ]]; then
    return 1 # FALSE
  fi

  MODEL=$(tr -d '\0' < $MODEL_FILE)
  if [[ "$MODEL" =~ ^"Raspberry Pi" ]]; then # some Raspberry Pi (model starts with "Raspberry Pi")
    return 0 # TRUE
  fi

  return 1 # FALSE
}

require_sudo() {
  if [[ "$UID" -ne 0 ]]; then
    echo_error "This command must be run as root:"
    if core_is_installed; then
      local BINARY=""
      BINARY=$(basename "$0")
      echo_error "  sudo $BINARY $*"
    else
      echo_error "  sudo $0 $*"
    fi
    exit 1
  fi
}

require_params() {
  local HAVE=$1
  local WANT_MIN=0
  local WANT_MAX=0

  if [[ $# == 2 ]]; then
    local WANT=$2
    WANT_MIN=$WANT
    WANT_MAX=$WANT
  else
    WANT_MIN=$2
    WANT_MAX=$3
  fi

  if [[ $HAVE -lt $WANT_MIN ]]; then
    echo_error "Missing parameters!\n"
    print_usage; exit 1
  elif [[ $WANT_MAX -ge 0 && $HAVE -gt $WANT_MAX ]]; then
    echo_error "Too many parameters!\n"
    print_usage; exit 1
  fi
}

ask_yes_no() {
  local QUESTION_=$1
  local DEFAULT_=$ASK_DEFAULT_NONE
  local RESULT_=0
  local YN_

  if [[ $# -ge 2 ]]; then
    DEFAULT_=$2
  fi

  while true; do
    if [[ $DEFAULT_ -eq $ASK_DEFAULT_YES ]]; then
      read -r -p "$QUESTION_ (yes/no) [default: yes] " YN_
    elif [[ $DEFAULT_ -eq $ASK_DEFAULT_NO ]]; then
      read -r -p "$QUESTION_ (yes/no) [default: no] " YN_
    else # $ASK_DEFAULT_NONE
      read -r -p "$QUESTION_ (yes/no) " YN_
    fi
    case $YN_ in
      [Yy]* )
        echo " -> yes"; RESULT_=0; break
        ;;
      [Nn]* )
        echo " -> no"; RESULT_=1; break
        ;;
      * )
        if [[ $DEFAULT_ -eq $ASK_DEFAULT_YES ]]; then
          echo " -> yes"; RESULT_=0; break
        elif [[ $DEFAULT_ -eq $ASK_DEFAULT_NO ]]; then
          echo " -> no"; RESULT_=1; break
        else # $ASK_DEFAULT_NONE
          echo " Please answer yes or no."
        fi
        ;;
    esac
  done

  if [[ $# -ge 3 ]]; then
    local -n RESULT_REF_=$3
    RESULT_REF_=$RESULT_
  fi

  return $RESULT_
}

ask_text() {
  local QUESTION_=$1
  local MODE_=$2
  local DEFAULT_=$3
  local -n RESULT_REF_=$4

  local RESULT_=0
  local MESSAGE_
  local VALUE_

  if [[ "$DEFAULT_" == "" ]]; then
    MESSAGE_="$QUESTION_: "
  else
    MESSAGE_="$QUESTION_ [default: $DEFAULT_]: "
  fi

  if [[ $MODE_ -eq $ASK_INPUT_HIDDEN ]]; then
    IFS="" read -s -r -p "$MESSAGE_" VALUE_
    echo ""
  elif [[ $MODE_ -eq $ASK_INPUT_COMPLETE ]]; then
    IFS="" read -e -r -p "$MESSAGE_" VALUE_
  else # $ASK_INPUT_REGULAR
    IFS="" read -r -p "$MESSAGE_" VALUE_
  fi

  if [[ -z "$VALUE_" && -n "$DEFAULT_" ]]; then
    VALUE_=$DEFAULT_
  fi

  if [[ -n "$VALUE_" ]]; then
    if [[ $MODE_ -eq $ASK_INPUT_HIDDEN ]]; then
      echo " -> specified"
    else # $ASK_INPUT_COMPLETE or $ASK_INPUT_REGULAR
      echo " -> $VALUE_"
    fi
  else
    echo " -> none"
  fi

  RESULT_REF_=$VALUE_
}

ask_option() {
  local QUESTION_=$1
  local OPTIONS_=$2
  local DEFAULT_=$3
  local -n RESULT_REF_=$4

  echo "$QUESTION_ [default: $DEFAULT_]:"
  PS3="Enter a number: "
  select OPT_ in $OPTIONS_; do
    #echo $REPLY
    case $OPT_ in
      "")
        echo " Please select a valid option."
        ;;
      *)
        echo " -> $OPT_"
        RESULT_REF_=$OPT_
        break
        ;;
    esac
  done

  return 0
}
