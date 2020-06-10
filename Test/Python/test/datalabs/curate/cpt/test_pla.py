""" source: datalabs.curate.cpt.pla """
import logging
import pytest

from   datalabs.curate.cpt.pla import PLAParser

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_pla_parser(text):
    parser = PLAParser()
    data = parser.parse(text)
    LOGGER.debug('Data: \n%s', data)

    assert len(data) == 10

    assert data['pla_code'][0] == '0001U'
    assert data['pla_code'][1] == '0002U'

    assert data['short_descriptor'][0] == 'RBC DNA HEA 35 AG 11 BLD GRP WHL BLD CMN ALLEL'
    assert data['short_descriptor'][1] == 'ONC CLRCT QUAN 3 UR METABOLITES ALG ADNMTS PLP'

    assert data['medium_descriptor'][0] == 'RBC DNA HEA 35 AG 11 BLD GRP'
    assert data['medium_descriptor'][1] == 'ONC CLRCT QUAN 3 UR METABOLITES ALG ADNMTS PLP'

    assert data['long_descriptor'][0] == 'Red blood cell antigen typing, DNA, human erythrocyte antigen gene analysis' \
                                         ' of 35 antigens from 11 blood groups, utilizing whole blood, common RBC ' \
                                         'alleles reported'
    assert data['long_descriptor'][1] == 'Oncology (colorectal), quantitative assessment of three urine metabolites' \
                                         ' (ascorbic acid, succinic acid and carnitine) by liquid chromatography with ' \
                                         'tandem mass spectrometry (LC-MS/MS) using multiple reaction monitoring ' \
                                         'acquisition, algorithm reported as likelihood of adenomatous polyps'

    assert data['status'][0] == 'EXISTING'
    assert data['status'][1] == 'EXISTING'

    assert data['effective_date'][0] == '2017-02-01T00:00:00-06:00'
    assert data['effective_date'][1] == '2017-02-01T00:00:00-06:00'

    assert data['lab_name'][0] == 'Immucor, Inc'
    assert data['lab_name'][1] == 'Atlantic Diagnostic Laboratories, LLC'

    assert data['manufacturer'][0] == 'Immucor, Inc'
    assert data['manufacturer'][1] == 'Metabolomic Technologies Inc'

    assert data['published_date'][0] == '2016-12-02T00:00:00-06:00'
    assert data['published_date'][1] == '2016-12-02T00:00:00-06:00'

    assert data['test'][0] == 'PreciseType® HEA Test'
    assert data['test'][1] == 'PolypDX™'


@pytest.fixture(scope='module')
def text():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<plaCodes>
    
<plaCode cdCode="0001U" cdId="1">
        <cdDesc>Red blood cell antigen typing, DNA, human erythrocyte antigen gene analysis of 35 antigens from 11 blood groups, utilizing whole blood, common RBC alleles reported</cdDesc>
        <cdMDesc>RBC DNA HEA 35 AG 11 BLD GRP WHL BLD CMN ALLEL</cdMDesc>
        <cdSDesc>RBC DNA HEA 35 AG 11 BLD GRP</cdSDesc>
        <cdStatus>EXISTING</cdStatus>
        <clinicalDesc></clinicalDesc>
        <consumerDesc></consumerDesc>
        <effectiveDate>2017-02-01T00:00:00-06:00</effectiveDate>
        <labName>Immucor, Inc</labName>
        <manufacturerName>Immucor, Inc</manufacturerName>
        <publishDate>2016-12-02T00:00:00-06:00</publishDate>
        <testName>PreciseType® HEA Test</testName>
    </plaCode>
