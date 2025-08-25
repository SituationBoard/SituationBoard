# Changelog

This changelog lists the changes of all the SituationBoard versions.

Breaking changes (e.g. regarding configuration, database and CSV) always come with a version bump.
In contrast, minor changes/bugfixes might not come with a new version number.

## Version 1.15 (2025-09-06)

- Add source driver for the Divera 24/7 API
- Correct handling of updated and outdated alarm events
- Update GPIO support to work with new Raspberry Pi versions
- Update various dependencies and make related adjustments
- Improve automatic screen activation and CEC support
- Make storing of setting updates optional
- Make location search in frontend optional
- Add support for Wayland
- Adjust features installed by default
- Update and improve documentation

## Version 1.14 (2023-08-21)

- Fix websocket bug in backend
- Update frontend dependencies (OpenLayers)
- Replace xorg.conf with xset call at runtime

## Version 1.13 (2022-09-27)

- Introduce a generic list view widget
- Add support for repeating events and all-day events to the calendar widget
- Log source state changes and improve overall log output
- Specify required versions for Python and JavaScript dependencies
- Minor code cleanup and minor other improvements

## Version 1.12 (2021-02-23)

First public release
