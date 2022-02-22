from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers

def sign(pdf_path, signed_pdf_path, key_path, cert_path, password):
    passphrase = None
    if password is not None:
        passphrase = password.encode()

    signer = signers.SimpleSigner.load(key_path, cert_path, key_passphrase=passphrase)
    with open(signed_pdf_path, 'bw') as signed_pdf:
        with open(pdf_path, 'br') as pdf:
            writer = IncrementalPdfFileWriter(pdf)
            signature = signers.PdfSignatureMetadata(
                field_name='Signature',
                name="American Medical Association",
                md_algorithm="sha256"
            )

            signers.sign_pdf(writer, signature, signer=signer)

            writer.write(signed_pdf)
# from   asn1crypto import keys, x509
# from   cryptography import x509
# import cryptography.hazmat.primitives.serialization as rsa
# import endesive.signer as signer
#
# def sign(pdf_path, signed_pdf_path, key_path, cert_path, password):
#     key = None
#     cert = None
#     pdf = None
#     signed_pdf = None
#
#     with open(key_path, 'br') as key_file:
#         key = key_file.read()
#
#     # rsa.load_pem_private_key(key, password)
#
#     with open(cert_path, 'br') as cert_file:
#         cert = cert_file.read()
#
#     # x509.load_pem_x509_certificate(cert)
#
#     with open(pdf_path, 'br') as pdf_file:
#         pdf = pdf_file.read()
#
#
#
#     # signed_pdf = signer.sign(pdf, keys.ECPrivateKey.load(key), x509.Certificate.load(cert), [], "sha256")
#     # signed_pdf = signer.sign(pdf, crypto.load_der_private_key(key, password), crypto.load_der_public_key(cert), [], "sha256")
#     signature = signer.sign(pdf, rsa.load_pem_private_key(key, password), x509.load_pem_x509_certificate(cert), [], "sha256")
#
#     with open(signed_pdf_path, 'bw') as signed_pdf_file:
#         signed_pdf_file.write(pdf)
#         signed_pdf_file.write(signature)