<plaCode cdCode="0002U" cdId="2">
        <cdDesc>Oncology (colorectal), quantitative assessment of three urine metabolites (ascorbic acid, succinic acid and carnitine) by liquid chromatography with tandem mass spectrometry (LC-MS/MS) using multiple reaction monitoring acquisition, algorithm reported as likelihood of adenomatous polyps</cdDesc>
        <cdMDesc>ONC CLRCT QUAN 3 UR METABOLITES ALG ADNMTS PLP</cdMDesc>
        <cdSDesc>ONC CLRCT 3 UR METAB ALG PLP</cdSDesc>
        <cdStatus>EXISTING</cdStatus>
        <clinicalDesc></clinicalDesc>
        <consumerDesc></consumerDesc>
        <effectiveDate>2017-02-01T00:00:00-06:00</effectiveDate>
        <labName>Atlantic Diagnostic Laboratories, LLC</labName>
        <manufacturerName>Metabolomic Technologies Inc</manufacturerName>
        <publishDate>2016-12-02T00:00:00-06:00</publishDate>
        <testName>PolypDX™</testName>
    </plaCode>
<plaCode cdCode="0003U" cdId="3">
        <cdDesc>Oncology (ovarian) biochemical assays of five proteins (apolipoprotein A-1, CA 125 II, follicle stimulating hormone, human epididymis protein 4, transferrin), utilizing serum, algorithm reported as a likelihood score</cdDesc>
        <cdMDesc>ONC OVARIAN ASSAY 5 PROTEINS SERUM ALG SCOR</cdMDesc>
        <cdSDesc>ONC OVAR 5 PRTN SER ALG SCOR</cdSDesc>
        <cdStatus>EXISTING</cdStatus>
        <clinicalDesc></clinicalDesc>
        <consumerDesc></consumerDesc>
        <effectiveDate>2017-02-01T00:00:00-06:00</effectiveDate>
        <labName>Aspira Labs, Inc</labName>
        <manufacturerName>Vermillion, Inc</manufacturerName>
        <publishDate>2016-12-02T00:00:00-06:00</publishDate>
        <testName>Overa (OVA1 Next Generation)</testName>
    </plaCode>
<plaCode cdCode="0005U" cdId="5">
        <cdDesc>Oncology (prostate) gene expression profile by real-time RT-PCR of 3 genes (ERG, PCA3, and SPDEF), urine, algorithm reported as risk score</cdDesc>
        <cdMDesc>ONCO PRST8 GENE XPRS PRFL 3 GENE UR ALG RSK SCOR</cdMDesc>
        <cdSDesc>ONCO PRST8 3 GENE UR ALG</cdSDesc>
        <cdStatus>EXISTING</cdStatus>
        <effectiveDate>2017-05-01T00:00:00-05:00</effectiveDate>
        <labName>Exosome Diagnostics, Inc</labName>
        <manufacturerName>Exosome Diagnostics, Inc</manufacturerName>
        <publishDate>2017-03-01T00:00:00-06:00</publishDate>
        <testName>ExosomeDx® Prostate (IntelliScore)</testName>
    </plaCode>
<plaCode cdCode="0007U" cdId="7">
        <cdDesc>Drug test(s), presumptive, with definitive confirmation of positive results, any number of drug classes, urine, includes specimen verification including DNA authentication in comparison to buccal DNA, per date of service</cdDesc>
        <cdMDesc>RX TEST PRESUMPTIVE URINE W/DEF CONFIRMATION</cdMDesc>
        <cdSDesc>RX TEST PRSMV UR W/DEF CONF</cdSDesc>
        <cdStatus>EXISTING</cdStatus>
        <effectiveDate>2017-08-01T00:00:00-05:00</effectiveDate>
        <labName>Genotox Laboratories LTD</labName>
        <manufacturerName>Genotox Laboratories LTD</manufacturerName>
        <publishDate>2017-06-01T00:00:00-05:00</publishDate>
        <testName>ToxProtect</testName>
    </plaCode>
<plaCode cdCode="0008U" cdId="8">
        <cdDesc>Helicobacter pylori detection and antibiotic resistance, DNA, 16S and 23S rRNA, gyrA, pbp1, rdxA and rpoB, next generation sequencing, formalin-fixed paraffin-embedded or fresh tissue or fecal sample, predictive, reported as positive or negative for resistance to clarithromycin, fluoroquinolones, metronidazole, amoxicillin, tetracycline, and rifabutin</cdDesc>
        <cdMDesc>HPYLORI DETECTION &amp; ANTIBIOTIC RESISTANCE DNA</cdMDesc>
        <cdSDesc>HPYLORI DETCJ ABX RSTNC DNA</cdSDesc>
        <cdStatus>EXISTING</cdStatus>
        <effectiveDate>2019-01-01T00:00:00-05:00</effectiveDate>
        <labName>American Molecular Laboratories, Inc</labName>
        <manufacturerName>American Molecular Laboratories, Inc</manufacturerName>
        <publishDate>2018-11-30T00:00:00-05:00</publishDate>
        <testName>AmHPR H. Antibiotic Resistance Panel</testName>
    </plaCode>
