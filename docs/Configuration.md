# SituationBoard Configuration
The configuration of SituationBoard is stored in the ```situationboard.conf``` file.
It is necessary to adjust these settings before starting SituationBoard for the first time.
The configuration file is divided into several sections.
Within each section individual settings are specified in form of key/value pairs:
```
[section]
key = value
# some comment
```

In addition to the settings stated below, all source and action plugins also feature a ```debug``` setting that can be used (```debug = True```) to enable plugin specific debug messages.

Important and frequently used settings are highlighted in **bold**.

## General Settings

### Backend
The backend settings adjust the general behaviour of the server backend.
Currently, the following settings are available in the ```[backend]``` section of the configuration:

| Setting                      | Description                                                                                                                                                       | Default Value                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| **server_host**              | Hostname or IP address for the server to listen on (127.0.0.1: available only locally; 0.0.0.0: available also for other machines)                                | "127.0.0.1" (local only)      |
| **server_port**              | Port number for the server to listen on                                                                                                                           | 5000                          |
| debug                        | Enable debug mode for the backend server                                                                                                                          | False                         |
| reloader                     | Enable Flask reloader                                                                                                                                             | False                         |
| web_api                      | Enable Web API to allow retrieval of system state and statistics                                                                                                  | False                         |
| loop_sleep_duration          | Duration slept in the event loop between polling/handling of alarm events (in seconds)                                                                            | 1 second                      |
| **sources**                  | Comma-separated list of active sources (i.e. source plugins)                                                                                                      | [] (none)                     |
| **actions**                  | Comma-separated list of active actions (i.e. action plugins)                                                                                                      | [] (none)                     |

### Frontend
The frontend settings adjust the appearance and behaviour of the standby view and the alarm view.
Currently, the following settings are available in the ```[frontend]``` section of the configuration:

| Setting                      | Description                                                                                                                                                       | Default Value                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| **header**                   | Header of the standby view (typically the name of the organization)                                                                                               | "Feuerwehr Musterdorf"        |
| **news**                     | Important news shown in the standby view (leave empty to hide this line)                                                                                          | "Herzlich Willkommen"         |
| debug                        | Enable debug output for frontend (java script)                                                                                                                    | False                         |
| **language**                 | Language of the frontend UI; currently only english (en) and german (de) is available                                                                             | "en"                          |
| **alarm_duration**           | Duration until an alarm disappears and the standby view becomes active again (in seconds)                                                                         | 60 * 60 seconds (1 hour)      |
| **alarm_show_maps**          | Maps shown during an alarm: Alarm Location ("location"); Route ("route"); "both"; "none"                                                                          | "both"                        |
| standby_show_statistics      | Enable statistics in the standby view                                                                                                                             | True                          |
| standby_show_clock           | Enable clock (and date) in the standby view                                                                                                                       | True                          |
| page_reload_duration         | Duration between two page reloads of the frontend (in seconds; 0 = never)                                                                                         | 0 (never)                     |
| calendar_url                 | URL of the calendar (ICS) file – should typically match the destination_url setting of the update_calendar plugin but exclude the "frontend/" prefix              | "data/calendar.ics"           |
| calendar_update_duration     | Duration between two updates of the calendar in the frontend (in seconds; 0 = never) – set this to never (0) if you use the update_calendar plugin                | 0 (never)                     |
| map_service                  | The map service used: Google Maps ("google") or Open Street Maps ("osm")                                                                                          | "osm"                         |
| map_api_key                  | Your personal API key (only required for Google Maps API v3)                                                                                                      | "" (none)                     |
| map_zoom                     | Map zoom level 1.0 - 20.0 depending on the map service (only affects location map; route map will show the whole route)                                           | 19.0                          |
| map_type                     | Different map views ("default", "roadmap", "satellite", "hybrid", "terrain") of the map (currently only supported by Google Maps)                                 | "default" (= "hybrid")        |
| map_emergency_layer          | Show emergency objects ("none", "fire", "medical", "all") in the map (currently only supported by OSM)                                                            | "all"                         |
| **map_home_latitude**        | Latitude location of the fire/emergency station (i.e. start of the journey for map view)                                                                          | 0.0                           |
| **map_home_longitude**       | Longitude location of the fire/emergency station (i.e. start of the journey for map view)                                                                         | 0.0                           |
| **map_search_location**      | Determines whether the frontend tries to search the location based on the address if there are no coordinates of the location provided in the alarm event         | False                         |
| show_splash_screen           | Determines whether a splash screen is shown when the frontend is loaded                                                                                           | True                          |

