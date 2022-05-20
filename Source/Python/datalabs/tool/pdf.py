''' PDF utility funcions '''
from   datetime import datetime
import pytz

from   cryptography.hazmat.primitives.serialization import pkcs12
import endesive.pdf


class PDFSigner:
    # pylint: disable=too-many-arguments
    @classmethod
    def sign(cls, pdf: 'str or file-like', signed_pdf: 'str or file-like', credentials: 'str or file-like', password, recipient=None):
        signature_details = cls._generate_signature_details(recipient)

        unsigned_pdf = cls._read_unsigned_pdf(pdf)

        signature = cls._generate_signature(unsigned_pdf, credentials, password, signature_details)

        cls._write_signed_pdf(unsigned_pdf, signature, signed_pdf)

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
    def _read_unsigned_pdf(cls, pdf):
        pdf_file = pdf
        unsigned_pdf = None

        if not hasattr(pdf, 'readable'):
            pdf_file = open(pdf, 'br')

        unsigned_pdf = pdf_file.read()

        if not hasattr(pdf, 'readable'):
            pdf_file.close()

        return unsigned_pdf

    @classmethod
    def _generate_signature(cls, unsigned_pdf, pkcs12_credentials, password, signature_details):
        pkcs12_file = pkcs12_credentials

        if not hasattr(pkcs12_credentials, 'readable'):
            pkcs12_file = open(pkcs12_credentials, 'br')

        credentials = pkcs12_file.read()

        if not hasattr(pkcs12_credentials, 'readable'):
            pkcs12_file.close()

        key, cert, trust_chain_certs = pkcs12.load_key_and_certificates(credentials, password.encode())

        return endesive.pdf.cms.sign(unsigned_pdf, signature_details, key, cert, trust_chain_certs, 'sha256')

    @classmethod
    def _write_signed_pdf(cls, unsigned_pdf, signature, signed_pdf):
        signed_pdf_file = signed_pdf

        if not hasattr(signed_pdf, 'readable'):
            signed_pdf_file = open(signed_pdf, 'bw')

        signed_pdf_file.write(unsigned_pdf)
        signed_pdf_file.write(signature)

        if not hasattr(signed_pdf, 'readable'):
            signed_pdf_file.close()
