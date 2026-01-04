from datetime import datetime

def parse_h17_message(message):
    
    lines = message.strip().split("\n")
    patient_data = {}
    provider_data = {}

    appointment_id = None
    appointment_datetime = None
    location = None
    reason = None

    for line in lines:
        parts = line.split("|")
        segment = parts[0]

        #Validate message type from MSH
        if segment == "MSH":
            message_type = parts[8] if len(parts) > 8 else None
            if message_type != "SIU^S12":
                raise ValueError(f"Unsupported message type: {message_type}")

        elif segment == "SCH":
            # Appointment ID
            appointment_id = parts[1].split("^")[0] if len(parts) > 1 else None

            # Appointment datetime
            appt_time = parts[4] if len(parts) > 4 else None
            if appt_time:
                try:
                    appointment_datetime = datetime.strptime(
                        appt_time, "%Y%m%d%H%M"
                    ).strftime("%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    raise ValueError(f"Invalid datetime format: {appt_time}")

            # Location and reason
            location = parts[6] if len(parts) > 6 else None
            reason = parts[7] if len(parts) > 7 else None

        elif segment == "PID":
            patient_id = parts[3].split("^")[0] if len(parts) > 3 else None
            last_name, first_name = (
                parts[5].split("^") + ["", ""]
            )[:2] if len(parts) > 5 else ("", "")
            dob = parts[7] if len(parts) > 7 else None
            gender = parts[8] if len(parts) > 8 else None
            patient_data = {
                "patient_id": patient_id,
                "name": f"{first_name} {last_name}".strip(),
                "dob": dob,
                "gender": gender
            }

        elif segment == "PV1":
            # Correct field for provider is parts
            provider_field = parts[3] if len(parts) > 3 else ""
            if provider_field:
                provider_parts = provider_field.split("^")
                provider_id = provider_parts[0] if len(provider_parts) > 0 else None
                if len(provider_parts) > 2:
                    provider_name = f"{provider_parts[2]} {provider_parts[1]}".strip()
                elif len(provider_parts) > 1:
                    provider_name = provider_parts[1]
                else:
                    provider_name = None
                provider_data = {
                    "provider_id": provider_id,
                    "provider_name": provider_name
                }

    # Build final JSON object
    return {
        "appointment_id": appointment_id,
        "appointment_datetime": appointment_datetime,
        "patient": patient_data,
        "provider": provider_data,
        "location": location,
        "reason": reason
    }
