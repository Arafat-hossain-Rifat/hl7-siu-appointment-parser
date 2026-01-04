# HL7 SIU Appointment Parser

## Overview

This project is a Python-based parser for **HL7 v2.x SIU^S12 messages**, designed to convert HL7 scheduling messages into a **normalized JSON format**. 

---

## High-Level Design

- **Parser (`utils.py`)**
  - Extracts fields from HL7 segments:
    - `MSH` – message metadata and type validation
    - `SCH` – appointment ID, datetime, location, and reason
    - `PID` – patient identifiers and demographics
    - `PV1` – provider information
  - Normalizes timestamps into ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`)
  - Handles missing or empty fields gracefully
  - Raises errors for invalid datetime formats or unsupported message types
  - Returns a **dictionary** representing the appointment, ready for JSON serialization

- **Command-Line Interface (`parser.py`)**
  - Reads a `.hl7` file containing one or more SIU^S12 messages
  - Splits multiple messages in a single file
  - Uses the parser function to extract structured data
  - Prints JSON output or saves it to a file
  - Handles errors gracefully and provides optional verbose output

- **Testing (`test_parser.py`)**
  - Unit tests for:
    - Valid messages
    - Missing SCH or PID segments
    - Empty fields
    - Malformed datetime
    - Invalid message types
    - Multiple messages in one file
    

- **Docker Support**
  - Dockerfile provided to run the parser in a container
  - Command to run:  
    docker run --rm -v ${PWD}:/app hl7-parser input.hl7
    

---

## How to Run the Parser

### Locally

1. Ensure Python 3.8+ is installed
2. Clone this repository:
   git clone https://github.com/Arafat-hossain-Rifat/hl7-siu-appointment-parser.git
   cd hl7-siu-appointment-parser
   
Run the parser with a HL7 file:

python parser.py input.hl7

Save output to a file:

python parser.py input.hl7 --output output.json

Use verbose mode for detailed errors:

python parser.py input.hl7 --verbose

Using Docker

Build the Docker image:

docker build -t hl7-parser 
.
Run the parser in Docker:

docker run --rm -v ${PWD}:/app hl7-parser input.hl7

Save JSON output:

docker run --rm -v ${PWD}:/app hl7-parser input.hl7 --output output.json

Running Tests

Unit tests are included in test_parser.py using Python’s unittest module:

python -m unittest test_parser.py

Test results:

. indicates a passed test

F indicates a failed test

E indicates an error


Assumptions and Trade-offs

Assumptions

Messages use pipe (|) delimiters and standard HL7 segment order.

Only SIU^S12 messages are parsed; other types are ignored.

Optional fields may be empty; parser handles them gracefully.

Multiple messages may exist in a single file, separated by MSH.

ISO 8601 format is used for all normalized timestamps.


Trade-offs

Manual parsing is used instead of HL7 libraries for clarity and assessment purposes.

Minimal validation on non-critical fields to simplify parsing.

Provider names are constructed as "Dr <Last> <First>" based on PV1 segment fields.


Example Input (input.hl7)

MSH|^~\&|EMR|HOSPITAL|RCM|RCMSYSTEM|202505021200||SIU^S12|12345|P|2.3
SCH|123456^A|...|...|202505021300|...|Clinic A - Room 203|General Consultation
PID|1||P12345^^^HOSP^MR||Doe^John||19850210|M
PV1|1|...|D67890^Smith^Dr

MSH|^~\&|EMR|HOSPITAL|RCM|RCMSYSTEM|202505031100||SIU^S12|12346|P|2.3
SCH|654321^B|...|...|202505031400|...|Clinic B - Room 105|Follow-up Visit
PID|1||P67890^^^HOSP^MR||Hossain^Arafat||19970311|M
PV1|1|...|D54321^Khan^Dr


Project Structure
```text
HL7-SIU-Appointment-Parser/
│
├─ parser.py # Command-line interface
├─ utils.py # HL7 parser logic
├─ test_parser.py # Unit tests
├─ Dockerfile # Docker build instructions
├─ input.hl7 # Sample HL7 input file
```


JSON Output
```json
[
  {
    "appointment_id": "123456",
    "appointment_datetime": "2025-05-02T13:00:00Z",
    "patient": {
      "patient_id": "P12345",
      "name": "John Doe",
      "dob": "19850210",
      "gender": "M"
    },
    "provider": {
      "provider_id": "D67890",
      "provider_name": "Dr Smith"
    },
    "location": "Clinic A - Room 203",
    "reason": "General Consultation"
  },
  {
    "appointment_id": "654321",
    "appointment_datetime": "2025-05-03T14:00:00Z",
    "patient": {
      "patient_id": "P67890",
      "name": "Arafat Hossain",
      "dob": "19970311",
      "gender": "M"
    },
    "provider": {
      "provider_id": "D54321",
      "provider_name": "Dr Khan"
    },
    "location": "Clinic B - Room 105",
    "reason": "Follow-up Visit"
  }
]
```
