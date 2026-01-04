import unittest
from utils import parse_h17_message


class TestHL7Parser(unittest.TestCase):

    def setUp(self):
        # Valid HL7 messages
        self.valid_message_1 = """MSH|^~\\&|EMR|HOSPITAL|RCM|RCMSYSTEM|202505021200||SIU^S12|12345|P|2.3
SCH|123456^A|...|...|202505021300|...|Clinic A - Room 203|General Consultation
PID|1||P12345^^^HOSP^MR||Doe^John||19850210|M
PV1|1|...|D67890^Smith^Dr"""

        self.valid_message_2 = """MSH|^~\\&|EMR|HOSPITAL|RCM|RCMSYSTEM|202505031100||SIU^S12|12346|P|2.3
SCH|654321^B|...|...|202505031400|...|Clinic B - Room 105|Follow-up Visit
PID|1||P67890^^^HOSP^MR||Hossain^Arafat||19970311|M
PV1|1|...|D54321^Khan^Dr"""

        # Missing SCH segment
        self.missing_sch = """MSH|^~\\&|EMR|HOSPITAL|RCM|RCMSYSTEM|202505041000||SIU^S12|12347|P|2.3
PID|1||P11111^^^HOSP^MR||Smith^Alice||19900101|F
PV1|1|...|D11111^Jones^Dr"""

        # Missing PID segment
        self.missing_pid = """MSH|^~\\&|EMR|HOSPITAL|RCM|RCMSYSTEM|202505051000||SIU^S12|12348|P|2.3
SCH|777888^C|...|...|202505051200|...|Clinic C - Room 301|Checkup
PV1|1|...|D22222^Brown^Dr"""

        # Malformed datetime
        self.malformed_datetime = """MSH|^~\\&|EMR|HOSPITAL|RCM|RCMSYSTEM|202505061000||SIU^S12|12349|P|2.3
SCH|999000^D|...|...|INVALIDTIME|...|Clinic D - Room 401|Follow-up
PID|1||P33333^^^HOSP^MR||Lee^Chris||19880303|M
PV1|1|...|D33333^White^Dr"""

        # Invalid message type
        self.invalid_type = """MSH|^~\\&|EMR|HOSPITAL|RCM|RCMSYSTEM|202505071000||ADT^A01|12350|P|2.3
SCH|111222^E|...|...|202505071200|...|Clinic E - Room 501|Consultation
PID|1||P44444^^^HOSP^MR||Taylor^Sam||19950505|F
PV1|1|...|D44444^Black^Dr"""

    # -------------------- VALID PARSING --------------------

    def test_parse_valid_message(self):
        result = parse_h17_message(self.valid_message_1)
        self.assertEqual(result["appointment_id"], "123456")
        self.assertEqual(result["appointment_datetime"], "2025-05-02T13:00:00Z")
        self.assertEqual(result["location"], "Clinic A - Room 203")
        self.assertEqual(result["reason"], "General Consultation")
        self.assertEqual(result["patient"]["patient_id"], "P12345")
        self.assertEqual(result["patient"]["name"], "John Doe")
        self.assertEqual(result["provider"]["provider_id"], "D67890")
        self.assertEqual(result["provider"]["provider_name"], "Dr Smith")

    def test_parse_multiple_messages(self):
        combined = self.valid_message_1 + "\n" + self.valid_message_2
        messages = combined.strip().split("\nMSH")
        messages = ["MSH" + m if not m.startswith("MSH") else m for m in messages]

        results = [parse_h17_message(msg) for msg in messages]

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["appointment_id"], "123456")
        self.assertEqual(results[1]["appointment_id"], "654321")
        self.assertEqual(results[1]["patient"]["name"], "Arafat Hossain")
        self.assertEqual(results[1]["provider"]["provider_name"], "Dr Khan")

    # -------------------- EDGE CASES --------------------

    def test_missing_sch(self):
        result = parse_h17_message(self.missing_sch)
        self.assertIsNone(result["appointment_id"])
        self.assertIsNone(result["appointment_datetime"])
        self.assertIsNone(result["location"])
        self.assertEqual(result["patient"]["name"], "Alice Smith")
        self.assertEqual(result["provider"]["provider_id"], "D11111")

    def test_missing_pid(self):
        result = parse_h17_message(self.missing_pid)
        self.assertEqual(result["appointment_id"], "777888")
        self.assertEqual(result["location"], "Clinic C - Room 301")
        self.assertEqual(result["patient"], {})
        self.assertEqual(result["provider"]["provider_name"], "Dr Brown")

    def test_empty_fields(self):
        msg = """MSH|^~\\&|EMR|HOSPITAL|RCM|RCMSYSTEM|202505081000||SIU^S12|12351|P|2.3
SCH|123999^F||||||||
PID|1||P55555^^^HOSP^MR||||||
PV1|1|...|"""
        result = parse_h17_message(msg)
        self.assertEqual(result["appointment_id"], "123999")
        self.assertIsNone(result["appointment_datetime"])
        self.assertEqual(result["location"], "")
        self.assertEqual(result["patient"]["patient_id"], "P55555")
        self.assertEqual(result["patient"]["name"], "")
        self.assertEqual(result["provider"], {})

    # -------------------- FAILURE CASES --------------------

    def test_malformed_datetime(self):
        with self.assertRaises(ValueError):
            parse_h17_message(self.malformed_datetime)

    def test_invalid_message_type(self):
        with self.assertRaises(ValueError):
            parse_h17_message(self.invalid_type)


if __name__ == "__main__":
    unittest.main()
