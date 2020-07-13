""" source: datalabs.curate.cpt.link.history """
import logging
import pytest

import link.history as link

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=protected-access, redefined-outer-name
def test_deleted_history(deleted_text):
    parser = link.DeletionHistoryParser()
    text = parser.parse(deleted_dtk_text)

    LOGGER.debug('Text: \n%s', text)

    lines = text.splitlines()

    assert len(lines) == 6

    for line in lines:
        assert line.startswith('1031078')


# pylint: disable=protected-access, redefined-outer-name
def test_code_history(code_history_text):
    parser = link.CodeHistoryParser()
    text = parser.parse(code_history_text)

    LOGGER.debug('Text: \n%s', text)

    lines = text.splitlines()

    assert len(lines) == 8

    for line in lines:
        assert line.startswith('Pre-1982')


# pylint: disable=protected-access, redefined-outer-name
def test_history_modifiers(modifier_history_text):
    parser = link.HistoryModifierParser()
    text = parser.parse(modifier_history_text)

    LOGGER.debug('Text: \n%s', text)

    lines = text.splitlines()

    assert len(lines) == 8

    for line in lines:
        assert line.startswith('Pre-1990')


@pytest.fixture
def deleted_test_data():
    return """Concept Id	Code	Date Deleted	Level	Descriptor	Instruction
1031078	11050	Pre-1982	Not available	Descriptor not available	
1031079	14800	Pre-1982	Not available	Descriptor not available	
1031080	14840	Pre-1982	Not available	Descriptor not available	
1031081	14845	Pre-1982	Not available	Descriptor not available	
1031082	14850	Pre-1982	Not available	Descriptor not available	
1031083	14855	Pre-1982	Not available	Descriptor not available	
1031084	14860	Pre-1982	Not available	Descriptor not available	
1031085	15055	Pre-1982	Not available	Descriptor not available	
1031086	15265	Pre-1982	Not available	Descriptor not available	
1031087	24300	Pre-1982	Not available	Descriptor not available
"""


@pytest.fixture
def code_history_test_data():
    return """Date	Change Type	Concept Id	CPT Code	Level	Prior Value	Current Value	Instruction
Pre-1982	DELETED	1031078	11050		Descriptor not available
Pre-1982	DELETED	1031079	14800		Descriptor not available
Pre-1982	DELETED	1031080	14840		Descriptor not available
Pre-1982	DELETED	1031081	14845		Descriptor not available
Pre-1982	DELETED	1031082	14850		Descriptor not available
Pre-1982	DELETED	1031083	14855		Descriptor not available
Pre-1982	DELETED	1031084	14860		Descriptor not available
Pre-1982	DELETED	1031085	15055		Descriptor not available
Pre-1982	DELETED	1031086	15265		Descriptor not available
Pre-1982	DELETED	1031087	24300		Descriptor not available
Pre-1982	DELETED	1031088	26125		Descriptor not available
"""


@pytest.fixture
def modifier_history_test_data():
    return """Date	Change Type	Concept Id	Modifier Code	Prior Value	CurrentValue
Pre-1990	ADDED	1021517	1P		Performance Measure Exclusion Modifier due to Medical Reasons
20140101	ADDED	1021516			Category II Modifiers
20140101	ADDED	1021862			CPT Level I Modifiers
Pre-1990	ADDED	1021440	22		Increased Procedural Services
Pre-1990	ADDED	1021441	23		Unusual Anesthesia
Pre-1990	ADDED	1021442	24		Unrelated Evaluation and Management Service by the Same Physician or Other Qualified Health Care Professional During a Postoperative Period
Pre-1990	ADDED	1021443	25		Significant, Separately Identifiable Evaluation and Management Service by the Same Physician or Other Qualified Health Care Professional on the Same Day of the Procedure or Other Service
20140101	ADDED	1021438			CPT Level I Modifiers for ASC
20140101	ADDED	1021437			Modifiers Approved for Ambulatory Surgery Center (ASC) Hospital Outpatient Use
"""
