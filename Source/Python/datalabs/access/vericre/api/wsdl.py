""" WSDL string constants """
ENTERPRISE_SEARCH_WSDL = """<?xml version="1.0" encoding="UTF-8"?><wsdl:definitions
 xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" name="enterprisesearch"
 targetNamespace="http://myama.com/enterprisesearch/" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
 xmlns:tns="http://myama.com/enterprisesearch/" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <wsdl:types>
    <xsd:schema targetNamespace="http://myama.com/enterprisesearch/">
      <xsd:element name="SearchEnterpriseEntity">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="searchEnterpriseEntityRequest" type="tns:SearchEnterpriseEntityRequestType"/>
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>
      <xsd:element name="SearchEnterpriseEntityResponse">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="searchEnterpriseEntityResponse" type="tns:SearchEnterpriseEntityResponseType"/>
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>
      <xsd:element name="SearchFirstInitialLastNameDOB">
      	<xsd:complexType>
      		<xsd:sequence>

      			<xsd:element name="searchFirstInitialLastNameDOBRequest" type="tns:SearchFirstInitialLastNameDOBRequestType"/>
      		</xsd:sequence>
      	</xsd:complexType>
      </xsd:element>
      <xsd:element name="SearchFirstInitialLastNameDOBResponse">
      	<xsd:complexType>
      		<xsd:sequence>

      			<xsd:element name="searchFirstInitialLastNameDOBResponse" type="tns:SearchFirstInitialLastNameDOBResponseType"/>
      		</xsd:sequence>
      	</xsd:complexType>
      </xsd:element>

      <xsd:complexType name="SearchEnterpriseEntityRequestType">
      	<xsd:sequence>
      		<xsd:element name="fullName" type="xsd:string"  minOccurs="0"/>
      		<xsd:element name="birthDate" type="xsd:string"  minOccurs="0"/>
      		<xsd:element name="address" type="xsd:string"  minOccurs="0"/>
      		<xsd:element name="postCd" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="npiNumber" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="licenceNumber" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="licenseStateCd" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="ecfmgNumber" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="meNumber" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="deaNumber" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="abmsId" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="delegateId" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="delegateType" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="email" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="schoolCode" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="gradYear" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="applicationId" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="searchWidth" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="matchTolerance" type="xsd:string" minOccurs="0"/>
      		<xsd:element name="resultSetMax" type="xsd:string" minOccurs="0"/>
      	</xsd:sequence>
      </xsd:complexType>

      <xsd:complexType name="SearchEnterpriseEntityResponseType">
      	<xsd:sequence>
      		<xsd:element maxOccurs="unbounded" minOccurs="0" name="physicianSearchResponse" type="tns:PhysicianSearchResponseType"/>
      	</xsd:sequence>
      </xsd:complexType>

            <xsd:complexType name="SearchFirstInitialLastNameDOBRequestType">
            	<xsd:sequence>
            		<xsd:element name="firstInitialLastName" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="address" type="xsd:string"/>
            		<xsd:element name="birthDt" type="xsd:string"/>
            		<xsd:element name="postCd" type="xsd:string"/>
					<xsd:element name="applicationId" type="xsd:string"/>
		      		<xsd:element name="searchWidth" type="xsd:string"/>
		      		<xsd:element name="matchTolerance" type="xsd:string"/>
		      		<xsd:element name="resultSetMax" type="xsd:string"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="SearchFirstInitialLastNameDOBResponseType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="physicianSearchResponse" type="tns:PhysicianSearchResponseType"/>
            	</xsd:sequence>
            </xsd:complexType>
            <xsd:element name="SearchFullNameDOB">
            	<xsd:complexType>
            		<xsd:sequence>
            			<xsd:element name="searchFullNameDOBRequest" type="tns:SearchFullNameDOBRequestType"/>
            		</xsd:sequence>
            	</xsd:complexType>
            </xsd:element>
            <xsd:element name="SearchFullNameDOBResponse">
            	<xsd:complexType>
            		<xsd:sequence>

            			<xsd:element name="searchFullNameDOBResponse" type="tns:SearchFullNameDOBResponseType"/>
            		</xsd:sequence>
            	</xsd:complexType>
            </xsd:element>
            <xsd:element name="SearchIndividualByState">
            	<xsd:complexType>
            		<xsd:sequence>

            			<xsd:element name="searchIndividualByStateRequest" type="tns:SearchIndividualByStateRequestType"/>
            		</xsd:sequence>
            	</xsd:complexType>
            </xsd:element>
            <xsd:element name="SearchIndividualByStateResponse">
            	<xsd:complexType>
            		<xsd:sequence>

            			<xsd:element name="searchIndividualByStateResponse" type="tns:SearchIndividualByStateResponseType"/>
            		</xsd:sequence>
            	</xsd:complexType>
            </xsd:element>
            <xsd:element name="SearchByPartyId">
            	<xsd:complexType>
            		<xsd:sequence>

            			<xsd:element name="searchByPartyIdRequest" type="tns:SearchByPartyIdRequestType"/>
            		</xsd:sequence>
            	</xsd:complexType>
            </xsd:element>
            <xsd:element name="SearchByPartyIdResponse">
            	<xsd:complexType>
            		<xsd:sequence>

            			<xsd:element name="searchByPartyIdResponse" type="tns:SearchByPartyIdResponseType"/>
            		</xsd:sequence>
            	</xsd:complexType>
            </xsd:element>
            <xsd:element name="SearchPA">
            	<xsd:complexType>
            		<xsd:sequence>

            			<xsd:element name="searchPARequest" type="tns:SearchPARequestType"/>
            		</xsd:sequence>
            	</xsd:complexType>
            </xsd:element>
            <xsd:element name="SearchPAResponse">
            	<xsd:complexType>
            		<xsd:sequence>

            			<xsd:element name="searchPAResponse" type="tns:SearchPAResponseType"/>
            		</xsd:sequence>
            	</xsd:complexType>
            </xsd:element>

            <xsd:complexType name="SearchFullNameDOBRequestType">
            	<xsd:sequence>
            		<xsd:element name="fullName" type="xsd:string"/>
            		<xsd:element name="address" type="xsd:string"/>
            		<xsd:element name="birthDate" type="xsd:string"/>
            		<xsd:element name="postCd" type="xsd:string"/>
            		<xsd:element name="applicationId" type="xsd:string"/>
		      		<xsd:element name="searchWidth" type="xsd:string"/>
		      		<xsd:element name="matchTolerance" type="xsd:string"/>
		      		<xsd:element name="resultSetMax" type="xsd:string"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="SearchFullNameDOBResponseType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="physicianSearchResponse" type="tns:PhysicianSearchResponseType"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="SearchIndividualByStateRequestType">
            	<xsd:sequence>
            		<xsd:element name="fullName" type="xsd:string" minOccurs="0"/>
            		<xsd:element name="birthDate" type="xsd:string" minOccurs="0"/>
            		<xsd:element name="stateCd" type="xsd:string" minOccurs="0"/>
            		<xsd:element name="applicationId" type="xsd:string" minOccurs="0"/>
		      		<xsd:element name="searchWidth" type="xsd:string" minOccurs="0"/>
		      		<xsd:element name="matchTolerance" type="xsd:string" minOccurs="0"/>
		      		<xsd:element name="resultSetMax" type="xsd:string" minOccurs="0"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="SearchIndividualByStateResponseType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="physicianSearchResponse" type="tns:PhysicianSearchResponseType"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="SearchByPartyIdRequestType">
            	<xsd:sequence>
            		<xsd:element name="partyId" type="xsd:string"/>
            		<xsd:element name="applicationId" type="xsd:string"/>
		      		<xsd:element name="searchWidth" type="xsd:string"/>
		      		<xsd:element name="matchTolerance" type="xsd:string"/>
		      		<xsd:element name="resultSetMax" type="xsd:string"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="SearchByPartyIdResponseType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="physicianSearchResponse" type="tns:PhysicianSearchResponseType"/>
            	</xsd:sequence>
            </xsd:complexType>
            <xsd:element name="SearchByAMAID">
            	<xsd:complexType>
            		<xsd:sequence>
            			<xsd:element name="searchByAMAIDRequest" type="tns:SearchByAMAIDRequestType"/>
            		</xsd:sequence>
            	</xsd:complexType>
            </xsd:element>
            <xsd:element name="SearchByAMAIDResponse">
            	<xsd:complexType>
            		<xsd:sequence>

            			<xsd:element name="searchByAMAIDResponse" type="tns:SearchByAMAIDResponseType"/>
            		</xsd:sequence>
            	</xsd:complexType>
            </xsd:element>

            <xsd:complexType name="SearchPARequestType">
            	<xsd:sequence>
            		<xsd:element name="fullName" type="xsd:string"/>
            		<xsd:element name="birthDate" type="xsd:string"/>
            		<xsd:element name="nccpa" type="xsd:string"/>
            		<xsd:element name="licenseNumber" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="licenseSource" type="xsd:string"/>
            		<xsd:element name="applicationId" type="xsd:string"/>
		      		<xsd:element name="searchWidth" type="xsd:string"/>
		      		<xsd:element name="matchTolerance" type="xsd:string"/>
		      		<xsd:element name="resultSetMax" type="xsd:string"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="SearchPAResponseType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="paSearchResponse" type="tns:PASearchResponseType"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="SearchByAMAIDRequestType">
            	<xsd:sequence>
            		<xsd:element name="amaId" type="xsd:string"/>
            		<xsd:element name="applicationId" type="xsd:string"/>
		      		<xsd:element name="searchWidth" type="xsd:string"/>
		      		<xsd:element name="matchTolerance" type="xsd:string"/>
		      		<xsd:element name="resultSetMax" type="xsd:string"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="SearchByAMAIDResponseType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="paSearchResponse" type="tns:PASearchResponseType"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="PhysicianSearchResponseType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="1" minOccurs="1" name="score" type="xsd:int">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="1" name="partyId" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="1" name="entityId" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="personType" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="legalFirstName" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="legalLastName" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="legalMiddleName" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="legalSuffix" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="legalFullName" type="xsd:string">
            		</xsd:element>





            		<xsd:element name="names" type="tns:NamesType"/>
            		<xsd:element maxOccurs="1" minOccurs="0" name="birthDate" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="degreeCode" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="npiNumber" type="tns:NPIsType"/>

            		<xsd:element name="licenses" type="tns:LicensesType">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="ecfmgNumber" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="meNumber" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="deaNumbers" type="tns:DEANumbersType">
            		</xsd:element>
            		<xsd:element name="emails" type="tns:EmailsType">
            		</xsd:element>

            		<xsd:element maxOccurs="1" minOccurs="0" name="medicalSchoolCode" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="medicalSchoolName" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="medicalSchoolEntityId" type="xsd:string"/>
            		<xsd:element maxOccurs="1" minOccurs="0" name="gradYear" type="xsd:int">
            		</xsd:element>



            		<xsd:element name="residencies" type="tns:ResidenciesType">
            		</xsd:element>
            		<xsd:element name="addresses" type="tns:AddressesType">
            		</xsd:element>
            		<xsd:element name="phoneNumbers" type="tns:PhoneNumbersType">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="dnrIndicator" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="mortalityStatusCode" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="cutStatus" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="permForeignStatus" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="primarySpeciality" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="primarySpecialityDescription" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="secondarySpeciality" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="secondarySpecialityDescription" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="membershipEligible" type="xsd:string">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="membershipYear" type="xsd:int">
            		</xsd:element>
            		<xsd:element maxOccurs="1" minOccurs="0" name="membershipStatus" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="abmsInfo" type="tns:ABMSListType">
            		</xsd:element>
            		<xsd:element name="delegateInfo" type="tns:DelegatesType">
            		</xsd:element>

            		<xsd:element maxOccurs="1" minOccurs="0" name="clId" type="xsd:string">
            		</xsd:element>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="PASearchResponseType">
            	<xsd:sequence>
            		<xsd:element name="score" type="xsd:int"/>
            		<xsd:element name="amaId" type="xsd:int"/>
            		<xsd:element name="firstName" type="xsd:string"/>
            		<xsd:element name="lastName" type="xsd:string"/>
            		<xsd:element name="middleName" type="xsd:string"/>
            		<xsd:element name="fullName" type="xsd:string"/>
            		<xsd:element name="birthDate" type="xsd:string"/>
            		<xsd:element name="nccpa" type="xsd:string"/>
            		<xsd:element name="licenses" type="tns:PALicensesType">
            		</xsd:element>

            		<xsd:element name="programCode" type="xsd:string"/>
            		<xsd:element name="programName" type="xsd:string"/>
            		<xsd:element name="gradYear" type="xsd:string"/>
            		<xsd:element name="homeAddressId" type="xsd:int">
            		</xsd:element>
            		<xsd:element name="workAddressId" type="xsd:int">
            		</xsd:element>
            		<xsd:element name="homeAddressLine1" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="homeAddressLine2" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="homeAddressLine3" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="homeCityName" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="homeStateCode" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="homeZip" type="xsd:string"/>
            		<xsd:element name="homeZipPlus4" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="workAddressLine1" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="workAddressLine2" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="workAddressLine3" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="workCityName" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="workStateCode" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="workZip" type="xsd:string"/>
            		<xsd:element name="workZipPlus4" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="clId" type="xsd:string"/>
            	</xsd:sequence>
            </xsd:complexType>

           <xsd:complexType name="PALicensesType">
                <xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="License" type="tns:PALicenseType"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="PALicenseType">
            	<xsd:sequence>
            		<xsd:element name="licenseNumber" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="licenseSource" type="xsd:string">
            		</xsd:element>

            	</xsd:sequence>
            </xsd:complexType>


            <xsd:complexType name="LicensesType">
                <xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="License" type="tns:LicenseType"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="LicenseType">
            	<xsd:sequence>
            		<xsd:element name="licenseNumber" type="xsd:string">
            		</xsd:element>
            		<xsd:element name="licenseStateCd" type="xsd:string">
            		</xsd:element>

            	</xsd:sequence>
            </xsd:complexType>


            <xsd:complexType name="EmailsType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="Email" type="tns:EmailType"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="EmailType">
            	<xsd:sequence>
            		<xsd:element name="emailAddress" type="xsd:string"/>
            	</xsd:sequence>
            </xsd:complexType>



              <xsd:complexType name="DEANumbersType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="DEANumber" type="tns:DEANumberType"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="DEANumberType">
            	<xsd:sequence>
            		<xsd:element name="deaNumber" type="xsd:string"/>
            	</xsd:sequence>
            </xsd:complexType>

  			<xsd:complexType name="ResidenciesType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="Residency" type="tns:ResidencyType"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="ResidencyType">
            	<xsd:sequence>
            		<xsd:element name="resBeginDate" type="xsd:string"/>
            		<xsd:element name="resEndDate" type="xsd:string"/>
            		<xsd:element name="resStartYear" type="xsd:int"/>
            	</xsd:sequence>
            </xsd:complexType>

  			<xsd:complexType name="AddressesType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="Address" type="tns:AddressType"/>
            	</xsd:sequence>
            </xsd:complexType>

             <xsd:complexType name="AddressType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="1" minOccurs="0" name="addressType" type="xsd:string"/>
            		<xsd:element maxOccurs="1" minOccurs="0" name="addressLine" type="xsd:string"/>
            		<xsd:element maxOccurs="1" minOccurs="0" name="city" type="xsd:string"/>
            		<xsd:element maxOccurs="1" minOccurs="0" name="stateCode" type="xsd:string"/>
            		<xsd:element maxOccurs="1" minOccurs="0" name="postalCode" type="xsd:string"/>
            	</xsd:sequence>
            </xsd:complexType>

             <xsd:complexType name="PhoneNumbersType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="PhoneNumber" type="tns:PhoneNumberType"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="PhoneNumberType">
            	<xsd:sequence>
            		<xsd:element name="phoneType" type="xsd:string"/>
            		<xsd:element name="phoneNumber" type="xsd:string"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="NamesType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="Name" type="tns:NameType"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="NameType">
            	<xsd:sequence>
            		<xsd:element name="firstName" type="xsd:string"/>
            		<xsd:element name="middleName" type="xsd:string"/>
            		<xsd:element name="lastName" type="xsd:string"/>
            		<xsd:element name="firstIniLastName" type="xsd:string"/>
            		<xsd:element name="fullName" type="xsd:string"/>
            	</xsd:sequence>
            </xsd:complexType>

             <xsd:complexType name="DelegatesType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="Delegate" type="tns:DelegateDesc"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="DelegateDesc">
            	<xsd:sequence>
            		<xsd:element name="delegateId" type="xsd:string"/>
            		<xsd:element name="delegateType" type="xsd:string"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="NPIsType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="NPI" type="tns:NPIType"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="NPIType">
            	<xsd:sequence>
            		<xsd:element name="npiNumber" type="xsd:string"/>
            	</xsd:sequence>
            </xsd:complexType>

             <xsd:complexType name="ABMSListType">
            	<xsd:sequence>
            		<xsd:element maxOccurs="unbounded" minOccurs="0" name="ABMS" type="tns:ABMSType"/>
            	</xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="ABMSType">
            	<xsd:sequence>
            		<xsd:element name="abmsId" type="xsd:string"/>
            	</xsd:sequence>
            </xsd:complexType>

    </xsd:schema>
  </wsdl:types>
  <wsdl:message name="SearchEnterpriseEntityRequest">
    <wsdl:part element="tns:SearchEnterpriseEntity" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="SearchEnterpriseEntityResponse">
    <wsdl:part element="tns:SearchEnterpriseEntityResponse" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="SearchFirstInitialLastNameDOBRequest">
  	<wsdl:part element="tns:SearchFirstInitialLastNameDOB" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="SearchFirstInitialLastNameDOBResponse">
  	<wsdl:part element="tns:SearchFirstInitialLastNameDOBResponse" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="SearchFullNameDOBRequest">
  	<wsdl:part element="tns:SearchFullNameDOB" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="SearchFullNameDOBResponse">
  	<wsdl:part element="tns:SearchFullNameDOBResponse" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="SearchIndividualByStateRequest">
  	<wsdl:part element="tns:SearchIndividualByState" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="SearchIndividualByStateResponse">
  	<wsdl:part element="tns:SearchIndividualByStateResponse" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="SearchByPartyIdRequest">
  	<wsdl:part element="tns:SearchByPartyId" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="SearchByPartyIdResponse">
  	<wsdl:part element="tns:SearchByPartyIdResponse" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="SearchPARequest">
  	<wsdl:part element="tns:SearchPA" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="SearchPAResponse">
  	<wsdl:part element="tns:SearchPAResponse" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="SearchByAMAIDRequest">
  	<wsdl:part element="tns:SearchByAMAID" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="SearchByAMAIDResponse">
  	<wsdl:part element="tns:SearchByAMAIDResponse" name="parameters"/>
  </wsdl:message>
  <wsdl:portType name="enterprisesearch">
    <wsdl:operation name="SearchEnterpriseEntity">
      <wsdl:input message="tns:SearchEnterpriseEntityRequest"/>
      <wsdl:output message="tns:SearchEnterpriseEntityResponse"/>
    </wsdl:operation>
    <wsdl:operation name="SearchFirstInitialLastNameDOB">
    	<wsdl:input message="tns:SearchFirstInitialLastNameDOBRequest"/>
    	<wsdl:output message="tns:SearchFirstInitialLastNameDOBResponse"/>
    </wsdl:operation>
    <wsdl:operation name="SearchFullNameDOB">
    	<wsdl:input message="tns:SearchFullNameDOBRequest"/>
    	<wsdl:output message="tns:SearchFullNameDOBResponse"/>
    </wsdl:operation>
    <wsdl:operation name="SearchIndividualByState">
    	<wsdl:input message="tns:SearchIndividualByStateRequest"/>
    	<wsdl:output message="tns:SearchIndividualByStateResponse"/>
    </wsdl:operation>
    <wsdl:operation name="SearchByPartyId">
    	<wsdl:input message="tns:SearchByPartyIdRequest"/>
    	<wsdl:output message="tns:SearchByPartyIdResponse"/>
    </wsdl:operation>
  </wsdl:portType>
  <wsdl:portType name="pasearch">
  	<wsdl:operation name="SearchPA">
  		<wsdl:input message="tns:SearchPARequest"/>
  		<wsdl:output message="tns:SearchPAResponse"/>
  	</wsdl:operation>
  	<wsdl:operation name="SearchByAMAID">
  		<wsdl:input message="tns:SearchByAMAIDRequest"/>
  		<wsdl:output message="tns:SearchByAMAIDResponse"/>
  	</wsdl:operation>
  </wsdl:portType>
  <wsdl:binding name="enterprisesearchSOAP" type="tns:enterprisesearch">
  	<soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
  	<wsdl:operation name="SearchEnterpriseEntity">
  		<soap:operation soapAction="http://myama.com/enterprisesearch/SearchEnterpriseEntity"/>
  		<wsdl:input>
  			<soap:body use="literal"/>
  		</wsdl:input>
  		<wsdl:output>
  			<soap:body use="literal"/>
  		</wsdl:output>
  	</wsdl:operation>
  	<wsdl:operation name="SearchFirstInitialLastNameDOB">
  		<soap:operation soapAction="http://myama.com/enterprisesearch/SearchFirstInitialLastNameDOB"/>
  		<wsdl:input>
  			<soap:body use="literal"/>
  		</wsdl:input>
  		<wsdl:output>
  			<soap:body use="literal"/>
  		</wsdl:output>
  	</wsdl:operation>
  	<wsdl:operation name="SearchFullNameDOB">
  		<soap:operation soapAction="http://myama.com/enterprisesearch/SearchFullNameDOB"/>
  		<wsdl:input>
  			<soap:body use="literal"/>
  		</wsdl:input>
  		<wsdl:output>
  			<soap:body use="literal"/>
  		</wsdl:output>
  	</wsdl:operation>
  	<wsdl:operation name="SearchIndividualByState">
  		<soap:operation soapAction="http://myama.com/enterprisesearch/SearchIndividualByState"/>
  		<wsdl:input>
  			<soap:body use="literal"/>
  		</wsdl:input>
  		<wsdl:output>
  			<soap:body use="literal"/>
  		</wsdl:output>
  	</wsdl:operation>
  	<wsdl:operation name="SearchByPartyId">
  		<soap:operation soapAction="http://myama.com/enterprisesearch/SearchByPartyId"/>
  		<wsdl:input>
  			<soap:body use="literal"/>
  		</wsdl:input>
  		<wsdl:output>
  			<soap:body use="literal"/>
  		</wsdl:output>
  	</wsdl:operation>
  </wsdl:binding>
  <wsdl:binding name="pasearchSOAP" type="tns:pasearch">
  	<soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
  	<wsdl:operation name="SearchPA">
  		<soap:operation soapAction="http://myama.com/enterprisesearch/SearchPA"/>
  		<wsdl:input>
  			<soap:body use="literal"/>
  		</wsdl:input>
  		<wsdl:output>
  			<soap:body use="literal"/>
  		</wsdl:output>
  	</wsdl:operation>
  	<wsdl:operation name="SearchByAMAID">
  		<soap:operation soapAction="http://myama.com/enterprisesearch/SearchByAMAID"/>
  		<wsdl:input>
  			<soap:body use="literal"/>
  		</wsdl:input>
  		<wsdl:output>
  			<soap:body use="literal"/>
  		</wsdl:output>
  	</wsdl:operation>
  </wsdl:binding>
  <wsdl:service name="EnterpriseSearchService">
    <wsdl:port binding="tns:enterprisesearchSOAP" name="enterprisesearchSOAP">
      <soap:address location=""/>
    </wsdl:port>
  </wsdl:service>
  <wsdl:service name="PASearchService">
  	<wsdl:port binding="tns:pasearchSOAP" name="pasearchSOAP">
  		<soap:address location="http://localhost:9080/enterprisesearch/PASearchService"/>
  	</wsdl:port>
  </wsdl:service>
</wsdl:definitions>
"""