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

class StringConverter:
    """StringConverter provides helper functions to store multiline text in a single line (and restore it).
    It is used for CSV files, the configuration file and console output."""

    @staticmethod
    def singleline2string(csvText: str) -> str:
        dbText = ""
        act = False

        for c in csvText:
            if act is False and c == '\\':
                act = True
            elif act is True and c == 'n':
                dbText += '\n'
                act = False
            elif act is True and c == '\\':
                dbText += '\\'
                act = False
            else:
                dbText += c

        return dbText


    @staticmethod
    def string2singleline(dbText: str) -> str:
        csvText = ""

        for c in dbText:
            if c == '\\':
                csvText += '\\\\'
            elif c == '\n':
                csvText += '\\n'
            else:
                csvText += c

        return csvText
