OPTION_MAP = {
    "1": "yesno",
    "2": "pronoun",
    "3": "race",
    "4": "language",
    "7": "state",
    "8": "country",
    "9": "privilege",
    "10": "yesnona",
    "11": "specialty",
    "12": "currentstatus",
    "13": "entity",
    "14": "yesnoother",
    "15": "dept",
    "16": "referencedegree",
    "17": "hospital",
    "18": "expertise",
    "19": "referencetype",
    "20": "trainingType",
    "21": "certificateType",
    "22": "specialtySCA",
    "23": "gender"
}

OPTION_VALUES_MAP = {
    "yesno": {
        "1": "Yes",
        "0": "No"
    },
    "yesnona": {
        "1": "Yes",
        "0": "No",
        "3": "N/A"
    },
    "yesnoother": {
        "1": "Yes",
        "2": "No",
        "3": "Other - Recently Completed Training Program"
    },
    "race": {
        "A1": "Asian",
        "A2": "Other Asian",
        "A3": "Bangladeshi",
        "A4": "Cambodian",
        "A5": "Chinese",
        "A6": "Filipino",
        "A7": "Indian",
        "A8": "Indonesian",
        "A9": "Japanese",
        "B1": "Korean",
        "B2": "Laotian",
        "B3": "Pakistani",
        "B4": "Taiwanese",
        "B5": "Vietnamese",
        "B6": "Black or African American",
        "B7": "African",
        "B8": "African American",
        "B9": "Afro-Caribbean",
        "C1": "Other Black or African American",
        "C2": "Hispanic, Latino, or of Spanish Origin",
        "C3": "Argentinean",
        "C4": "Colombian",
        "C5": "Cuban",
        "C6": "Dominican",
        "C7": "Mexican, Mexican American, Chicago/Chicana",
        "C8": "Other Hispanic, Latino, or of Spanish Origin",
        "C9": "Peruvian",
        "D1": "Puerto Rican",
        "D2": "American Indian or Alaska Native",
        "D3": "Tribal Affiliation",
        "D4": "Native Hawaiian or Other Pacific Islander",
        "D5": "Guamanian",
        "D6": "Native Hawaiian",
        "D7": "Other Pacific Islander",
        "D8": "Samoan",
        "D9": "Unknown",
        "E1": "White",
        "E2": "Other",
        "E3": "Prefer not to say"
    },
    "pronoun": {
        "1": "she/her/hers",
        "2": "he/him/his",
        "3": "they/them/theirs",
        "4": "ze/hir/hirs",
        "5": "ze/zir/zirs",
        "6": "ey/em/eirs",
        "7": "no pronouns",
        "9": "prefer not to say"
    },
    "gender": {
        "1": "Male",
        "2": "Female",
        "3": "Non-binary/third gender",
        "4": "Genderqueer",
        "5": "Prefer to self-describe as",
        "6": "prefer not to say"
    },
    "language": {
        "A0": "Abkhazian",
        "A1": "Afan (Oromo)",
        "A2": "Afar",
        "A3": "Afrikaans",
        "A4": "Albanian",
        "A5": "American Sign Language",
        "A6": "Amharic",
        "A7": "Arabic",
        "A8": "Armenian",
        "A9": "Assamese",
        "B0": "Assyrian",
        "B1": "Azerbaijani",
        "B2": "Bashkir",
        "B3": "Basque",
        "B4": "Belarusian",
        "B5": "Bengali;Bangla",
        "B6": "Bihari",
        "B7": "Bislama",
        "B8": "Bosnian",
        "B9": "Breton",
        "C0": "Bulgarian",
        "C1": "Burmese",
        "C2": "Cambodian",
        "C3": "Cantonese",
        "C4": "Cape Verdean Creole",
        "C5": "Catalan",
        "C6": "Cebuano",
        "C7": "Chaldean",
        "C8": "Chechen",
        "C9": "Cherokee",
        "D0": "Chinese",
        "D1": "Corsican",
        "D2": "Creole",
        "D3": "Croatian",
        "D4": "Czech",
        "D5": "Danish",
        "D6": "Dutch",
        "D7": "Dzongkha",
        "D8": "Eastern Aramaic",
        "D9": "Egyptian Arabic",
        "E0": "Esperanto",
        "E1": "Estonian",
        "E2": "Faroese",
        "E3": "Fiji",
        "E4": "Filipino",
        "E5": "Finnish",
        "E6": "Flemish",
        "E7": "French",
        "E8": "Frisian",
        "E9": "Galician",
        "F0": "Georgian",
        "F1": "German",
        "F2": "Greek",
        "F3": "Greenlandic",
        "F4": "Guarani",
        "F5": "Gujarati",
        "F6": "Haitian Creole",
        "F7": "Hakka",
        "F8": "Hausa",
        "F9": "Hebrew",
        "G0": "Hindi",
        "G1": "Hmong",
        "G2": "Hungarian",
        "G3": "Icelandic",
        "G4": "Ilokano",
        "G5": "Indonesian",
        "G6": "Interlingua",
        "G7": "Interlingue",
        "G8": "Inuktitut",
        "G9": "Inupiaq",
        "H0": "Irish",
        "H1": "Italian",
        "H2": "Iu Mien",
        "H3": "Jamaican Patois",
        "H4": "Japanese",
        "H5": "Javanese",
        "H6": "Kannada",
        "H7": "Kashmiri",
        "H8": "Kazakh",
        "H9": "Khmer",
        "I0": "Kinyarwanda",
        "I1": "Kirghiz",
        "I2": "Kirundi",
        "I3": "Korean",
        "I4": "Kurdish",
        "I5": "Lao",
        "I6": "Latin",
        "I7": "Latvian",
        "I8": "Lebanese",
        "I9": "Lingala",
        "J0": "Lithuanian",
        "J1": "Lombard",
        "J2": "Macedonian",
        "J3": "Malagasy",
        "J4": "Malay",
        "J5": "Malayalam",
        "J6": "Maltese",
        "J7": "Mandarin",
        "J8": "Maori",
        "J9": "Marathi",
        "K0": "Maung",
        "K1": "Min",
        "K2": "Moldavian",
        "K3": "Mongolian",
        "K4": "Native American Dialect",
        "K5": "Nauru",
        "K6": "Nepali",
        "K7": "Norwegian",
        "K8": "Occitan",
        "K9": "Oriya",
        "L0": "Pashto;Pushto",
        "L1": "Persian (Farsi)",
        "L2": "Polish",
        "L3": "Portuguese",
        "L4": "Punjabi",
        "L5": "Quechua",
        "L6": "Rhaeto-Romance",
        "L7": "Romanian",
        "L8": "Russian",
        "L9": "Samoan",
        "M0": "Sangho",
        "M1": "Sanskrit",
        "M2": "Scot Gaelic",
        "M3": "Scots",
        "M4": "Serbian",
        "M5": "Serbo-Croatian",
        "M6": "Sesotho",
        "M7": "Setswana",
        "M8": "Shona",
        "M9": "Sindhi",
        "N0": "Singhalese",
        "N1": "Siswati",
        "N2": "Slovak",
        "N3": "Slovenian",
        "N4": "Somali",
        "N5": "Spanish",
        "N6": "Sundanese",
        "N7": "Swahili",
        "N8": "Swedish",
        "N9": "Tagalog",
        "O0": "Taiwanese",
        "O1": "Tajik",
        "O2": "Tamil",
        "O3": "Tatar",
        "O4": "Telugu",
        "O5": "Thai",
        "O6": "Tibetan",
        "O7": "Tigrinya",
        "O8": "Tonga",
        "O9": "Tsonga",
        "P0": "Tulu",
        "P1": "Turkish",
        "P2": "Turkmen",
        "P3": "Twi",
        "P4": "Uigur",
        "P5": "Ukrainian",
        "P6": "Urdu",
        "P7": "Uzbek",
        "P8": "Vietnamese",
        "P9": "Volapuk",
        "Q0": "Welsh",
        "Q1": "Wolof",
        "Q2": "Xhosa",
        "Q3": "Yiddish",
        "Q4": "Yoruba",
        "Q5": "Zhuang",
        "Q6": "Zulu"
    },
    "privilege": {
        "1": "Nationwide Children's Hospital (NCH)",
        "2": "NCH Westerville Surgery Center",
        "3": "Partners For Kids (PHO)"
    },
    "state": {
        "A0": "Non-US State",
        "A1": "AA",
        "A2": "AE",
        "A3": "AK",
        "A4": "AL",
        "A5": "AP",
        "A6": "AR",
        "A7": "AZ",
        "A8": "CA",
        "A9": "CO",
        "B1": "CT",
        "B2": "DC",
        "B3": "DE",
        "B4": "FL",
        "B5": "FM",
        "B6": "GA",
        "B7": "GU",
        "B8": "HI",
        "B9": "IA",
        "C1": "ID",
        "C2": "IL",
        "C3": "IN",
        "C4": "KS",
        "C5": "KY",
        "C6": "LA",
        "C7": "MA",
        "C8": "MD",
        "C9": "ME",
        "D1": "MH",
        "D2": "MI",
        "D3": "MN",
        "D4": "MO",
        "D5": "MP",
        "D6": "MS",
        "D7": "MT",
        "D8": "NC",
        "D9": "ND",
        "E1": "NE",
        "E2": "NH",
        "E3": "NJ",
        "E4": "NM",
        "E5": "NV",
        "E6": "NY",
        "E7": "OH",
        "E8": "OK",
        "E9": "OR",
        "F1": "PA",
        "F2": "PR",
        "F3": "PW",
        "F4": "RI",
        "F5": "SC",
        "F6": "SD",
        "F7": "TN",
        "F8": "TX",
        "F9": "UT",
        "G0": "VA",
        "G1": "VI",
        "G2": "VT",
        "G3": "WA",
        "G4": "WI",
        "G5": "WV",
        "G6": "WY"
    },
    "entity": {
        "1": "Children's Anesthesia Associates",
        "2": "Children's Surgical Associates",
        "3": "Children's Physical Medicine/Rehabilitation Physicians",
        "4": "Nationwide Children's Hospital",
        "5": "Children's Psychiatrists",
        "6": "Pediatric Academic Association",
        "7": "Children's Radiological Institute",
        "8": "Pediatric Pathology Associates of Columbus"
    },
    "country": {
        "A0": "United States",
        "A1": "Afghanistan",
        "A2": "Albania",
        "A3": "Algeria",
        "A4": "Andorra",
        "A5": "Angola",
        "A6": "Antigua and Barbuda",
        "A7": "Argentina",
        "A8": "Armenia",
        "A9": "Australia",
        "B0": "Austria",
        "B1": "Azerbaijan",
        "B2": "Bahamas",
        "B3": "Bahrain",
        "B4": "Bangladesh",
        "B5": "Barbados",
        "B6": "Belarus",
        "B7": "Belgium",
        "B8": "Belize",
        "B9": "Benin",
        "C0": "Bhutan",
        "C1": "Bolivia",
        "C2": "Bosnia and Herzegovina",
        "C3": "Botswana",
        "C4": "Brazil",
        "C5": "Brunei Darussalam",
        "C6": "Bulgaria",
        "C7": "Burkina Faso",
        "C8": "Burundi",
        "C9": "Cambodia",
        "D0": "Cameroon",
        "D1": "Canada",
        "D2": "Cape Verda",
        "D3": "Central African Republic",
        "D4": "Chad",
        "D5": "Chile",
        "D6": "China",
        "D7": "Colombia",
        "D8": "Comoros",
        "D9": "Congo",
        "E0": "Costa Rica",
        "E1": "Cote D'Ivoire",
        "E2": "Croatia",
        "E3": "Cuba",
        "E4": "Cyprus",
        "E5": "Czech Republic",
        "E8": "Denmark",
        "E9": "Djibouti",
        "F0": "Dominica",
        "F1": "Dominican Republic",
        "F2": "Ecuador",
        "F3": "Egypt",
        "F4": "El Salvador",
        "F5": "Equatorial Guinea",
        "F6": "Eritrea",
        "F7": "Estonia",
        "F8": "Ethiopia",
        "F9": "Falkland Islands (Malvinas)",
        "G0": "Fiji",
        "G1": "Finland",
        "G2": "France",
        "G3": "Gabon",
        "G4": "Gambia",
        "G5": "Georgia",
        "G6": "Germany",
        "G7": "Ghana",
        "G8": "Greece",
        "G9": "Grenada",
        "H0": "Guatemala",
        "H1": "Guinea",
        "H2": "Guinea-Bissau",
        "H3": "Guyana",
        "H4": "Haiti",
        "H5": "Honduras",
        "H6": "Hungary",
        "H7": "Iceland",
        "H8": "India",
        "H9": "Indonesia",
        "I0": "Iran",
        "I1": "Iraq",
        "I2": "Ireland",
        "I3": "Israel",
        "I4": "Italy",
        "I5": "Jamaica",
        "I6": "Japan",
        "I7": "Jordan",
        "I8": "Kazakhstan",
        "I9": "Kenya",
        "J0": "Kiribati",
        "J1": "Kuwait",
        "J2": "Kyrgyzstan",
        "J3": "Laos",
        "J4": "Latvia",
        "J5": "Lebanon",
        "J6": "Lesotho",
        "J7": "Liberia",
        "J8": "Libya",
        "J9": "Liechtenstein",
        "K0": "Lithuania",
        "K1": "Luxembourg",
        "K2": "Madagascar",
        "K3": "Malawi",
        "K4": "Malaysia",
        "K5": "Maldives",
        "K6": "Mali",
        "K7": "Malta",
        "K8": "Marshall Islands",
        "K9": "Mauritania",
        "L0": "Mauritius",
        "L1": "Mexico",
        "L2": "Micronesia",
        "L3": "Monaco",
        "L4": "Mongolia",
        "L5": "Montenegro",
        "L6": "Morocco",
        "L7": "Mozambique",
        "L8": "Myanmar",
        "L9": "Namibia",
        "M0": "Nauru",
        "M1": "Nepal",
        "M2": "Netherlands",
        "M3": "New Zealand",
        "M4": "Nicaragua",
        "M5": "Niger",
        "M6": "Nigeria",
        "M7": "Northern Mariana Islands",
        "M8": "Norway",
        "M9": "Oman",
        "N0": "Pakistan",
        "N1": "Palau",
        "N2": "Panama",
        "N3": "Papua New Guinea",
        "N4": "Paraguay",
        "N5": "Peru",
        "N6": "Philippines",
        "N7": "Poland",
        "N8": "Portugal",
        "N9": "Qatar",
        "O0": "Reunion",
        "O2": "Romania",
        "O3": "Russian Federation",
        "O4": "Rwanda",
        "O5": "Saint Kitts and Nevis",
        "O6": "Saint Lucia",
        "O7": "Saint Vincent and the Grenadines",
        "O8": "Samoa",
        "O9": "San Marino",
        "P0": "Sao Tome and Principe",
        "P1": "Saudi Arabia",
        "P2": "Senegal",
        "P3": "Serbia",
        "P4": "Seychelles",
        "P5": "Sierra Leone",
        "P6": "Singapore",
        "P7": "Slovakia",
        "P8": "Slovenia",
        "P9": "Solomon Islands",
        "Q0": "Somalia",
        "Q1": "South Africa",
        "Q2": "South Georgia and the South Sandwich Islands",
        "Q3": "Spain",
        "Q4": "Sri Lanka",
        "Q5": "Sudan",
        "Q6": "Suriname",
        "Q7": "Sweden",
        "Q8": "Switzerland",
        "Q9": "Syria",
        "R0": "Tajikistan",
        "R1": "Thailand",
        "R2": "Togo",
        "R3": "Tokelau",
        "R4": "Tonga",
        "R5": "Trinidad and Tobago",
        "R6": "Tunisia",
        "R7": "Turkey",
        "R8": "Turkmenistan",
        "R9": "Tuvalu",
        "S0": "Uganda",
        "S1": "Ukraine",
        "S2": "United Arab Emirates",
        "S3": "United Kingdom",
        "S4": "United States Minor Outlying Islands",
        "S5": "Uruguay",
        "S6": "Uzbekistan",
        "S7": "Vanuatu",
        "S8": "Venezuela",
        "S9": "Viet Nam",
        "T0": "Yemen",
        "T1": "Zambia",
        "T2": "Zimbabwe",
        "A3A0": "American Samoa",
        "A5A0": "Anguilla",
        "A5A1": "Antarctica",
        "A8A0": "Aruba",
        "B9A0": "Bermuda",
        "C3A0": "Bouvet Island",
        "C4A0": "British Indian Ocean Territory",
        "D2A0": "Cayman Islands",
        "D6A0": "Christmas Island",
        "D6A1": "Cocos (Keeling) Islands",
        "D9A0": "Congo, Democratic Republic of the",
        "D9A1": "Cook Islands",
        "F1A0": "East Timor",
        "F9A0": "Faroe Islands",
        "G2A0": "France, Metropolitan",
        "G2A1": "French Guiana",
        "G2A2": "French Polynesia",
        "G2A3": "French Southern Territories",
        "G4A0": "Gaza Strip",
        "G7A0": "Gibraltar",
        "G8A0": "Greenland",
        "G9A0": "Guadeloupe",
        "G9A1": "Guam",
        "H0A0": "Guernsey",
        "H4A0": "Heard Island and McDonald Islands",
        "H5A0": "Hong Kong",
        "I2A0": "Isle of Man",
        "I6A0": "Jersey",
        "J0A0": "Korea, North",
        "J0A1": "Korea, South",
        "J0A2": "Kosovo",
        "K1A0": "Macau",
        "K1A1": "Macedonia",
        "K8A0": "Martinique",
        "L0A0": "Mayotte",
        "L2A0": "Moldova",
        "L5A0": "Montserrat",
        "M6A0": "Niue",
        "M6A1": "Norfolk Island",
        "N1A0": "Palestinian Territory",
        "N6A0": "Pitcairn",
        "N8A0": "Puerto Rico",
        "O4A0": "Saint Barthelemy",
        "O4A1": "Saint Helena",
        "O6A0": "Saint Pierre and Miquelon",
        "P1A0": "Scotland",
        "Q6A0": "Svalbard and Jan Mayen",
        "Q6A1": "Swaziland",
        "Q9A0": "Taiwan",
        "R0A0": "Tanzania",
        "R8A0": "Turks and Caicos Islands",
        "S7A0": "Vatican City State (Holy See)",
        "S9A0": "Virgin Islands, British",
        "S9A1": "Virgin Islands, U.S.",
        "S9A2": "Wallis and Futuna",
        "S9A3": "West Bank",
        "S9A4": "Western Sahara",
        "T0A0": "Yugoslavia"
    },
    "specialty": {
        "A0": "ABDOMINAL RADIOLOGY (RADIOLOGY-DIAGNOSTIC)",
        "A1": "ABDOMINAL SURGERY",
        "A2": "ADDICTION MEDICINE (PSYCHIATRY)",
        "A3": "ADDICTION PSYCHIATRY (PSYCHIATRY)",
        "A4": "ADOLESCENT MEDICINE (FAMILY MEDICINE)",
        "A5": "ADOLESCENT MEDICINE (INTERNAL MEDICINE)",
        "A6": "ADOLESCENT MEDICINE (PEDIATRICS)",
        "A7": "ADULT CARDIOTHORACIC ANESTHESIOLOGY (ANESTHESIOLOGY)",
        "A8": "ADULT CONGENITAL HEART DISEASE (INTERNAL MEDICINE)",
        "A9": "ADULT RECONSTRUCTIVE ORTHOPAEDICS (ORTHOPAEDIC SURGERY)",
        "B0": "ADVANCED HEART FAILURE AND TRANSPLANT CARDIOLOGY (INTERNAL MEDICINE)",
        "B1": "AEROSPACE MEDICINE",
        "B2": "ALLERGY",
        "B3": "ALLERGY AND IMMUNOLOGY",
        "B4": "ANATOMIC PATHOLOGY",
        "B5": "ANESTHESIOLOGY",
        "B6": "ANESTHESIOLOGY CRITICAL CARE MEDICINE (EMERGENCY MEDICINE)",
        "B7": "BLOOD BANKING/TRANSFUSION MEDICINE (PATHOLOGY)",
        "B8": "BRAIN INJURY MEDICINE (NEUROLOGY)",
        "B9": "BRAIN INJURY MEDICINE (PHYSICAL MEDICINE & REHABILITATION)",
        "C0": "CARDIOTHORACIC RADIOLOGY",
        "C1": "CARDIOVASCULAR DISEASE (INTERNAL MEDICINE)",
        "C2": "CHEMICAL PATHOLOGY (PATHOLOGY)",
        "C3": "CHILD & ADOLESCENT PSYCHIATRY (PSYCHIATRY)",
        "C4": "CHILD ABUSE PEDIATRICS (PEDIATRICS)",
        "C5": "CHILD NEUROLOGY",
        "C6": "CLINICAL & LABORATORY DERMATOLOGICAL IMMUNOLOGY",
        "C7": "CLINICAL & LABORATORY IMMUNOLOGY (PEDIATRICS)",
        "C8": "CLINICAL AND LABORATORY IMMUNOLOGY (INTERNAL MEDICINE)",
        "C9": "CLINICAL BIOCHEMICAL GENETICS",
        "D0": "CLINICAL CARDIAC ELECTROPHYSIOLOGY (INTERNAL MEDICINE)",
        "D1": "CLINICAL CYTOGENETICS",
        "D2": "CLINICAL GENETICS",
        "D3": "CLINICAL INFORMATICS (ANESTHESIOLOGY)",
        "D4": "CLINICAL INFORMATICS (EMERGENCY MEDICINE)",
        "D5": "CLINICAL INFORMATICS (FAMILY MEDICINE)",
        "D6": "CLINICAL INFORMATICS (INTERNAL MEDICINE)",
        "D7": "CLINICAL INFORMATICS (PATHOLOGY)",
        "D8": "CLINICAL INFORMATICS (PEDIATRICS)",
        "D9": "CLINICAL INFORMATICS (PREVENTIVE MEDICINE)",
        "E0": "CLINICAL LABORATORY IMMUNOLOGY (ALLERGY & IMMUNOLOGY)",
        "E1": "CLINICAL MOLECULAR GENETICS",
        "E2": "CLINICAL NEUROPHYSIOLOGY (NEUROLOGY)",
        "E3": "CLINICAL PATHOLOGY",
        "E4": "CLINICAL PHARMACOLOGY",
        "E5": "COLON AND RECTAL SURGERY",
        "E6": "COMPLEX FAMILY PLANNING (OBSTETRICS AND GYNECOLOGY)",
        "E7": "COMPLEX GENERAL SURGICAL ONCOLOGY (GENERAL SURGERY)",
        "E8": "CONGENITAL CARDIAC SURGERY (THORACIC SURGERY)",
        "E9": "CONSULTATION-LIAISON PSYCHIATRY (PSYCHIATRY)",
        "F0": "COSMETIC SURGERY",
        "F1": "CRANIOFACIAL SURGERY (PLASTIC SURGERY)",
        "F2": "CRITICAL CARE MEDICINE (ANESTHESIOLOGY)",
        "F3": "CRITICAL CARE MEDICINE (EMERGENCY MEDICINE)",
        "F4": "CRITICAL CARE MEDICINE (INTERNAL MEDICINE)",
        "F5": "CRITICAL CARE MEDICINE (OBSTETRICS & GYNECOLOGY)",
        "F6": "CYTOPATHOLOGY (PATHOLOGY)",
        "F7": "DERMATOLOGIC SURGERY",
        "F8": "DERMATOLOGY",
        "F9": "DERMATOPATHOLOGY (DERMATOLOGY)",
        "G0": "DEVELOPMENTAL-BEHAVIORAL PEDIATRICS (PEDIATRICS)",
        "G1": "DIABETES",
        "G2": "DIAGNOSTIC RADIOLOGY",
        "G3": "DIAGNOSTIC RADIOLOGY/NUCLEAR MEDICINE",
        "G4": "EMERGENCY MEDICAL SERVICES (EMERGENCY MEDICINE)",
        "G5": "EMERGENCY MEDICINE",
        "G6": "EMERGENCY MEDICINE/ANESTHESIOLOGY",
        "G7": "EMERGENCY MEDICINE/FAMILY MEDICINE",
        "G8": "ENDOCRINOLOGY, DIABETES & METABOLISM (INTERNAL MEDICINE)",
        "G9": "ENDOVASCULAR SURGICAL NEURORADIOLOGY (NEUROLOGICAL SURGERY)",
        "H0": "ENDOVASCULAR SURGICAL NEURORADIOLOGY (NEUROLOGY)",
        "H1": "ENDOVASCULAR SURGICAL NEURORADIOLOGY (RADIOLOGY)",
        "H2": "EPIDEMIOLOGY",
        "H3": "EPILEPSY (NEUROLOGY)",
        "H4": "FACIAL PLASTIC SURGERY",
        "H5": "FAMILY MEDICINE",
        "H6": "FAMILY MEDICINE/PREVENTIVE MEDICINE",
        "H7": "FEMALE PELVIC MEDICINE & RECONSTRUCTIVE SURGERY (UROLOGY)",
        "H8": "FEMALE PELVIC MEDICINE AND RECONSTRUCTIVE SURGERY (OBSTETRICS & GYNECOLOGY)",
        "H9": "FOOT AND ANKLE ORTHOPAEDICS (ORHTOPAEDIC SURGERY)",
        "I0": "FORENSIC PATHOLOGY (PATHOLOGY)",
        "I1": "FORENSIC PSYCHIATRY (PSYCHIATRY)",
        "I2": "GASTROENTEROLOGY (INTERNAL MEDICINE)",
        "I3": "GENERAL PRACTICE",
        "I4": "GENERAL PREVENTIVE MEDICINE",
        "I5": "GENERAL SURGERY",
        "I6": "GERIATRIC MEDICINE (FAMILY MEDICINE)",
        "I7": "GERIATRIC MEDICINE (INTERNAL MEDICINE)",
        "I8": "GERIATRIC PSYCHIATRY (PSYCHIATRY)",
        "I9": "GYNECOLOGIC ONCOLOGY (OBSTETRICS & GYNECOLOGY)",
        "J0": "GYNECOLOGY",
        "J1": "HAND SURGERY",
        "J2": "HAND SURGERY (GENERAL SURGERY)",
        "J3": "HAND SURGERY (ORTHOPAEDIC SURGERY)",
        "J4": "HAND SURGERY (PLASTIC SURGERY)",
        "J5": "HEAD AND NECK SURGERY",
        "J6": "HEMATOLOGY & MEDICAL ONCOLOGY (INTERNAL MEDICINE)",
        "J7": "HEMATOLOGY (INTERNAL MEDICINE)",
        "J8": "HEMATOPATHOLOGY (PATHOLOGY)",
        "J9": "HEPATOLOGY",
        "K0": "HOSPICE & PALLIATIVE MEDICINE",
        "K1": "HOSPICE & PALLIATIVE MEDICINE (ANESTHESIOLOGY)",
        "K2": "HOSPICE & PALLIATIVE MEDICINE (EMERGENCY MEDICINE)",
        "K3": "HOSPICE & PALLIATIVE MEDICINE (FAMILY MEDICINE)",
        "K4": "HOSPICE & PALLIATIVE MEDICINE (INTERNAL MEDICINE)",
        "K5": "HOSPICE & PALLIATIVE MEDICINE (OBSTETRICS & GYNECOLOGY)",
        "K6": "HOSPICE & PALLIATIVE MEDICINE (PEDIATRICS)",
        "K7": "HOSPICE & PALLIATIVE MEDICINE (PHYSICAL MEDICINE & REHABILITATION)",
        "K8": "HOSPICE & PALLIATIVE MEDICINE (PSYCHIATRY & NEUROLOGY)",
        "K9": "HOSPICE & PALLIATIVE MEDICINE (RADIOLOGY)",
        "L0": "HOSPICE & PALLIATIVE MEDICINE (SURGERY)",
        "L1": "HOSPITALIST",
        "L2": "IMMUNOLOGY",
        "L3": "INFECTIOUS DISEASE (INTERNAL MEDICINE)",
        "L4": "INTERNAL MED/EMERGENCY MED/CRITICAL CARE MED",
        "L5": "INTERNAL MED/PHYS MED AND REHABILITATION",
        "L6": "INTERNAL MED/PSYCHIATRY",
        "L7": "INTERNAL MEDICINE",
        "L8": "INTERNAL MEDICINE/ANESTHESIOLOGY",
        "L9": "INTERNAL MEDICINE/DERMATOLOGY",
        "M0": "INTERNAL MEDICINE/EMERGENCY MEDICINE",
        "M1": "INTERNAL MEDICINE/FAMILY MEDICINE",
        "M2": "INTERNAL MEDICINE/MEDICAL GENETICS & GENOMICS",
        "M3": "INTERNAL MEDICINE/NEUROLOGY",
        "M4": "INTERNAL MEDICINE/NUCLEAR MEDICINE",
        "M5": "INTERNAL MEDICINE/PEDIATRICS",
        "M6": "INTERNAL MEDICINE/PREVENTIVE MEDICINE",
        "M7": "INTERVENTIONAL CARDIOLOGY (INTERNAL MEDICINE)",
        "M8": "INTERVENTIONAL RADIOLOGY - INDEPENDENT",
        "M9": "INTERVENTIONAL RADIOLOGY - INTEGRATED",
        "N0": "LEGAL MEDICINE",
        "N1": "MATERNAL AND FETAL MEDICINE",
        "N2": "MEDICAL BIOCHEMICAL GENETICS (MEDICAL GENETICS)",
        "N3": "MEDICAL GENETICS",
        "N4": "MEDICAL GENETICS AND GENOMICS/MATERNAL-FETAL MEDICINE",
        "N5": "MEDICAL MANAGEMENT",
        "N6": "MEDICAL MICROBIOLOGY (PATHOLOGY)",
        "N7": "MEDICAL ONCOLOGY (INTERNAL MEDICINE)",
        "N8": "MEDICAL PHYSICS",
        "N9": "MEDICAL TOXICOLOGY (EMERGENCY MEDICINE)",
        "O0": "MEDICAL TOXICOLOGY (PEDIATRICS)",
        "O1": "MEDICAL TOXICOLOGY (PREVENTIVE MEDICINE)",
        "O2": "MICROGRAPHIC SURGERY AND DERMATOLOGIC ONCOLOGY (DERMATOLOGY)",
        "O3": "MOLECULAR GENETIC PATHOLOGY (MEDICAL GENETICS)",
        "O4": "MOLECULAR GENETIC PATHOLOGY (PATHOLOGY AND MEDICAL GENETICS)",
        "O5": "MUSCULOSKELETAL ONCOLOGY (ORTHOPAEDIC SURGERY)",
        "O6": "MUSCULOSKELETAL RADIOLOGY (RADIOLOGY-DIAGNOSTIC)",
        "O7": "NEONATAL-PERINATAL MEDICINE (PEDIATRICS)",
        "O8": "NEPHROLOGY",
        "O9": "NEUROCRITICAL CARE",
        "P0": "NEURODEVELOPMENTAL DISABILITIES (NEUROLOGY)",
        "P1": "NEURODEVELOPMENTAL DISABILITIES (PEDIATRICS)",
        "P2": "NEUROLOGICAL SURGERY",
        "P3": "NEUROLOGY",
        "P4": "NEUROLOGY/DIAGNOSTIC RADIOLOGY/NEURORADIOLOGY",
        "P5": "NEUROLOGY/NUCLEAR MEDICINE",
        "P6": "NEUROLOGY/PHYSICAL MEDICINE AND REHABILITATION",
        "P7": "NEUROMUSCULAR MEDICINE (NEUROLOGY)",
        "P8": "NEUROMUSCULAR MEDICINE (PHYSICAL MEDICINE & REHABILITATION)",
        "P9": "NEUROPATHOLOGY (PATHOLOGY)",
        "Q0": "NEUROPSYCHIATRY",
        "Q1": "NEURORADIOLOGY (RADIOLOGY-DIAGNOSTIC)",
        "Q2": "NEUROTOLOGY (OTOLARYNGOLOGY)",
        "Q3": "NUCLEAR CARDIOLOGY",
        "Q4": "NUCLEAR MEDICINE",
        "Q5": "NUCLEAR RADIOLOGY (RADIOLOGY-DIAGNOSTIC)",
        "Q6": "NUTRITION",
        "Q7": "OBSTETRIC ANESTHESIOLOGY (ANESTHESIOLOGY)",
        "Q8": "OBSTETRICS",
        "Q9": "OBSTETRICS & GYNECOLOGY",
        "R0": "OCCUPATIONAL MEDICINE",
        "R1": "OPHTHALMIC PLASTIC AND RECONSTRUCTIVE SURGERY (OPHTHALMOLOGY)",
        "R2": "OPHTHALMOLOGY",
        "R3": "ORAL & MAXILLOFACIAL SURGERY",
        "R4": "ORTHOPAEDIC SURGERY",
        "R5": "ORTHOPAEDIC SURGERY OF THE SPINE (ORTHOPAEDIC SURGERY)",
        "R6": "ORTHOPAEDIC TRAUMA (ORTHOPAEDIC SURGERY)",
        "R7": "OSTEOPATHIC MANIPULATIVE MEDICINE",
        "R8": "OSTEOPATHIC NEUROMUSCULOSKELETAL MEDICINE",
        "R9": "OTHER SPECIALTY",
        "S0": "OTOLARYNGOLOGY-HEAD AND NECK SURGERY",
        "S1": "PAIN MANAGEMENT",
        "S2": "PAIN MEDICINE",
        "S3": "PAIN MEDICINE (ANESTHESIOLOGY)",
        "S4": "PAIN MEDICINE (NEUROLOGY)",
        "S5": "PAIN MEDICINE (PHYSICAL MEDICINE & REHABILITATION)",
        "S6": "PAIN MEDICINE (PSYCHIATRY)",
        "S7": "PALLIATIVE MEDICINE",
        "S8": "PATHOLOGY-ANATOMIC & CLINICAL",
        "S9": "PEDIATRIC ALLERGY",
        "T0": "PEDIATRIC ANESTHESIOLOGY (ANESTHESIOLOGY)",
        "T1": "PEDIATRIC CARDIAC ANESTHESIOLOGY (ANESTHESIOLOGY)",
        "T2": "PEDIATRIC CARDIOLOGY (PEDIATRICS)",
        "T3": "PEDIATRIC CARDIOTHORACIC SURGERY",
        "T4": "PEDIATRIC CRITICAL CARE MEDICINE (PEDIATRICS)",
        "T5": "PEDIATRIC DERMATOLOGY (DERMATOLOGY)",
        "T6": "PEDIATRIC EMERGENCY MED (EMERGENCY MED)",
        "T7": "PEDIATRIC EMERGENCY MEDICINE (PEDIATRICS)",
        "T8": "PEDIATRIC ENDOCRINOLOGY (PEDIATRICS)",
        "T9": "PEDIATRIC GASTROENTEROLOGY (PEDIATRICS)",
        "U0": "PEDIATRIC HEMATOLOGY-ONCOLOGY (PEDIATRICS)",
        "U1": "PEDIATRIC HOSPITAL MEDICINE (PEDIATRICS)",
        "U2": "PEDIATRIC INFECTIOUS DISEASES (PEDIATRICS)",
        "U3": "PEDIATRIC NEPHROLOGY (PEDIATRICS)",
        "U4": "PEDIATRIC OPHTHALMOLOGY",
        "U5": "PEDIATRIC ORTHOPAEDICS (ORTHOPAEDIC SURGERY)",
        "U6": "PEDIATRIC OTOLARYNGOLOGY (OTOLARYNGOLOGY)",
        "U7": "PEDIATRIC PATHOLOGY (PATHOLOGY)",
        "U8": "PEDIATRIC PULMONOLOGY (PEDIATRICS)",
        "U9": "PEDIATRIC RADIOLOGY (RADIOLOGY-DIAGNOSTIC)",
        "V0": "PEDIATRIC REHABILITATION (PHYSICAL MEDICINE & REHABILITATION)",
        "V1": "PEDIATRIC RHEUMATOLOGY (PEDIATRICS)",
        "V2": "PEDIATRIC SPORTS MEDICINE (PEDIATRICS)",
        "V3": "PEDIATRIC SURGERY (GENERAL SURGERY)",
        "V4": "PEDIATRIC SURGERY (NEUROLOGY)",
        "V5": "PEDIATRIC TRANSPLANT HEPATOLOGY (PEDIATRICS)",
        "V6": "PEDIATRIC UROLOGY (UROLOGY)",
        "V7": "PEDIATRICS",
        "V8": "PEDIATRICS/ANESTHESIOLOGY",
        "V9": "PEDIATRICS/DERMATOLOGY",
        "W0": "PEDIATRICS/EMERGENCY MEDICINE",
        "W1": "PEDIATRICS/MEDICAL GENETICS & GENOMICS",
        "W2": "PEDIATRICS/PHYSICAL MEDICINE AND REHABILITATION",
        "W3": "PEDIATRICS/PSYCHIATRY/CHILD & ADOLESCENT PSYCHIATRY",
        "W4": "PHARMACEUTICAL MEDICINE",
        "W5": "PHLEBOLOGY",
        "W6": "PHYSICAL MEDICINE AND REHABILITATION",
        "W7": "PLASTIC SURGERY",
        "W8": "PLASTIC SURGERY WITHIN THE HEAD & NECK",
        "W9": "PLASTIC SURGERY WITHIN THE HEAD & NECK (OTOLARYNGOLOGY)",
        "X0": "PLASTIC SURGERY WITHIN THE HEAD & NECK (PLASTIC SURGERY)",
        "X1": "PROCTOLOGY",
        "X2": "PSYCHIATRY",
        "X3": "PSYCHIATRY/FAMILY MEDICINE",
        "X4": "PSYCHIATRY/NEUROLOGY",
        "X5": "PSYCHOANALYSIS",
        "X6": "PUBLIC HEALTH AND GENERAL PREVENTIVE MEDICINE",
        "X7": "PULMONARY & CRITICAL CARE MEDICINE (INTERNAL MEDICINE)",
        "X8": "PULMONARY DISEASE (INTERNAL MEDICINE)",
        "X9": "RADIATION ONCOLOGY",
        "Y0": "RADIOLOGICAL PHYSICS",
        "Y1": "RADIOLOGY",
        "Y2": "REGIONAL ANESTHESIOLOGY AND ACUTE PAIN MEDICINE (ANESTHESIOLOGY)",
        "Y3": "REPRODUCTIVE ENDOCRINOLOGY AND INFERTILITY (OBSTETRICS & GYNECOLOGY)",
        "Y4": "REPRODUCTIVE ENDOCRINOLOGY AND INFERTILITY/MEDICAL GENETICS AND GENOMICS",
        "Y5": "RHEUMATOLOGY (INTERNAL MEDICINE)",
        "Y6": "SELECTIVE PATHOLOGY (PATHOLOGY)",
        "Y7": "SLEEP MEDICINE",
        "Y8": "SLEEP MEDICINE (ANESTHESIOLOGY)",
        "Y9": "SLEEP MEDICINE (INTERNAL MEDICINE)",
        "Z0": "SLEEP MEDICINE (OTOLARYNGOLOGY)",
        "Z1": "SLEEP MEDICINE (PEDIATRICS)",
        "Z2": "SLEEP MEDICINE (PSYCHIATRY & NEUROLOGY)",
        "Z3": "SPINAL CORD INJURY MEDICINE (PHYSICAL MEDICINE & REHABILITATION)",
        "Z4": "SPORTS MEDICINE (EMERGENCY MEDICINE)",
        "Z5": "SPORTS MEDICINE (FAMILY MEDICINE)",
        "Z6": "SPORTS MEDICINE (INTERNAL MEDICINE)",
        "Z7": "SPORTS MEDICINE (ORTHOPAEDIC SURGERY)",
        "Z8": "SPORTS MEDICINE (PHYSICAL MEDICINE & REHABILITATION)",
        "Z9": "SURGICAL CRITICAL CARE (GENERAL SURGERY)",
        "Z9A0": "SURGICAL ONCOLOGY",
        "Z9A1": "THORACIC SURGERY",
        "Z9A2": "TRANSPLANT HEPATOLOGY (INTERNAL MEDICINE)",
        "Z9A3": "TRANSPLANT SURGERY",
        "Z9A4": "TRAUMATIC SURGERY",
        "Z9A5": "UNDERSEA & HYPERBARIC MEDICINE (EMERGENCY MEDICINE)",
        "Z9A6": "UNDERSEA & HYPERBARIC MEDICINE (PREVENTIVE MEDICINE)",
        "Z9A7": "UNSPECIFIED",
        "Z9A8": "URGENT CARE MEDICINE",
        "Z9A9": "UROLOGY",
        "Z9B0": "VASCULAR AND INTERVENTIONAL RADIOLOGY (RADIOLOGY-DIAGNOSTIC)",
        "Z9B1": "VASCULAR MEDICINE",
        "Z9B2": "VASCULAR NEUROLOGY (NEUROLOGY)",
        "Z9B3": "VASCULAR SURGERY (GENERAL SURGERY)"
    },
    "currentstatus": {
        "1": "Application In Progress",
        "2": "Current Member",
        "3": "Prior Member"
    },
    "dept": {
        "A1": "DEPARTMENT OF ANESTHESIOLOGY & PAIN MEDICINE",
        "A2": "Anesthesiology",
        "A3": "Advanced Pain for Anesthesiologists",
        "A4": "Pain Management for Non-Anesthesiologists",
        "A5": "Dental Anesthesiology",
        "A6": "DEPARTMENT OF CARDIOTHORACIC SURGERY",
        "A7": "DEPARTMENT OF DENTISTRY",
        "A8": "Oral & Naxillofacial Surgery",
        "A9": "Pediatric Dentistry",
        "B1": "Orthodontics",
        "B2": "Ambulatory - Dental Clinic Only",
        "B3": "DEPARTMENT OF HOSPTIAL MEDICINE",
        "B4": "Adult Hospital Medicine",
        "B5": "Hospital Pediatrics",
        "B6": "DEPARTMENT OF PATHOLOGY/LABORATORY MEDICINE",
        "B7": "Anatomical Pathology",
        "B8": "Clinical Pathology",
        "B9": "DEPARTMENT OF OPHTHALMOLOGY",
        "C1": "DEPARTMENT OF ORTHOPAEDICS",
        "C2": "Orthopaedics",
        "C3": "Podiatry Services",
        "C4": "DEPARTMENT OF OTOLARYNGOLOGY",
        "C5": "DEPARTMENT OF PEDIATRICS",
        "C6": "Adolescent Medicine",
        "C7": "Gastroenterology/Hepatology/Nutrition",
        "C8": "Allergy & Immunology",
        "C9": "General Pediatrics",
        "D1": "Ambulatory Pediatrics",
        "D2": "Hematology & Oncology",
        "D3": "Cardiology",
        "D4": "Infectious Diseases",
        "D5": "Child & Family Advocacy",
        "D6": "Molecular & Human Genetics",
        "D7": "Complex Care",
        "D8": "Neonatology",
        "D9": "Critical Care",
        "E1": "Nephrology",
        "E2": "Dermatology",
        "E3": "Neurology",
        "E4": "Developmental & Behavioral Pediatrics",
        "E5": "Physical Medicine",
        "E6": "Emergency Medicine",
        "E7": "Pulmonary Medicine",
        "E8": "Endocrinology",
        "E9": "Rheumatology",
        "F1": "Family Practice",
        "F2": "Toxicology",
        "F3": "DEPARTMENT OF PEDIATRIC SURGERY",
        "F4": "Abdominal Transplant Surgery",
        "F5": "Colorectal and Pelvic Reconstructive Surgery",
        "F6": "General Pediatric Surgery",
        "F7": "Neurosurgery",
        "F8": "Pediatric & Adolescent Gynecology & Obstetrics",
        "F9": "Plastic & Reconstructive Surgery",
        "G1": "Urology",
        "G2": "DEPARTMENT OF PSYCHIATRY & BEHAVIORAL HEALTH",
        "G3": "Psychiatry",
        "G4": "Psychology",
        "G5": "DEPARTMENT OF RADIOLOGY",
        "G6": "Diagnostic Radiology",
        "G7": "Nuclear Medicine"
    },
    "hospital": {
        "A0": "Ohio State University Hospitals",
        "A1": "Attending",
        "A2": "Courtesy A",
        "A3": "Courtesy B",
        "A4": "Physician Scholar",
        "A5": "Contract Physician",
        "A6": "Consulting",
        "A7": "The James Cancer Hospital",
        "A8": "Attending",
        "A9": "Attending w/o privileges",
        "B0": "Associate Attending",
        "B1": "Associate Attending w/o privileges",
        "B2": "Clinial Attending",
        "B3": "Contract Physician",
        "B4": "Consulting"
    },
    "expertise": {
        "A0": "Persons with physical disabilities",
        "A1": "Persons with chronic illness",
        "A2": "Persons with HIV/AIDS",
        "A3": "Persons with serious mental illness",
        "A4": "Homeless persons",
        "A5": "Persons who are deaf or hard of hearing",
        "A6": "Persons who are blind or visually impaired",
        "A7": "Persons with co-occuring disorders"
    },
    "referencetype": {
        "A0": "Current Program Director",
        "A1": "Department Chair"
    },
    "referencedegree": {
        "A0": "Doctor of Medical Science",
        "A1": "Doctor of Medicine",
        "A2": "Doctor of Osteopathic Medicine"
    },
    "trainingType": {
        "A0": "Specialty",
        "A1": "Sub-Specialty"
    },
    "certificateType": {
        "A0": "General",
        "A1": "Subspecialty"
    },
    "specialtySCA": {
        "A0": "Anesthesiology",
        "A1": "Anesthesiology - Critical Care Medicine",
        "A2": "Anesthesiology - Pediatric",
        "A3": "Bariatric Medicine",
        "A4": "Cardiology",
        "A5": "Cardiovascular",
        "A6": "Clinical Neurophysiology",
        "A7": "Colon Rectal Surgery",
        "A8": "Dental/Oral/Maxillofacial Surgery",
        "A9": "Dental/Oral/Maxillofacial Surgery - Pediatric",
        "B0": "Dermatology",
        "B1": "Diagnostic Radiology",
        "B2": "Electrophysiology",
        "B3": "Emergency Medicine",
        "B4": "Endocrinology - Reproductive",
        "B5": "Facial Plastic & Reconstructive Surgery",
        "B6": "Family Medicine",
        "B7": "Female Pelvic Medicine and Reconstructive Surgery",
        "B8": "Gastroenterology",
        "B9": "Gastroenterology - Pediatric",
        "C0": "General & Vascular Surgery",
        "C1": "General Surgery",
        "C2": "Gynecology",
        "C3": "Gynecologic Oncology",
        "C4": "Hospitalist",
        "C5": "Infectious Disease",
        "C6": "Internal Medicine",
        "C7": "Interventional Radiology",
        "C8": "Nephrology",
        "C9": "Neuro Spine Surgery",
        "D0": "Neurological Surgery",
        "D1": "Neurology",
        "D2": "Neurophysiologic Intraoperative Remote Monitoring",
        "D3": "Obstetrics & Gynecology",
        "D4": "Occuloplastics",
        "D5": "Oncology",
        "D6": "Ophthalmology",
        "D7": "Ophthalmology Retina",
        "D8": "Optometry",
        "D9": "Orthopaedic Hand Surgery",
        "E0": "Orthopaedic Joint Replacement",
        "E1": "Orthopaedic Spine",
        "E2": "Orthopaedic Sports Medicine",
        "E3": "Orthopaedic Surgery",
        "E4": "Orthopaedic Surgery - Pediatric",
        "E5": "Otolaryngology - Head & Neck Surgery",
        "E6": "Otolaryngology - Pediatric Ear/Nose/Throat",
        "E7": "Otolaryngology Ear/Nose/Throat",
        "E8": "Pain Management Anesthesiologist",
        "E9": "Pain Management Non-Anesthesiologist",
        "F0": "Pathology",
        "F1": "Physical Medicine & Rehabilitation",
        "F2": "Plastic & Reconstructive Surgery",
        "F3": "Podiatric Surgery",
        "F4": "Psychiatry",
        "F5": "Pulmonology",
        "F6": "Radiation Oncology",
        "F7": "Diagnostic Radiology",
        "F8": "Reconstructive Rearfoot/Ankle Surgery",
        "F9": "Reproductive Endocrinology and Infertility",
        "G0": "Sports Medicine",
        "G1": "Surgical Oncology",
        "G2": "Teleradiology",
        "G3": "Urology",
        "G4": "Urology - Pediatric",
        "G5": "Vascular & Thoracic Surgery",
        "G6": "Vascular Surgery"
    }
}