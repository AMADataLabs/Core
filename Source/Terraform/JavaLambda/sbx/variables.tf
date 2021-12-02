variable "project" {
   description  = "Name of the project used primarily in resource names."
   type = string
   default = "CPT-API"
}

variable "contact" {
   description  = "Email of the contact for this app stack."
   type = string
   default = "DataLabs@ama-assn.org"
}

variable "owner" {
   description  = "Name of the owner of this application."
   type = string
   default = "Data Labs"
}

variable "budget_code" {
   description  = "Budget code for accounting purposes."
   type = string
   default = "PBW"
}

variable "accounts" {
   description  = "AWS accounts into which this app stack is deployed."
   default = {
     sbx = "644454719059"
     dev = "191296302136"
     tst = "194221139997"
     stg = "340826698851"
     prd = "285887636563"
   }
}

variable "region" {
   description  = "AWS region into which this app stack is deployed."
   type = string
   default = "us-east-1"
}

variable "days_to_recover" {
   description  = "AWS Secrets Manager Recovery Window in Days"
   type = number
   default = 0
}

variable "s3_lambda_bucket_template" {
   description  = "S3 bucket where Lambda function code artifact is stored."
   type = string
   default = "ama-%%environment%%-datalake-lambda-us-east-1"
}

variable "s3_lambda_key" {
   description  = "CPT API Lambda function code artifact name."
   type = string
   default = "CPT/ETL.zip"
}

variable "runtime" {
   description  = "Lambda function runtime."
   type = string
   default = "python3.7"
}

variable "endpoint_lambda_memory_size" {
   description  = "API endpoint Lambda function memory size in MB."
   type = number
   default = 3072
}

variable "endpoint_lambda_timeout" {
   description  = "API endpoint Lambda function timeout in seconds."
   type = number
   default = 60
}

variable "authorizer_lambda_memory_size" {
   description  = "Authorizer Lambda function memory size in MB."
   type = number
   default = 1024
}

variable "authorizer_lambda_timeout" {
   description  = "Authorizer Lambda function timeout in seconds."
   type = number
   default = 15
}

variable "etl_lambda_memory_size" {
   description  = "ETL Lambda function memory size in MB."
   type = number
   default = 3072
}

variable "etl_lambda_timeout" {
   description  = "ETL Lambda function timeout in seconds."
   type = number
   default = 600
}

variable "router_lambda_memory_size" {
   description  = "Router Lambda function memory size in MB."
   type = number
   default = 1024
}

variable "router_lambda_timeout" {
   description  = "Router Lambda function timeout in seconds."
   type = number
   default = 20
}

variable "s3_processed_data_bucket_template" {
   description  = "Data Lake S3 bucket where processed data is stored."
   type = string
   default = "ama-%%environment%%-datalake-processed-data-us-east-1"
}

variable "s3_data_base_path" {
   description  = "Base path in the Data Lake S3 bucket where CPT API data is located."
   type = string
   default = "AMA/CPT"
}

variable "passport_url" {
   description  = "URL to AMA Passport authorization service."
   type = string
   default = "https://amapassport-staging.ama-assn.org/auth/entitlements/list/CPTAPI"
}

variable "raw_data_files" {
   description  = "Names of the raw CPT data files."
   type = string
   default = "ETL_TRIGGER,standard/SHORTU.txt,standard/MEDU.txt,standard/LONGULT.txt,standard/MODUL.txt,standard/Consumer Friendly Descriptors/ConsumerDescriptor.txt,standard/Clinician Descriptors/ClinicianDescriptor.txt,standard/Proprietary Laboratory Analyses (PLA) Codes/CPTPLA,CPT Link/history/Deleted_DTK_tab.txt,CPT Link/history/HistoryModifiers_DTK_tab.txt,CPT Link/history/History_DTK_tab.txt"
}

variable "release_schedule" {
   description  = "CPT release schedule."
   type = string
   default = "{\"ANNUAL\": [\"1-Sep\", \"1-Jan\"], \"Q1\": [\"1-Jan\", \"1-Apr\"], \"Q2\": [\"1-Apr\", \"1-Jul\"], \"Q3\": [\"1-Jul\", \"1-Oct\"], \"Q4\": [\"1-Oct\", \"1-Jan\"]}"
}

variable "raw_data_parsers" {
   description  = "Parser classes for the raw CPT data files."
   type = string
   default = "datalabs.curate.parse.CSVParser,datalabs.curate.parse.PassThroughParser,datalabs.curate.cpt.descriptor.ShortDescriptorParser,datalabs.curate.cpt.descriptor.MediumDescriptorParser,datalabs.curate.cpt.descriptor.LongDescriptorParser,datalabs.curate.cpt.modifier.ModifierParser,datalabs.curate.cpt.descriptor.ConsumerDescriptorParser,datalabs.curate.cpt.descriptor.ClinicianDescriptorParser,datalabs.curate.cpt.pla.PLAParser,datalabs.curate.cpt.link.history.DeletionHistoryParser,datalabs.curate.cpt.link.history.ModifierHistoryParser,datalabs.curate.cpt.link.history.CodeHistoryParser"
}