## Sources
Alarm sources allow the detection of alarm events.
They are activated by adding them to the list of ```sources``` in the ```[backend]``` section of the configuration:
```
sources = source1,source2,...

# for example:
sources = dummy,binary,sms
```
Each source has its own configuration section:
```
# for example:
[source:binary]
key = value
```
Some source plugins may support multiple instances.
When using a source plugin more than once, it is required to append a unique instance name
to the individual source names (separated by ```:```):
```
# for example:
sources = binary:one,binary:two,sms
```
The same holds for the corresponding configuration sections:
```
# for example:
[source:binary:one]
key = value

[source:binary:two]
key = value
```

Sources are scanned in the order they are specified in the list of sources.
Currently, the following sources are available:

### SMS Source
The ```sms``` source allows to receive alarm events via SMS messages.
The SMS messages are received with the help of the [Gammu](https://wammu.eu/gammu/) SMS/phone library and then parsed
with a specified parser to retrieve information on the individual alarms (like the actual alarm event or location).
The SMS source is configured in the ```[source:sms]``` section and has the following settings:

| Setting                      | Description                                                                                                                                                       | Default Value                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| gammu_config                 | Path to the Gammu configuration file                                                                                                                              | "/etc/gammu-smsdrc"           |
| **parser**                   | Selected message parser                                                                                                                                           | "sms"                         |
| allowlist                    | Comma-separated list of allowed/accepted phone numbers in E.164 / FQTN format without whitespace/slashes (e.g. +491234567890)                                     | [] (accept all)               |
| denylist                     | Comma-separated list of denied/rejected phone numbers in E.164 / FQTN format without whitespace/slashes (e.g. +491234567890)                                      | [] (reject none)              |

Depending on your setup, further adjustments (e.g. modem device, modem connection or SIM PIN)
might be necessary in the Gammu configuration file ```/etc/gammu-smsdrc```.

#### Tested Cellular USB Modems
The following cellular USB modems were tested successfully with the stated configuration parameters:

| Cellular USB Modem          | USB-ID (as modem)  | Device        | Connection  | Other USB-IDs (used in other operation modes)         |
|-----------------------------|--------------------|---------------|-------------|-------------------------------------------------------|
| **Huawei E303 (51077742)**  | 12d1:1506          | /dev/ttyUSB0  | at          | (none)                                                |
| **Huawei E303 (51070NQP)**  | 12d1:1001          | /dev/ttyUSB0  | at          | 12d1:1f01 (storage device), 12d1:14dc (network card)  |

The devices in this table are identified by a USB-ID consisting of a vendor ID and a product ID.
Some USB devices can operate in different modes (e.g. as a storage device containing device drivers,
a network card and as an actual modem). These different modes are often represented by different product IDs:

| Cellular USB Modem          | Vendor ID | Vendor                         | Product ID | Product                                      | Device Mode    | Comment                                                  |
|-----------------------------|-----------|--------------------------------|------------|----------------------------------------------|----------------|----------------------------------------------------------|
| **Huawei E303 (51077742)**  | **12d1**  | Huawei Technologies Co., Ltd.  | **1506**   | Modem/Networkcard                            | **modem**      | required mode (default and only mode)                    |
| **Huawei E303 (51070NQP)**  | **12d1**  | Huawei Technologies Co., Ltd.  | 1f01       | E353/E3131 (Mass storage mode)               | storage device | default mode (without usb_modeswitch)                    |
|                             |           |                                | 14dc       | E33372 LTE/UMTS/GSM HiLink Modem/Networkcard | network card   | default target mode (with stock usb_modeswitch)          |
|                             |           |                                | **1001**   | E161/E169/E620/E800 HSDPA Modem              | **modem**      | required mode (enforced with custom usb_modeswitch file) |

You can retrieve the (current) vendor/product ID of your USB modem with the ```lsusb``` command line tool.
The ```usb_modeswitch``` tool makes sure that the device is in the correct mode for usage as a modem.
After the SituationBoard installation, a reboot might be necessary before your device is recognized correctly.

**Important:**
USB modems can consume a lot of power (often exceeding the capabilities of the Raspberry Pi).
Therefore, it often makes sense to operate them on an externally-powered USB hub.

#### SMS Message Parser
Currently, there is only one message parser (the default ```sms``` parser) available.
It is configured in the ```[parser:sms]``` section and has the following settings:

| Setting                      | Description                                                                                                                                                       | Default Value                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| merge_duration               | Duration in which non-standard multipart SMS are merged (in seconds)                                                                                              | 90 seconds                    |
| **alarm_header**             | Message header identifying an alarm message                                                                                                                       | "SMS Alarm"                   |
| **alarm_senders**            | Comma-separated list of typical senders of alarms (phone number in E.164 / FQTN format) whose messages will be treated as alarm even if the header does not match | [] (none)                     |

Regarding alarm events, the SMS parser supports the following message format:
```
<ALARM_HEADER>
Alarmzeit: <DD.MM.YYYY HH:MM:SS>
EO: <LOCATION>, <LOCATION_DETAILS>
<EVENT_DETAILS>
STW: <EVENT>
Bem: <MULTILINE_COMMENT>
<MULTILINE_COMMENT>
<MULTILINE_COMMENT>
```

An example SMS could therefore look like:
```
ILS BA-FO SMS Alarm
Alarmzeit: 03.09.2020 16:24:12
EO: Musterort - Mustergemeinde, Musterstraße 1
Technische Hilfe / #T2719#klein#Straße reinigen
STW: THL 1
Bem: Längere Ölspur
Beginn kurz vor Aussiedlerhof
```

### Divera Source
The `divera` source allows to retrieve alarms from the web API of the [Divera 24/7](https://www.divera247.com) alarm service.
Alongside the actual alarm infos it is also possible to retrieve the responses of crew members to an alarm and the current status of vehicles.
The Divera source is configured in the ```[source:divera]``` section and has the following settings:

| Setting                      | Description                                                                                                                                                       | Default Value                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| **api_key**                  | API key (also called access key by Divera) of the organization (required)                                                                                         | ""                            |
| timeout                      | Request timeout (in seconds)                                                                                                                                      | 5 seconds                     |
| api_url                      | URL of the API (adjust only when testing with a manual mock API setup)                                                                                            | "https://www.divera247.com"   |
| use_mock_api                 | Use mock API instead of the specified API URL to simulate alarm events (starts a local mock API server; ignores the specified api_url and api_key)                | False                         |
| ignore_test_alarm            | Ignore test alarms (i.e. alarms with an author_id of 0)                                                                                                           | False                         |
| **show_vehicle_status**      | Update the news setting with the current status of the vehicles to show it in the standby view                                                                    | True                          |
| **show_crew_responses**      | Append the crew responses to the comment of the alarm event to show them in the alarm view                                                                        | True                          |
| response_id_fast             | Identifier used for responses that signal fast availability of a crew member (< 5 min)                                                                            | "99148"                       |
| response_id_slow             | Identifier used for responses that signal slow availability of a crew member (< 10 min)                                                                           | "99149"                       |
| response_id_na               | Identifier used for responses that signal no availability of a crew member (n/a)                                                                                  | "99150"                       |

### Binary Source
The ```binary``` source allows to detect alarm events based on a GPIO input of the Raspberry Pi.
A typical use case for the ```binary``` source is to connect a pager as alarm source (e.g. as fallback or to forward alarm events to emergency personnel).
Unlike the SMS source it does not provide additional information on the alarm (like the actual alarm event or location).
The binary source is configured in the ```[source:binary]``` section and has the following settings:

| Setting                      | Description                                                                                                                                                       | Default Value                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| **message**                  | Text show as alarm message                                                                                                                                        | "Alarm"                       |
| **pin**                      | BCM pin of the Raspberry Pi used for alarm detection                                                                                                              | 13 (BCM Pin 13)               |
| **active_high**              | Determines whether the IO pin is active high                                                                                                                      | False                         |

By appending unique instance names (e.g. ```binary:pager``` and ```[source:binary:pager]```),
more than one ```binary``` source can be used at the same time.

### Dummy Source
The ```dummy``` source allows to debug the system and its configuration without the need to trigger alarm events via SMS or binary input.
It generates dummy messages when a specific signal is sent to the backend process (e.g. via the ```sbctl``` tool).
Currently, the dummy source offers no settings.

To simulate a regular (text) alarm use:
```
sbctl dalarm
```

To simulate a binary alarm use:
```
sbctl dbinary
```

To simulate a remote update to settings (for example to the header or news line) use:
```
sbctl dsetting
```

## Actions
Actions are triggered by alarm events or on a regular timely manner.
They are activated by adding them to the list of ```actions``` in the ```[backend]``` section of the configuration:
```
actions = action1,action2,...

# for example:
actions = search_location,update_database,update_settings,update_frontend,update_calendar,send_poweralarm,toggle_outlet,activate_screen
```
Each action has its own configuration section:
```
# for example:
[action:toggle_outlet]
key = value
```
Some action plugins may support multiple instances.
When using an action plugin more than once, it is required to append a unique instance name
to the individual action names (separated by ```:```):
```
# for example:
actions = ...,toggle_outlet:one,toggle_outlet:two,...
```
The same holds for the corresponding configuration sections:
```
# for example:
[action:toggle_outlet:one]
key = value

[action:toggle_outlet:two]
key = value
```

Actions are triggered in the order they are specified in the list of actions.
Currently, the following actions are available:

### Search Location Action (should be 1st)
The ```search_location``` action is responsible to find the location (longitude and latitude) of an alarm event when only the address is known.
It should always be the first action since it might add location information to the alarm event that is useful for the following actions.
It is configured in the ```[action:search_location]``` section and has the following settings:

| Setting                      | Description                                                                                                                                                       | Default Value                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| timeout                      | Lookup Timeout (in seconds)                                                                                                                                       | 5 seconds                     |

### Update Database Action (should be 2nd)
The ```update_database``` action is responsible to add new alarm events to the database.
It should always be the second action and does not offer any settings.

### Update Settings Action (should be 3rd)
The ```update_settings``` action is responsible to adjust settings (like the header or news in the frontend) when special messages are received.
It should always be the third action since it might update settings that are visible in the frontend.
It is configured in the ```[action:update_settings]``` section and has the following settings:

| Setting                      | Description                                                                                                                                                       | Default Value                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| store_changes                | Store changes to config file                                                                                                                                      | True                          |

### Update Frontend Action (should be 4th)
The ```update_frontend``` action is responsible to update the frontend and show the alarm view when an alarm is detected.
It should always be the fourth action and does not offer any settings.

### Update Calendar Action (optional)
The optional ```update_calendar``` action is responsible to download updated versions of the calendar file to the frontend.
It is configured in the ```[action:update_calendar]``` section and has the following settings:

| Setting                      | Description                                                                                                                                                       | Default Value                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| **source_url**               | Source URL of the calendar (ICS) file                                                                                                                             | "" (none)                     |
| destination_url              | Destination filename of the calendar (ICS) file – should typically match the calendar_url setting in the frontend section but include a "frontend/" prefix        | "frontend/data/calendar.ics"  |
| **calendar_update_duration** | Duration between two updates of the calendar (in seconds; 0 = never)                                                                                              | 120 * 60 seconds (2 hours)    |
| timeout                      | Download Timeout (in seconds)                                                                                                                                     | 5 seconds                     |

### Send Message PowerAlarm Action (optional)
The optional ```send_poweralarm``` action is responsible to forward an alarm message to emergency personnel via the commercial [PowerAlarm](https://www.poweralarm.de) service.
It is configured in the ```[action:send_poweralarm]``` section and has the following settings:

| Setting                      | Description                                                                                                                                                       | Default Value                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| **api_key**                  | PowerAlarm API key                                                                                                                                                | "" (none)                     |
| timeout                      | Request timeout (in seconds)                                                                                                                                      | 5 seconds                     |
| **api_group_nodetails**      | Group alarmed with no detailed information (for text alarm messages)                                                                                              | "" (none)                     |
| **api_group_reduced**        | Group alarmed with reduced information (for text alarm messages)                                                                                                  | "" (none)                     |
| **api_group_full**           | Group alarmed with full information (for text alarm messages)                                                                                                     | "" (none)                     |
| **api_group_tablet**         | Additional group provided with full information (e.g. silent group for tablet devices)                                                                            | "" (none)                     |
| **api_group_binary**         | Group alarmed for binary alarm messages                                                                                                                           | "" (none)                     |
| **api_group_admin**          | Group informed for setting events and unhandled events (depending on the configuration)                                                                           | "" (none)                     |
| **alarm_message**            | Alarm message used as fallback text for invalid alarms and the nodetails group                                                                                    | "Alarm"                       |
| **send_invalid**             | Send invalid alarm events (e.g. triggered by currently incomplete alarm messages) to the specified alarm groups                                                   | True                          |
| deduplication_duration       | Do not send exactly the same message to the same group within the specified time span (in seconds; 0 = send always)                                               | 60 seconds                    |
| admin_send_setting           | Send setting events to admin group                                                                                                                                | False                         |
| admin_send_unhandled         | Send unhandled events to admin group                                                                                                                              | True                          |
| admin_send_invalid           | Send invalid alarm events to admin group                                                                                                                          | False                         |

### Toggle Output Action (optional)
The optional ```toggle_output``` action allows to toggle a GPIO output of the Raspberry Pi in case of an alarm.
It is configured in the ```[action:toggle_output]``` section and has the following settings:

| Setting                      | Description                                                                                                                                                       | Default Value                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| **pin**                      | BCM pin of the Raspberry Pi used as output                                                                                                                        | Pin 0                         |
| **active_high**              | Determines whether the IO pin is active high                                                                                                                      | True                          |
| reset_on_startup             | Determines whether the IO pin level (high/low) is reset during startup                                                                                            | True                          |
| **active_duration**          | Duration the IO pin is activated in seconds (0 = forever)                                                                                                         | 15 * 60 seconds (15 minutes)  |
| **max_alarm_age**            | Maximum age of the alarm to be handled (0 = any age)                                                                                                              | 5 * 60 seconds (5 minutes)    |
| **handle_alarm_updates**     | Determines whether alarm updates are also handled                                                                                                                 | False                         |
| toggle_valid                 | Toggle for valid alarm messages                                                                                                                                   | True                          |
| toggle_invalid               | Toggle for invalid alarm messages                                                                                                                                 | True                          |
| toggle_binary                | Toggle for binary alarm messages                                                                                                                                  | True                          |

By appending unique instance names (e.g. ```toggle_output:signal``` and ```[action:toggle_output:signal]```),
more than one ```toggle_output``` action can be used at the same time.

### Toggle Outlet Action (optional)
The optional ```toggle_outlet``` action allows to toggle a remote [myStrom](https://mystrom.com/wifi-switch/) outlet in case of an alarm.
It is configured in the ```[action:toggle_outlet]``` section and has the following settings:

| Setting                      | Description                                                                                                                                                       | Default Value                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| **api_url**                  | URL of the outlet                                                                                                                                                 | "" (none)                     |
| timeout                      | Request timeout (in seconds)                                                                                                                                      | 2 seconds                     |
| inverted                     | Determines whether the outlet state (on/off) is inverted                                                                                                          | False                         |
| reset_on_startup             | Determines whether the outlet state (on/off) is reset during startup                                                                                              | True                          |
| **active_duration**          | Duration the outlet is activated in seconds (0 = forever)                                                                                                         | 15 * 60 seconds (15 minutes)  |
| **max_alarm_age**            | Maximum age of the alarm to be handled (0 = any age)                                                                                                              | 5 * 60 seconds (5 minutes)    |
| **handle_alarm_updates**     | Determines whether alarm updates are also handled                                                                                                                 | False                         |
| toggle_valid                 | Toggle for valid alarm messages                                                                                                                                   | True                          |
| toggle_invalid               | Toggle for invalid alarm messages                                                                                                                                 | True                          |
| toggle_binary                | Toggle for binary alarm messages                                                                                                                                  | True                          |

By appending unique instance names (e.g. ```toggle_outlet:lamp``` and ```[action:toggle_outlet:lamp]```),
more than one ```toggle_outlet``` action can be used at the same time.

### Activate Screen Action (optional)
The optional ```activate_screen``` action is responsible to activate (i.e. power on) the attached display/screen/TV in case it is currently in standby.
It is configured in the ```[action:activate_screen]``` section and has the following settings:

| Setting                      | Description                                                                                                                                                       | Default Value                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| **active_duration**          | Duration the screen should be active after an alarm event in seconds (0 = forever)                                                                                | 0 (forever)                   |
| **max_alarm_age**            | Maximum age of the alarm to be handled (0 = any age)                                                                                                              | 5 * 60 seconds (5 minutes)    |
| **handle_alarm_updates**     | Determines whether alarm updates are also handled                                                                                                                 | False                         |

### Write File Action (for automated testing)
The optional ```write_file``` action writes detected alarms to a specified file.
This action is currently only used for automated testing.
It is configured in the ```[action:write_file]``` section and has the following settings:

| Setting                      | Description                                                                                                                                                       | Default Value                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| filename                     | Filename of the alarm file                                                                                                                                        | "alarm.txt"                   |
