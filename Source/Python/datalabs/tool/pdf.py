''' PDF utility funcions '''
from   datetime import datetime
import pytz

from   cryptography.hazmat.primitives.serialization import pkcs12
import endesive.pdf


class PDFSigner:
    # pylint: disable=too-many-arguments
    @classmethod
    def sign(
        cls,
        pdf: 'str or file-like',
        signed_pdf: 'str or file-like',
        credentials: 'str or file-like',
        password: str,
        recipient: str=None
    ):
        signature_details = cls._generate_signature_details(recipient)

        unsigned_pdf = cls._read_pdf(pdf)

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
    def _read_pdf(cls, pdf):
        unsigned_pdf = None

        if hasattr(pdf, 'readable'):
            unsigned_pdf = pdf.read()
        else:
            unsigned_pdf = cls._open_and_read(pdf)

        return unsigned_pdf

    @classmethod
    def _generate_signature(cls, unsigned_pdf, pkcs12_credentials, password, signature_details):
        pkcs12_file = pkcs12_credentials

        if  hasattr(pkcs12_credentials, 'readable'):
            credentials = pkcs12_file.read()
        else:
            credentials = cls._open_and_read(pkcs12_credentials)

        key, cert, trust_chain_certs = pkcs12.load_key_and_certificates(credentials, password.encode())

        return endesive.pdf.cms.sign(unsigned_pdf, signature_details, key, cert, trust_chain_certs, 'sha256')

    @classmethod
    def _write_signed_pdf(cls, unsigned_pdf, signature, signed_pdf):
        if hasattr(signed_pdf, 'readable'):
            signed_pdf.write(unsigned_pdf)
            signed_pdf.write(signature)
        else:
            cls._open_and_write(signed_pdf, [unsigned_pdf, signature])

    @classmethod
    def _open_and_read(cls, filename):
        contents = None

        with open(filename, 'br') as file:
            contents = file.read()

        return contents

    @classmethod
    def _open_and_write(cls, filename, contents):
        with open(filename, 'bw') as file:
            for item in contents:
                file.write(item)
