''' OneView database model module. '''
from datalabs.model.masterfile.oneview.content import \
    BASE, \
    Physician, \
    ResidencyProgram, \
    ResidencyProgramPersonnelMember, \
    ResidencyProgramInstitution, \
    Business, \
    Provider, \
    ProviderAffiliation, \
    CredentialingCustomer, \
    CredentialingOrder, \
    ZipCode, \
    County, \
    AreaCode, \
    Census, \
    CoreBasedStatisticalAreaMelissa, \
    ZipCodeCoreBasedStatisticalArea, \
    MetropolitanStatisticalArea, \
    HistoricalResident, \
    IqviaUpdate, \
    CredentialingCustomerInstitution, \
    CredentialingCustomerBusiness, \
    ResidencyProgramPhysician, \
    CorporateParentBusiness, \
    SubsidiaryOwnerBusiness, \
    CredentialingProduct, \
    TypeOfPractice, \
    PresentEmployment, \
    MajorProfessionalActivity, \
    FederalInformationProcessingStandardCounty, \
    CoreBasedStatisticalArea, \
    Specialty, \
    State, \
    ClassOfTradeClassification, \
    ClassOfTradeSpecialty, \
    ClassOfTradeFacilityType, \
    ProviderAffiliationGroup, \
    ProviderAffiliationType, \
    ProfitStatus, \
    OwnerStatus, \
    MedicalSchool
from datalabs.model.masterfile.oneview.user_interface import \
    PHYSICIAN_MATERIALIZED_VIEW, \
    PHYSICIAN_PROVIDER_MATERIALIZED_VIEW, \
    FLATTENED_PROVIDER_MATERIALIZED_VIEW, \
    FLATTENED_PHYSICIAN_MATERIALIZED_VIEW
from datalabs.model.masterfile.oneview.restricted import PHYSICIAN_DATA_VIEW
