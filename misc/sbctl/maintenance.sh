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
[[ -n ${LIB_SB_MAINTENANCE+defined} ]] && return; readonly LIB_SB_MAINTENANCE=1

###################################################################
#  Includes and Definitions
###################################################################

# none

###################################################################
#  Functions
###################################################################

maintenance_service_operation() {
  core_service_operation "$1"
  return $?
}

maintenance_service_show_log() {
  journalctl --all --pager-end --unit "$SBSERVICE"
  return $?
}

maintenance_export() {
  core_export "$1"
  return $?
}

maintenance_import() {
  local OPERATION=$1 # "import" or "rimport" (reset and import)
  local CSV_FILE=$2
  local RESULT=$?

  if [[ "$OPERATION" == "import" ]]; then
    core_service_suspend; local SERVICE_WAS_ACTIVE=$?
    echo_bold "Importing CSV data..."
    core_runf -i "$CSV_FILE"; RESULT=$?
    core_service_resume $SERVICE_WAS_ACTIVE
  elif [[ "$OPERATION" == "rimport" ]]; then
    core_service_suspend; local SERVICE_WAS_ACTIVE=$?
    echo_bold "Resetting and Importing CSV data..."
    core_runf -r -i "$CSV_FILE"; RESULT=$?
    core_service_resume $SERVICE_WAS_ACTIVE
  else
    echo_error "Invalid import operation."; RESULT=1
  fi

  return $RESULT
}

maintenance_show_version() {
  local VERSION="" GIT_INFO=""
  core_get_version VERSION
  core_get_git_info GIT_INFO
  echo "SituationBoard $VERSION ($GIT_INFO)"
  return 0
}

maintenance_backup() {
  local DESTINATION=$1
  local BACKUP_HOST="" # "" for local backups
  local BACKUP_PATH=$DESTINATION

  if [[ "$DESTINATION" == *":"* ]]; then
    # remote backup
    BACKUP_HOST=${DESTINATION%%:*}
    BACKUP_PATH=${DESTINATION#*:}
  fi

  local CURRENT_DATE="latest"
  CURRENT_DATE=$(date +"%Y-%m-%d")

  local CSV_FILE="situationboard.csv"

  local BACKUP_FOLDER_NAME="situationboard_backup_$CURRENT_DATE"
  local BACKUP_FOLDER="$SBTEMP/$BACKUP_FOLDER_NAME"
  mkdir -p "$BACKUP_FOLDER"

  core_service_suspend; local SERVICE_WAS_ACTIVE=$?

  core_export "$BACKUP_FOLDER/$CSV_FILE"
  local RESULT=$?
  if [[ $RESULT -ne 0 ]]; then
    echo_error "Failed to perform backup! Could not export CSV."
  else
    echo_bold "Backup data and config..."
    if [[ -f "$SBCONFIG" && -f "$SBDATABASE" ]]; then
      cp "$SBCONFIG" "$BACKUP_FOLDER/" 2>/dev/null
      cp "$SBDATABASE" "$BACKUP_FOLDER/" 2>/dev/null

      if [[ "$BACKUP_HOST" == "" ]]; then
        # local backup
        cp -r "$BACKUP_FOLDER" "$BACKUP_PATH"; RESULT=$?
        if [[ $RESULT -ne 0 ]]; then
          echo_error "Failed to perform backup! Could not copy backup to destination folder."
        else
          local FULL_PATH=""
          FULL_PATH=$(readlink -f "$BACKUP_PATH/$BACKUP_FOLDER_NAME" 2> /dev/null)
          echo "$FULL_PATH"
        fi
      else
        # remote backup
        scp -r "$BACKUP_FOLDER" "$BACKUP_HOST:$BACKUP_PATH"; RESULT=$?
        if [[ $RESULT -ne 0 ]]; then
          echo_error "Failed to perform backup! Could not copy backup to remote destination folder."
        fi
      fi
    else
      echo_error "Failed to perform backup! Either config file or database file did not exist."
      RESULT=1
    fi
  fi

  core_service_resume $SERVICE_WAS_ACTIVE

  rm -rf "$BACKUP_FOLDER"

  return $RESULT
}

maintenance_update() {
  local RESULT=1

  local OLD_VERSION="" OLD_GIT_INFO=""
  local NEW_VERSION="" NEW_GIT_INFO=""

  core_get_git_info OLD_GIT_INFO
  core_get_version OLD_VERSION

  core_service_suspend; local SERVICE_WAS_ACTIVE=$?

  echo_bold "Updating SituationBoard..."
  BRANCH=$(git -C "$SBPATH" rev-parse --abbrev-ref HEAD)
  RESULT=$?
  if [[ $RESULT -ne 0 ]]; then
    echo_error "Failed to perform auto update:"
    echo_error "Not a GIT repository!"
  elif [[ "$BRANCH" != "$SBRELEASEBRANCH" ]]; then
    echo_error "Failed to perform auto update:"
    echo_error "Not on $SBRELEASEBRANCH branch!"
    RESULT=1
  else
    git -C "$SBPATH" pull --ff-only
    RESULT=$?
    if [[ $RESULT -ne 0 ]]; then
      echo_error "Failed to perform auto update:"
      echo_error "Fast forward not possible!"
    fi
  fi

  core_get_git_info NEW_GIT_INFO
  core_get_version NEW_VERSION

  if [[ "$OLD_VERSION" == "$NEW_VERSION" ]]; then
    if [[ "$OLD_GIT_INFO" == "$NEW_GIT_INFO" ]]; then
      # no update available
      echo_bold "No update installed."
      echo "Current version: $OLD_VERSION ($OLD_GIT_INFO)"
    else
      # performed only a minor update (without breaking changes)
      echo_bold "Installed a minor update."
      echo "Old version: $OLD_VERSION ($OLD_GIT_INFO)"
      echo "New version: $NEW_VERSION ($NEW_GIT_INFO)"
    fi
    # we can restart the service (if required)
    core_service_resume $SERVICE_WAS_ACTIVE
  else
    # performed a major update (that might require user's attention)
    echo_bold "Installed a major update."
    echo "Old version: $OLD_VERSION ($OLD_GIT_INFO)"
    echo "New version: $NEW_VERSION ($NEW_GIT_INFO)"
    echo_bold "Read \"CHANGELOG.md\" first before starting SituationBoard again:"
    echo "There might be breaking changes that require adjustments in the config file or"
    echo "updating your installation by executing \"sbctl reinstall\" (e.g. to install new dependencies)."
  fi

  return $RESULT
}