variable "converted_data_files" {
   description  = "Names of the converted CPT data files."
   type = string
   default = "standard/release.csv,ETL_TRIGGER,standard/SHORTU.csv,standard/MEDU.csv,standard/LONGULT.csv,standard/MODUL.csv,standard/Consumer Friendly Descriptors/ConsumerDescriptor.csv,standard/Clinician Descriptors/ClinicianDescriptor.csv,standard/Proprietary Laboratory Analyses (PLA) Codes/CPTPLA.csv,CPT Link/history/Deleted_DTK_tab.csv,CPT Link/history/HistoryModifiers_DTK_tab.csv,CPT Link/history/History_DTK_tab.csv"
}

variable "raw_csv_files" {
   description  = "Names of the converted CPT data files."
   type = string
   default = "standard/release.csv,standard/SHORTU.csv,standard/MEDU.csv,standard/LONGULT.csv,standard/MODUL.csv,standard/Consumer Friendly Descriptors/ConsumerDescriptor.csv,standard/Clinician Descriptors/ClinicianDescriptor.csv,standard/Proprietary Laboratory Analyses (PLA) Codes/CPTPLA.csv,CPT Link/history/Deleted_DTK_tab.csv,CPT Link/history/HistoryModifiers_DTK_tab.csv,CPT Link/history/History_DTK_tab.csv"
}


variable "pdf_files" {
   description  = "Names of the converted CPT data files."
   type = string
   default = "CPT Link Release Notes *.pdf,standard/AnesthesiaGuidelines.pdf,standard/AppendixB.pdf,standard/AppendixN.pdf,standard/AppendixO.pdf,standard/AppendixQ.pdf,standard/AppendixR.pdf,standard/CategoryIIGuidelines.pdf,standard/CategoryIIIGuidelines.pdf,standard/CPT * README.pdf,standard/EvalManagementGuidelines.pdf,standard/MedicineGuidelines.pdf,standard/PathLabGuidelines.pdf,standard/RadiologyGuidelines.pdf,standard/Clinician Descriptors/* Clinician Descriptors README.pdf,standard/Consumer Friendly Descriptors/* Consumer Friendly Descriptors README.pdf,standard/SurgeryGuidelines.pdf"
}

variable "pdf_bundle_file" {
   description  = "Name of the zip archive file containing the CPT PDFs."
   type = string
   default = "pdfs.zip"
}

variable "spec_description" {
   description  = "The API specification description"
   type = string
   default = "CPT API Phase I"
}

variable "db_instance_class" {
   description  = "RDS instance class."
   type = string
   default = "db.t2.micro"
}

variable "database_username" {
  type = string
  description = "The master username for the RDS instance"
  default = "cptadmin"
}

variable "db_instance_allocated_storage" {
   description  = "RDS instance allocated storage size in GB."
   type = number
   default = 20
}

variable "max_allocated_storage" {
   description  = "RDS instance allocated storage maximum size in GB."
   type = number
   default = 1000
}

variable "db_engine_version" {
   description  = "RDS instance engine version."
   type = string
   default = "11.10"
}

variable "enable_multi_az" {
   description  = "Whether to enable multi-availability-zone deployment for the RDS instance."
   type = bool
   default = false
}

variable "ssl_policy" {
   description = "SSL Policy Variable"
   type = string
   default = "ELBSecurityPolicy-2020-10"
}

variable "s3_url_duration" {
   description = "SSL Policy Variable"
   type = string
   default = "600"
}

variable "private_certificate_arn" {
    description = "ARN of certificate for *.cptapi.local"
    type        = string
    default     = "arn:aws:acm:us-east-1:644454719059:certificate/1e7b94d2-e53b-4ff6-8825-bce758b3a059"
}

variable "public_certificate_arn" {
    description = "ARN of certificate for AMA-wide CNAME"
    type        = string
    default     = "arn:aws:acm:us-east-1:644454719059:certificate/e3976dc3-ad98-4303-b357-557e364ae3ce"
}

variable "private_cname_template" {
    description = "Private CNAME of the API Gateway load balancer"
    type        = string
    default     = "cpt-api-%%environment%%.cptapi.local"
}

variable "public_cname_template" {
    description = "Public CNAME of the API Gateway load balancer"
    type        = string
    default     = "cpt-data-api-%%environment%%.amaaws.org"
}

variable "dynamodb_config_table_template" {
    description = "timeout in seconds"
    type        = string
    default     = "DataLake-configuration-%%environment%%"
}
