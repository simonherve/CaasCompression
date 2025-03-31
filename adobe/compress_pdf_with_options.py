"""
 Copyright 2024 Adobe
 All Rights Reserved.

 NOTICE: Adobe permits you to use, modify, and distribute this file in
 accordance with the terms of the Adobe license agreement accompanying it.
"""

import logging
import os
from datetime import datetime
import json

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.config.client_config import ClientConfig
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.compress_pdf_job import CompressPDFJob
from adobe.pdfservices.operation.pdfjobs.params.compress_pdf.compress_pdf_params import CompressPDFParams
from adobe.pdfservices.operation.pdfjobs.params.compress_pdf.compression_level import CompressionLevel
from adobe.pdfservices.operation.pdfjobs.result.compress_pdf_result import CompressPDFResult

# Initialize the logger
logging.basicConfig(level=logging.INFO)


#
# This sample illustrates how to compress PDF by reducing the size of the PDF file.
#
# Refer to README.md for instructions on how to run the samples.
#
class CompressPDF:
    def __init__(self):
        try:
            #file = open('src/resources/compressPDFInput.pdf', 'rb')
            #file = open("../input/Bagage_Impact_Carbone_by_CA_Septembre_2024.pdf", "rb")
            file = open("../input/test_file_2.pdf", "rb")
            input_stream = file.read()
            file.close()

            # Initial setup, create credentials instance
            credentials = ServicePrincipalCredentials(
                client_id=os.getenv('PDF_SERVICES_CLIENT_ID'),
                client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET')
            )

            # Creates client config instance with custom time-outs
            client_config: ClientConfig = ClientConfig(
                connect_timeout=10000,
                read_timeout=40000,
            )

            # Creates a PDF Services instance
            pdf_services = PDFServices(
                credentials=credentials,
                client_config=client_config,
            )

            # Creates an asset(s) from source file(s) and upload
            input_asset = pdf_services.upload(input_stream=input_stream,
                                              mime_type=PDFServicesMediaType.PDF)
            
            # Create parameters for the job
            compress_pdf_params = CompressPDFParams(compression_level=CompressionLevel.HIGH)

            # Creates a new job instance
            compress_pdf_job = CompressPDFJob(
                input_asset=input_asset,
                compress_pdf_params=compress_pdf_params
            )

            # Submit the job and gets the job result
            location = pdf_services.submit(compress_pdf_job)
            pdf_services_response = pdf_services.get_job_result(location, CompressPDFResult)

            # Get content from the resulting asset(s)
            result_asset: CloudAsset = pdf_services_response.get_result().get_asset()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)

            # Creates an output stream and copy stream asset's content to it
            output_file_path = self.create_output_file_path()
            with open(output_file_path, "wb") as file:
                file.write(stream_asset.get_input_stream())

        except (ServiceApiException, ServiceUsageException, SdkException) as e:
            logging.exception(f'Exception encountered while executing operation: {e}')

    # Generates a string containing a directory structure and file name for the output file
    @staticmethod
    def create_output_file_path() -> str:
        now = datetime.now()
        time_stamp = now.strftime("%Y-%m-%dT%H-%M-%S")
        os.makedirs("output/CompressPDF", exist_ok=True)
        return f"output/CompressPDF/compress{time_stamp}_HIGH.pdf"
    
def init_env_var():
    with open("../input/pdfservices-api-credentials.json") as f:
        credential = json.load(f)
        os.environ["PDF_SERVICES_CLIENT_ID"] = credential["client_credentials"]["client_id"]
        os.environ["PDF_SERVICES_CLIENT_SECRET"] = credential["client_credentials"]["client_secret"]


if __name__ == "__main__":
    init_env_var()
    CompressPDF()