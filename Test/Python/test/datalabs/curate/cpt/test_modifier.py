""" source: datalabs.curate.cpt.modifier """
import logging
import pytest

from   datalabs.curate.cpt.modifier import ModifierParser, ModifierType

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name
def test_modifier_parser(text):
    parser = ModifierParser()

    data = parser.parse(text)

    LOGGER.debug('Data: \n%s', data)

    assert len(data) == 2 * len(ModifierType.__members__)

    regular_modifiers = data[data['type'] == 'Category I']
    assert len(regular_modifiers) == 2

    regular_modifiers = data[data['type'] == 'Anesthesia Physical Status']
    assert len(regular_modifiers) == 2

    regular_modifiers = data[data['type'] == 'Ambulatory Service Center']
    assert len(regular_modifiers) == 2

    regular_modifiers = data[data['type'] == 'Category II']
    assert len(regular_modifiers) == 2

    regular_modifiers = data[data['type'] == 'Level II']
    assert len(regular_modifiers) == 2


@pytest.fixture
def text():
    return """
CPT® codes, descriptions and other data are copyright 1966, 1970, 1973,
1977, 1981, 1983-2019 American Medical Association. All rights reserved.
CPT is a registered trademark of the American Medical Association.

U.S. GOVERNMENT RIGHTS. CPT is commercial technical data and/or
computer data bases and/or commercial computer software and/or


Appendix A

Modifiers 

This list includes all of the modifiers applicable to CPT 2020 codes. 

A modifier provides the means to report or indicate that a 
service or procedure that has been performed has been 
altered by some specific circumstance but not changed in 
its definition or code. Modifiers also enable health care 
professionals to effectively respond to payment policy 
requirements established by other entities. 

22 Increased Procedural Services: When the work required 
to provide a service is substantially greater than typically 

23 Unusual Anesthesia: Occasionally, a procedure, which 
usually requires either no anesthesia or local anesthesia, 

Anesthesia Physical Status 
Modifiers 

The Physical Status modifiers are consistent with the 
American Society of Anesthesiologists ranking of patient 
physical status, and distinguishing various levels of 
complexity of the anesthesia service provided. All 
anesthesia services are reported by use of the anesthesia 
five-digit procedure code (00100-01999) with the 
appropriate physical status modifier appended. 

Example: 00100-P1 

Under certain circumstances, when another established 
modifier(s) is appropriate, it should be used in addition 
to the physical status modifier. 

Example: 00100-P4-53 

Physical Status Modifier P1: A normal healthy patient 

Physical Status Modifier P2: A patient with mild systemic disease 


Modifiers Approved for Ambulatory Surgery Center (ASC) Hospital Outpatient Use 

CPT Level I Modifiers 

25 Significant, Separately Identifiable Evaluation and 
Management Service by the Same Physician or Other 

27 Multiple Outpatient Hospital E/M Encounters on the 
Same Date: For hospital outpatient reporting purposes, 


Category II Modifiers

The following performance measurement modifiers may be used for 
Category II codes to indicate that a service specified in the 
associated measure(s) was considered but, due to either medical, 
patient, or system circumstance(s) documented in the medical 
record, the service was not provided. These modifiers serve 
as denominator exclusions from the performance measure. 
The user should note that not all listed measures provide 
for exclusions (see Alphabetical Clinical Topics Listing for 
more discussion regarding exclusion criteria).

Category II modifiers should only be reported with Category II 
codes—they should not be reported with Category I or Category III 
codes. In addition, the modifiers in the Category II section 
should only be used where specified in the guidelines, reporting 
instructions, parenthetic notes, or code descriptor language 
listed in the Category II section (code listing and the 
Alphabetical Clinical Topics Listing).

1P Performance Measure Exclusion Modifier due to Medical Reasons
Reasons include:
Not indicated (absence of organ/limb, already received/ performed, other)
Contraindicated (patient allergic history, potential adverse drug interaction, other)
Other medical reasons

2P Performance Measure Exclusion Modifier due to Patient Reasons
Reasons include:
Patient declined
Economic, social, or religious reasons
Other patient reasons
 

Level II (HCPCS/National) Modifiers 

E1 Upper left, eyelid 
E2 Lower left, eyelid 

(*HCPCS modifiers for selective identification of subsets of 
Distinct Procedural Services [-59 modifier])""".encode('cp1252').replace(b'\n', b'\r\n').decode('cp1252')
