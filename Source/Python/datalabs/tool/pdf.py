''' PDF utility funcions '''
from   datetime import datetime
import pytz

from   cryptography.hazmat.primitives.serialization import pkcs12
from   endesive import pdf


class PDFSigner:
    @classmethod
    def sign(cls, pdf_path, signed_pdf_path, credentials_path, password, recipient=None):
        signature_details = cls._generate_signature_details(recipient)

        unsigned_pdf = cls._read_unsigned_pdf(pdf_path)

        signature = cls._generate_signature(unsigned_pdf, credentials_path, password, signature_details)

        cls._write_signed_pdf(unsigned_pdf, signature, signed_pdf_path)

    @classmethod
    def _generate_signature_details(cls, recipient):
        timezone = pytz.timezone('US/Central')
        current_time = datetime.now(timezone).strftime('%Y%m%d%H%M%S%z')[:-2] + "'00'"
        message = "Download"

        if recipient is not None:
            message += f" by {recipient}"


        return {
            'sigflags': 3,
            'contact': 'DataLabs@ama-assn.org',
            'location': 'Chicago',
            'signingdate': current_time,
            'reason': message,
        }

    @classmethod
    def _read_unsigned_pdf(cls, pdf_path):
        unsigned_pdf = None

        with open(pdf_path, 'br') as pdf_file:
            unsigned_pdf = pdf_file.read()

        return unsigned_pdf

    @classmethod
    def _generate_signature(cls, unsigned_pdf, credentials_path, password, signature_details):

        with open(credentials_path, 'br') as credentials_file:
            credentials = credentials_file.read()

            key, cert, trust_chain_certs = pkcs12.load_key_and_certificates(credentials, password.encode())

        return pdf.cms.sign(unsigned_pdf, signature_details, key, cert, trust_chain_certs, 'sha256')

    @classmethod
    def _write_signed_pdf(cls, unsigned_pdf, signature, signed_pdf_path):
        with open(signed_pdf_path, 'bw') as signed_pdf_file:
            signed_pdf_file.write(unsigned_pdf)
            signed_pdf_file.write(signature)
