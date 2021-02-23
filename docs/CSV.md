# Alarm Events and CSV Files

Alarm events received from various sources are not only handled by the backend and visualized in the frontend.
Instead, these events are also stored in a database (e.g. to enable alarm statistics).
This data can be exported to a [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) file for external processing or as a backup.
Accordingly, CSV files can also be imported into the database (e.g. to add/edit alarms manually or to restore a backup).

The sections below introduce the format of these CSV files.
For more information on the import/export commands themselves consult [README.md](../README.md).

## Example CSV File
The following block shows the content of an example CSV file:
```
Timestamp;Event;EventDetails;Location;LocationDetails;Comment;AlarmTimestamp;LocationLatitude;LocationLongitude;Source;Sender;Raw;Flags
2020-07-24 00:43:58;B 4;Großbrand Gebäude;Musterheim;Musterstr. 112;Weitere\nEinsatzdetails;2020-07-24 00:42:57;1.12;-13.2;SMS;+49112;Komplette Originalnachricht;VALID
2020-08-15 15:46:34;THL 3;Technische Hilfeleistung;Musterdorf;Hauptstr. 112;Kommentar;2020-08-15 15:45:33;1.12;-13.2;SMS;+49112;Komplette Originalnachricht;VALID
2020-09-04 17:53:02;;;;;;2020-09-04 17:53:02;0.0;0.0;BINARY;;Einsatzalarmierung;BINARY
2020-10-16 19:07:14;Fehlalarm Brandmeldeanlage;;Industriegebiet Musterstadt;Versandzentrum;;2020-10-16 19:06:13;0.0;0.0;MANUAL;;;VALID
```

It consists of a header followed by alarm events from various kinds and sources (one event per line).
The individual fields are separated by a semicolon ```;```.
Line breaks within multi-line fields are represented by ```\n```.

## Overview of all CSV Fields
The following table gives an overview of all the fields stored in CSV files:

| Column            | Description                                                                    | Example                        |
|-------------------|--------------------------------------------------------------------------------|--------------------------------|
| Timestamp         | Timestamp of event reception (in the format YYYY-MM-DD HH:MM:DD)               | 2020-07-24 00:43:58            |
| Event             | Short event name or identifier                                                 | B4                             |
| EventDetails      | Long event name or description                                                 | Großbrand Gebäude              |
| Location          | Location (e.g. city)                                                           | Musterheim                     |
| LocationDetails   | Exact location (e.g. street)                                                   | Musterstr. 112                 |
| Comment           | Additional comments/remarks regarding the alarm (multi-line string)            | Weitere\nEinsatzdetails        |
| AlarmTimestamp    | Timestamp of the original alarm (in the format YYYY-MM-DD HH:MM:DD)            | 2020-07-24 00:42:57            |
| LocationLatitude  | Latitude of the GPS position (if available – 0.0 otherwise)                    | 1.12                           | 
| LocationLongitude | Longitude of the GPS position (if available – 0.0 otherwise)                   | -13.2                          | 
| Source            | ```SMS```, ```BINARY```, ```DUMMY``` or ```MANUAL``` (used for manual entries) | ```SMS```                      |
| Sender            | Address identifying the alarm sender (e.g. phone number)                       | +49112                         |
| Raw               | Raw content of the original alarm message (e.g. SMS)                           | Komplette Originalnachricht    |
| Flags             | ```VALID``` or ```INVALID``` (binary events always use ```BINARY``` instead)   | ```VALID```                    |
