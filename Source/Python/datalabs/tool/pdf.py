from   datetime import datetime
import pytz

from   cryptography.hazmat import backends
from   cryptography.hazmat.primitives.serialization import pkcs12
from   endesive import pdf


def sign(pdf_path, signed_pdf_path, credentials_path, password):
    timezone = pytz.timezone('US/Central')
    current_time = datetime.now(timezone).strftime('%Y%m%d%H%M%S%z')[:-2] + "'00'"

    signature_details = {
        'sigflags': 3,
        'contact': 'DataLabs@ama-assn.org',
        'location': 'Chicago',
        'signingdate': current_time,
        'reason': 'API Download',
    }

    with open(pdf_path, 'br') as pdf_file:
        unsigned_pdf = pdf_file.read()

    with open(credentials_path, 'br') as credentials_file:
        credentials = credentials_file.read()

        key, cert, trust_chain_certs = pkcs12.load_key_and_certificates(credentials, password.encode())  # , backends.default_backend())

    signed_pdf = pdf.cms.sign(unsigned_pdf, signature_details, key, cert, trust_chain_certs, 'sha256')

    with open(signed_pdf_path, 'bw') as signed_pdf_file:
        signed_pdf_file.write(unsigned_pdf)
        signed_pdf_file.write(signed_pdf)
