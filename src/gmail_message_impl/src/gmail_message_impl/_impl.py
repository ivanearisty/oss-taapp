r"""Gmail Message Implementation - Concrete message implementation for Gmail.

This module provides the GmailMessage class, which implements the Message protocol
for Gmail messages. It handles Gmail-specific message parsing, email decoding,
and content extraction from Gmail API message data.

The implementation handles:
- Base64 URL-safe decoding of Gmail message data
- RFC 2047 subject line decoding
- Date parsing and formatting
- Multipart message body extraction
- Graceful error handling for malformed messages
"""

import base64
import email
import email.header
import email.utils
from email.message import Message as EmailMessage

# Import the protocol
import message


class GmailMessage(message.Message):
    """Concrete implementation of the Message protocol for Gmail messages.

    This class provides a complete implementation of the Message protocol specifically
    designed to work with Gmail API message data. It handles the parsing and decoding
    of Gmail messages from their raw base64url-encoded format.

    Features:
        - Decodes base64url-encoded Gmail message data
        - Parses RFC 2822 email format
        - Handles RFC 2047 encoded subject lines
        - Extracts plain text body from multipart messages
        - Formats dates in MM/DD/YYYY format
        - Provides graceful error handling for malformed data

    Attributes:
        _id (str): The unique message identifier from Gmail
        _raw_data (str): The original base64url-encoded message data
        _parsed (EmailMessage): The parsed email message object

    """

    # Constants for binary data detection
    MAX_PRINTABLE_ASCII = 126  # ASCII value of '~', last printable character
    BINARY_THRESHOLD_RATIO = 0.5  # Threshold for non-printable character ratio

    # ASCII control character values (allowed in text)
    TAB_ASCII = 9
    NEWLINE_ASCII = 10
    CARRIAGE_RETURN_ASCII = 13
    SPACE_ASCII = 32

    # Error messages and defaults
    ERROR_PARSING_MESSAGE = "Error Parsing Message"
    UNKNOWN_SENDER = "Unknown Sender"
    UNKNOWN_RECIPIENT = "Unknown Recipient"
    UNKNOWN_DATE = "Unknown Date"

    # Date formatting
    DATE_FORMAT = "%m/%d/%Y"

    # Email parsing constants
    RFC2047_ENCODING_MARKER = "=?"
    DEFAULT_CHARSET = "utf-8"
    TEXT_PLAIN_CONTENT_TYPE = "text/plain"
    CONTENT_DISPOSITION_HEADER = "Content-Disposition"
    ATTACHMENT_DISPOSITION = "attachment"

    # Body extraction error messages
    NON_BYTES_PAYLOAD_TEXT_PART = "[Non-bytes payload found in text/plain part]"
    COULD_NOT_DECODE_BODY_PART = "[Could not decode body part]"
    NO_PLAIN_TEXT_BODY = "[No plain text body found]"
    NON_BYTES_PAYLOAD = "[Non-bytes payload found]"
    COULD_NOT_DECODE_BODY = "[Could not decode body]"

    # Email body line start markers
    EMAIL_BODY_LINE_STARTS = ("\r\n", "\n")

    def __init__(self, msg_id: str, raw_data: str) -> None:
        """Initialize GmailMessage instance.

        Args:
            msg_id: The unique ID of the message.
            raw_data: The raw, base64url encoded email data.

        """
        self._id = msg_id
        self._raw_data = raw_data
        # Decode the raw data and parse it into an EmailMessage object
        try:
            decoded_bytes = base64.urlsafe_b64decode(raw_data.encode("utf-8"))
            self._parsed: EmailMessage = email.message_from_bytes(
                decoded_bytes,
            )

            # Check if we have essentially empty or invalid email data
            # email.message_from_bytes is very lenient and won't raise errors for invalid data
            # but will create an EmailMessage with missing headers
            payload = self._parsed.get_payload()
            if (
                not decoded_bytes  # Empty decoded data
                or (
                    not any(self._parsed.keys())  # No headers AND
                    and (
                        not payload  # No payload OR
                        or (isinstance(payload, str) and not payload.startswith(self.EMAIL_BODY_LINE_STARTS))
                    )
                )  # Payload doesn't start with newlines (not proper email body)
                or self._is_binary_garbage(decoded_bytes)
            ):  # Binary garbage that shouldn't be parsed as email
                # Handle invalid email data gracefully
                # Create a dummy EmailMessage to avoid subsequent attribute errors
                self._parsed = EmailMessage()
                self._parsed["Subject"] = self.ERROR_PARSING_MESSAGE
                self._parsed["From"] = self.UNKNOWN_SENDER
                self._parsed["To"] = self.UNKNOWN_RECIPIENT
                self._parsed["Date"] = self.UNKNOWN_DATE

        except (TypeError, ValueError):
            # Handle potential decoding or parsing errors gracefully
            # Create a dummy EmailMessage to avoid subsequent attribute errors
            self._parsed = EmailMessage()
            self._parsed["Subject"] = self.ERROR_PARSING_MESSAGE
            self._parsed["From"] = self.UNKNOWN_SENDER
            self._parsed["To"] = self.UNKNOWN_RECIPIENT
            self._parsed["Date"] = self.UNKNOWN_DATE

    def _is_binary_garbage(self, data: bytes) -> bool:
        """Check if data appears to be binary garbage rather than text/email content."""
        if not data:
            return False

        # Try to decode as UTF-8 first - if it's valid UTF-8, it's probably text, not garbage
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            pass
        else:
            # If UTF-8 decoding succeeds, it's likely text content, not binary garbage
            return False

        # If UTF-8 decoding fails, check for binary patterns
        # If the data contains a lot of non-printable characters, it's likely binary garbage
        # Use a higher threshold since we're now only checking non-UTF-8 data
        non_printable_count = 0
        for byte_val in data:
            # Consider bytes outside of printable ASCII range as non-printable
            # Allow some common control chars like \r, \n, \t
            if (
                byte_val < self.SPACE_ASCII and byte_val not in (self.TAB_ASCII, self.NEWLINE_ASCII, self.CARRIAGE_RETURN_ASCII)
            ) or byte_val > self.MAX_PRINTABLE_ASCII:  # \t, \n, \r
                non_printable_count += 1

        return (non_printable_count / len(data)) > self.BINARY_THRESHOLD_RATIO  # Higher threshold for non-UTF-8 data

    @property
    def id(self) -> str:
        """Returns the unique message ID."""
        return self._id

    @property
    def from_(self) -> str:
        """Returns the sender's email address, or empty string if not found."""
        return self._parsed.get("From", "")

    @property
    def to(self) -> str:
        """Returns the recipient's email address, or empty string if not found."""
        return self._parsed.get("To", "")

    @property
    def date(self) -> str:
        """Returns the message date formatted as MM/DD/YYYY, or the raw date string if parsing fails."""
        raw_date = self._parsed.get("Date", "")
        if not raw_date:
            return self.UNKNOWN_DATE
        try:
            # Attempt to parse the date string into a datetime object
            parsed_dt = email.utils.parsedate_to_datetime(raw_date)
            # Format the datetime object
            return parsed_dt.strftime(self.DATE_FORMAT)
        except (TypeError, ValueError):
            # Fallback to the raw date string if parsing fails
            return raw_date

    @property
    def subject(self) -> str:
        """Returns the message subject, decoding if necessary."""
        subject_header = self._parsed.get("Subject", "")
        if not subject_header:
            return ""

        # Convert Header object to string if necessary
        if hasattr(subject_header, "__str__"):
            subject_header = str(subject_header)

        # Attempt to decode RFC 2047 encoded words
        try:
            # Check if it looks like an encoded header to avoid unnecessary processing
            if self.RFC2047_ENCODING_MARKER not in subject_header:
                return subject_header  # Return plain string directly

            decoded_parts = email.header.decode_header(subject_header)
            subject_str = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    subject_str += part.decode(encoding or self.DEFAULT_CHARSET, errors="replace")
                else:
                    subject_str += part  # Append decoded string part

            return subject_str if subject_str else subject_header # noqa: TRY300
        except (UnicodeDecodeError, LookupError, ValueError, AttributeError):
            # Fallback to the raw header if any decoding error occurs
            return subject_header

    @property
    def body(self) -> str:
        """Extracts and returns the plain text body of the message."""
        body_content = ""
        if self._parsed.is_multipart():
            for part in self._parsed.walk():
                content_type = part.get_content_type()
                content_disposition = part.get(self.CONTENT_DISPOSITION_HEADER, "")

                # Look for plain text parts that are not attachments
                if content_type == self.TEXT_PLAIN_CONTENT_TYPE and self.ATTACHMENT_DISPOSITION not in content_disposition:
                    try:
                        # Decode payload, handling potential encoding issues
                        payload = part.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            charset = part.get_content_charset() or self.DEFAULT_CHARSET
                            body_content = payload.decode(charset, errors="replace")
                            # Found the plain text body, no need to look further
                            break
                        body_content = self.NON_BYTES_PAYLOAD_TEXT_PART
                        break
                    except (UnicodeDecodeError, LookupError, AttributeError, TypeError):
                        body_content = self.COULD_NOT_DECODE_BODY_PART
                        break
            else:
                # If no text/plain part found after walking
                body_content = self.NO_PLAIN_TEXT_BODY
        else:
            # If it's not multipart, get the main payload
            try:
                payload = self._parsed.get_payload(decode=True)
                if isinstance(payload, bytes):
                    charset = self._parsed.get_content_charset() or self.DEFAULT_CHARSET
                    body_content = payload.decode(charset, errors="replace")
                else:
                    # Handle non-bytes payload
                    body_content = self.NON_BYTES_PAYLOAD
            except (UnicodeDecodeError, LookupError, AttributeError):
                body_content = self.COULD_NOT_DECODE_BODY

        return body_content
