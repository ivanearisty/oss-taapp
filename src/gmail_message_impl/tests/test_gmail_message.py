"""Tests for GmailMessage implementation.

This module contains comprehensive tests for the GmailMessage class,
covering message parsing, property access, error handling, and edge cases.
"""

import base64
import email
from email.message import EmailMessage
import pytest
from gmail_message_impl._impl import GmailMessage


class TestGmailMessage:
    """Test cases for the GmailMessage class."""

    def test_basic_message_creation(self):
        """Test creating a GmailMessage with valid data."""
        # Create a simple email message
        email_content = (
            "From: sender@example.com\r\n"
            "To: recipient@example.com\r\n" 
            "Subject: Test Subject\r\n"
            "Date: Wed, 30 Jul 2025 10:30:00 +0000\r\n"
            "\r\n"
            "This is the message body."
        )
        
        # Encode as Gmail would
        encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()
        
        # Create GmailMessage instance
        message = GmailMessage(msg_id="test123", raw_data=encoded_data)
        
        # Verify properties
        assert message.id == "test123"
        assert message.from_ == "sender@example.com"
        assert message.to == "recipient@example.com"
        assert message.subject == "Test Subject"
        assert message.date == "07/30/2025"
        assert message.body == "This is the message body."

    def test_message_with_encoded_subject(self):
        """Test message with RFC 2047 encoded subject."""
        email_content = (
            "From: sender@example.com\r\n"
            "To: recipient@example.com\r\n"
            "Subject: =?UTF-8?B?VGVzdCBTdWJqZWN0IGVuY29kZWQ=?=\r\n"
            "Date: Wed, 30 Jul 2025 10:30:00 +0000\r\n"
            "\r\n"
            "Message body"
        )
        
        encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()
        message = GmailMessage(msg_id="test456", raw_data=encoded_data)
        
        assert message.subject == "Test Subject encoded"

    def test_multipart_message(self):
        """Test parsing a multipart message."""
        # Create a multipart email
        email_msg = EmailMessage()
        email_msg["From"] = "sender@example.com"
        email_msg["To"] = "recipient@example.com"
        email_msg["Subject"] = "Multipart Test"
        email_msg["Date"] = "Wed, 30 Jul 2025 10:30:00 +0000"
        
        # Add text part
        email_msg.set_content("This is the plain text body.")
        
        # Add HTML part
        email_msg.add_alternative(
            "<html><body><p>This is the HTML body.</p></body></html>",
            subtype="html"
        )
        
        # Encode the message
        raw_email = email_msg.as_bytes()
        encoded_data = base64.urlsafe_b64encode(raw_email).decode()
        
        message = GmailMessage(msg_id="multipart123", raw_data=encoded_data)
        
        assert message.id == "multipart123"
        assert message.from_ == "sender@example.com"
        assert "This is the plain text body." in message.body

    def test_invalid_base64_data(self):
        """Test handling of invalid base64 data."""
        invalid_data = "This is not valid base64!"
        
        # Should not raise an exception, but handle gracefully
        message = GmailMessage(msg_id="invalid123", raw_data=invalid_data)
        
        assert message.id == "invalid123"
        assert message.subject == "Error Parsing Message"
        assert message.from_ == "Unknown Sender"

    def test_empty_message_fields(self):
        """Test message with missing fields."""
        email_content = "\r\n\r\nJust a body, no headers."
        
        encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()
        message = GmailMessage(msg_id="empty123", raw_data=encoded_data)
        
        assert message.id == "empty123"
        assert message.from_ == ""
        assert message.to == ""
        assert message.subject == ""
        assert message.date == "Unknown Date"
        assert message.body == "\r\nJust a body, no headers."

    def test_date_parsing_fallback(self):
        """Test date parsing with invalid date format."""
        email_content = (
            "From: sender@example.com\r\n"
            "Date: Invalid Date Format\r\n"
            "\r\n"
            "Message body"
        )
        
        encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()
        message = GmailMessage(msg_id="baddate123", raw_data=encoded_data)
        
        # Should fallback to raw date string
        assert message.date == "Invalid Date Format"

    def test_subject_without_encoding(self):
        """Test subject that doesn't need RFC 2047 decoding."""
        email_content = (
            "From: sender@example.com\r\n"
            "Subject: Plain Subject Line\r\n"
            "\r\n"
            "Message body"
        )
        
        encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()
        message = GmailMessage(msg_id="plain123", raw_data=encoded_data)
        
        assert message.subject == "Plain Subject Line"

    def test_message_with_attachment(self):
        """Test multipart message with attachment (should extract text body)."""
        # Create multipart message with attachment
        email_msg = EmailMessage()
        email_msg["From"] = "sender@example.com"
        email_msg["Subject"] = "Message with Attachment"
        email_msg["Date"] = "Wed, 30 Jul 2025 10:30:00 +0000"
        
        # Set main text content
        email_msg.set_content("This is the main message body.")
        
        # Add an attachment
        email_msg.add_attachment(
            b"fake attachment data",
            maintype="application",
            subtype="octet-stream",
            filename="attachment.txt"
        )
        
        raw_email = email_msg.as_bytes()
        encoded_data = base64.urlsafe_b64encode(raw_email).decode()
        
        message = GmailMessage(msg_id="attach123", raw_data=encoded_data)
        
        # Should extract the main text body, not the attachment
        assert "This is the main message body." in message.body
        assert "fake attachment data" not in message.body

    def test_message_body_encoding(self):
        """Test message body with non-UTF-8 encoding."""
        # Create message with Latin-1 encoding
        body_text = "Café and naïve"
        email_content = (
            "From: sender@example.com\r\n"
            "Subject: Encoding Test\r\n"
            "Content-Type: text/plain; charset=iso-8859-1\r\n"
            "\r\n"
        ).encode('utf-8') + body_text.encode('iso-8859-1')
        
        encoded_data = base64.urlsafe_b64encode(email_content).decode()
        message = GmailMessage(msg_id="encoding123", raw_data=encoded_data)
        
        # Should handle the encoding gracefully
        assert message.id == "encoding123"
        assert message.subject == "Encoding Test"
        # Body should be decoded (may have replacement characters for encoding issues)
        assert len(message.body) > 0

    def test_completely_malformed_email(self):
        """Test with completely malformed email data."""
        malformed_data = "Not an email at all!"
        encoded_data = base64.urlsafe_b64encode(malformed_data.encode()).decode()
        
        message = GmailMessage(msg_id="malformed123", raw_data=encoded_data)
        
        # Should handle gracefully with error message
        assert message.id == "malformed123"
        assert message.subject == "Error Parsing Message"
        assert message.from_ == "Unknown Sender"

    def test_message_without_plain_text_body(self):
        """Test multipart message without plain text part."""
        email_msg = EmailMessage()
        email_msg["From"] = "sender@example.com"
        email_msg["Subject"] = "HTML Only"
        
        # Add only HTML content, no plain text
        email_msg.set_content(
            "<html><body><h1>HTML Only Message</h1></body></html>",
            subtype="html"
        )
        
        raw_email = email_msg.as_bytes()
        encoded_data = base64.urlsafe_b64encode(raw_email).decode()
        
        message = GmailMessage(msg_id="htmlonly123", raw_data=encoded_data)
        
        # Should indicate no plain text body found
        assert "<h1>HTML Only Message</h1>" in message.body
