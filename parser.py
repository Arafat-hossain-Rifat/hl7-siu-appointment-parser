import sys
import argparse
import json
from utils import parse_h17_message  

# ---------------------------
# Custom Exceptions for clarity
# ---------------------------
class HL7ParseError(Exception):
    pass

class InvalidMessageTypeError(HL7ParseError):
    pass

class MissingSegmentError(HL7ParseError):
    pass

# ---------------------------
# Streaming HL7 file parser
# ---------------------------
def parse_file_stream(filepath):
    """
    Generator to read HL7 messages one by one from a file.
    Handles large files efficiently.
    """
    message = ""
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  
            if line.startswith("MSH") and message:
                try:
                    yield parse_h17_message(message)
                except Exception as e:
                    raise HL7ParseError(f"Error parsing message:\n{message}\n{e}")
                message = line
            else:
                message += "\n" + line if message else line

        if message:
            try:
                yield parse_h17_message(message)
            except Exception as e:
                raise HL7ParseError(f"Error parsing message:\n{message}\n{e}")

# ---------------------------
# Main parsing function
# ---------------------------
def parse_file(filepath):
    results = []
    try:
        for parsed in parse_file_stream(filepath):
            results.append(parsed)
    except HL7ParseError as e:
        print(f"Parsing error: {e}", file=sys.stderr)
    return results

# ---------------------------
# Command Line Interface
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="HL7 SIU Appointment Parser")
    parser.add_argument("file", help="Path to the .hl7 input file")
    parser.add_argument(
        "--output", "-o", help="Path to output JSON file (optional)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed errors"
    )
    args = parser.parse_args()

    try:
        results = parse_file(args.file)
        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.output}")
        else:
            print(json.dumps(results, indent=2))
    except HL7ParseError as e:
        if args.verbose:
            print(f"Parsing error:\n{e}", file=sys.stderr)
        else:
            print(f"Error parsing HL7 file. Use -v for details.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