<plaCode cdCode="0009U" cdId="9">
        <cdDesc>Oncology (breast cancer), ERBB2 (HER2) copy number by FISH, tumor cells from formalin-fixed paraffin-embedded tissue isolated using image-based dielectrophoresis (DEP) sorting, reported as ERBB2 gene amplified or non-amplified</cdDesc>
        <cdMDesc>ONC BRST CA ERBB2 COPY NUMBER FISH AMP/NONAMP</cdMDesc>
        <cdSDesc>ONC BRST CA ERBB2 AMP/NONAMP</cdSDesc>
        <cdStatus>EXISTING</cdStatus>
        <effectiveDate>2017-08-01T00:00:00-05:00</effectiveDate>
        <labName>PacificDx</labName>
        <manufacturerName>PacificDx</manufacturerName>
        <publishDate>2017-06-01T00:00:00-05:00</publishDate>
        <testName>DEPArray™ HER2</testName>
    </plaCode>
<plaCode cdCode="0010U" cdId="10">
       <cdDesc>Infectious disease (bacterial), strain typing by whole genome sequencing, phylogenetic-based report of strain relatedness, per submitted isolate</cdDesc>
        <cdMDesc>NFCT DS STRN TYP WHL GENOME SEQUENCING PR ISOL</cdMDesc>
        <cdSDesc>NFCT DS STRN TYP WHL GEN SEQ</cdSDesc>
        <cdStatus>EXISTING</cdStatus>
        <effectiveDate>2017-08-01T00:00:00-05:00</effectiveDate>
        <labName>Mayo Clinic</labName>
        <manufacturerName>Mayo Clinic</manufacturerName>
        <publishDate>2017-06-01T00:00:00-05:00</publishDate>
        <testName>Bacterial Strain Typing by Whole Genome Sequencing</testName>
    </plaCode>
<plaCode cdCode="0011U" cdId="11">
       <cdDesc>Prescription drug monitoring, evaluation of drugs present by LC-MS/MS, using oral fluid, reported as a comparison to an estimated steady-state range, per date of service including all drug compounds and metabolites</cdDesc>
        <cdMDesc>RX MNTR DRUGS PRESENT LC-MS/MS ORAL FLUID PR DOS</cdMDesc>
        <cdSDesc>RX MNTR LC-MS/MS ORAL FLUID</cdSDesc>
        <cdStatus>EXISTING</cdStatus>
        <effectiveDate>2017-08-01T00:00:00-05:00</effectiveDate>
        <labName>Cordant Health Solutions</labName>
        <manufacturerName>Cordant Health Solutions</manufacturerName>
        <publishDate>2017-06-01T00:00:00-05:00</publishDate>
        <testName>Cordant CORE™</testName>
    </plaCode>
<plaCode cdCode="0012U" cdId="12">
       <cdDesc>Germline disorders, gene rearrangement detection by whole genome next-generation sequencing, DNA, whole blood, report of specific gene rearrangement(s)</cdDesc>
        <cdMDesc>GERMLN DO GENE REARGMT DETCJ DNA WHOLE BLOOD</cdMDesc>
        <cdSDesc>GERMLN DO GENE REARGMT DETCJ</cdSDesc>
        <cdStatus>EXISTING</cdStatus>
        <effectiveDate>2017-08-01T00:00:00-05:00</effectiveDate>
        <labName>Mayo Clinic</labName>
        <manufacturerName>Mayo Clinic</manufacturerName>
        <publishDate>2017-06-01T00:00:00-05:00</publishDate>
        <testName>MatePair Targeted Rearrangements, Congenital</testName>
    </plaCode>
  </plaCodes>
"""