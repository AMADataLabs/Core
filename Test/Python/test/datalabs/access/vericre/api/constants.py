""" source: datalabs.access.vericre.api.constants """

# constant values for the Vericred API
SAMPLE_NOTIFICATION_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<monitorNotificationList xmlns="http://eprofiles.myama.com/core/">
    <notifications>
        <notificationId>999999</notificationId>
        <entityId>111111</entityId>
        <abmsUpdated>false</abmsUpdated>
        <deaUpdated>true</deaUpdated>
        <licenseUpdated>false</licenseUpdated>
        <npiUpdated>false</npiUpdated>
        <sanctionsUpdated>false</sanctionsUpdated>
        <medSchoolUpdated>true</medSchoolUpdated>
        <medTrainingUpdated>false</medTrainingUpdated>
        <notificationDate>2023-11-01</notificationDate>
        <acknowledgedDate xmlns:si="http://www.w3.org/2001/XMLSchema-instance" si:nil="true"/>
        <monitorExpirationDate>2025-11-01</monitorExpirationDate>
        <ssoUniqueId xmlns:si="http://www.w3.org/2001/XMLSchema-instance" si:nil="true"/>
        <customerNbr xmlns:si="http://www.w3.org/2001/XMLSchema-instance" si:nil="true"/>
        <email xmlns:si="http://www.w3.org/2001/XMLSchema-instance" si:nil="true"/>
    </notifications>
</monitorNotificationList>"""

SAMPLE_NOTIFICATION_JSON = """
    [{
        "notification_id": 999999,
        "entity_id": 111111,
        "abms_updated": false,
        "dea_updated": true,
        "license_updated": false,
        "npi_updated": false,
        "sanctions_updated": false,
        "med_school_updated": true,
        "med_training_updated": false,
        "notification_date": "2023-11-01",
        "acknowledged_date": null,
        "monitor_expiration_date": "2025-11-01",
        "sso_unique_id": null,
        "customer_nbr":null,
        "email": null
    }]
"""

SAMPLE_ENTITY_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<monitorList xmlns="http://eprofiles.myama.com/core/">
    <entries>
        <entityId>11111</entityId>
        <monitorExpirationDate>2025-01-1</monitorExpirationDate>
    </entries>
    <entries>
        <entityId>22222</entityId>
        <monitorExpirationDate>2025-02-2</monitorExpirationDate>
    </entries>
    <entries>
        <entityId>33333</entityId>
        <monitorExpirationDate>2025-03-3</monitorExpirationDate>
    </entries>
</monitorList>"""

SAMPLE_ENTITY_JSON = """
[
  {
    "entity_id": 11111,
    "monitor_expiration_date": "2025-01-1"
  },
  {
    "entity_id": 22222,
    "monitor_expiration_date": "2025-02-2"
  },
  {
    "entity_id": 33333,
    "monitor_expiration_date": "2025-03-3"
  }
]
"""
