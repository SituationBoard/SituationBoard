# Testing Message Parsers

Message parsers are automatically tested if there is a folder in the /tests/parser_input/ directory with the name of the parser containing the following files: 

### input.[txt,html]

This file contains the input information for the parser.

### output.json

A JSON file that is checked against the attributes of the returned AlarmEvent.

Example:

```json
{
  "result": {
    "event": "Alarm",
    "eventDetails": "Probealarm",
    "location": "Musterstraße 1 \n 12345 Musterhausen",
    "locationDetails": "Im 1. OG",
    "comment": "Probealarm",
    "locationLatitude": "51.163375",
    "locationLongitude": "10.447683"
  }
}
```
