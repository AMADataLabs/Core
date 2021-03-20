import pandas as pd
from datetime import datetime
import os
import settings


def get_percent_change(val1, val2):
    if val1 == val2 == 0:
        return 0
    dif = 1.0 * abs(val1 - val2)
    return (100.0 * dif) / val1


class DBLReportValidation:
    def __init__(self):
        self.dbl_file_location = None
        self.prev_dbl_file_location = None
        self.log_file_directory = None
        self.log_file = None
        self.tab_validations = {}
        """
        self.tab_validations = {
            "ChangeFileAudit": {
                'status': ''
            },
            "ReportByFieldFrom SAS": {
                'status': ''
            },
            "ChangeByFieldCount": {
                'status': ''
            },
            "RecordActionExtract": {
                'status': ''
            },
            "ChangeByRecordCount": {
                'status': ''
            },
            "PE Counts": {
                'status': ''
            },
            "TOP Counts": {
                'status': ''
            },
            "TOP by PE": {
                'status': ''
            },
            "PrimSpecbyMPA": {
                'status': ''
            },
        }
        """
        self.supplement_number = None
        self.current_dls_file_read = None  # variable read from first tab, checked across multiple tabs

    def run(self):
        self._load_environment_variables()

        self.validate_tab1()
        self.validate_tab2()
        self.validate_tab3()
        self.validate_tab4()
        self.validate_tab5()
        self.validate_tab6()
        self.validate_tab7()
        self.validate_tab8()
        self.validate_tab9()

        self.write_log_file()

        return self.tab_validations

    def validate_tab1(self):
        """ChangeFileAudit"""
        tab_name = 'ChangeFileAudit'

        data = pd.read_excel(self.dbl_file_location, sheet_name=tab_name, header=None, index_col=0).dropna().T
        prev = pd.read_excel(self.prev_dbl_file_location, sheet_name=tab_name, header=None, index_col=0).dropna().T

        self.current_dls_file_read = data['CURRENT DLS FILE READ'].values[0]

        errors = []

        prev_dls_file_read = prev['CURRENT DLS FILE READ'].values[0]
        cur_prev_dls_file_read = data['PREVIOUS DLS FILE READ'].values[0]

        if prev_dls_file_read != cur_prev_dls_file_read:
            errors.append("CURRENT REPORT'S 'PREVIOUS DLS FILE READ' DOES NOT MATCH PREVIOUS REPORT'S 'CURRENT' COUNT")

        prev_supplement = prev['SUPPLEMENT NUMBER'].values[0]
        supplement = data['SUPPLEMENT NUMBER'].values[0]

        if prev_supplement + 1 != supplement:
            errors.append("SUPPLEMENT NUMBER HAS NOT CORRECTLY INCREMENTED FROM PREVIOUS REPORT")

        self.supplement_number = supplement

        self.tab_validations[tab_name] = {}

        if len(errors) == 0:
            self.tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self.tab_validations[tab_name]['status'] = 'FAILING'
            self.tab_validations[tab_name]['errors'] = errors

    def validate_tab2(self):
        """ReportByFieldFrom SAS"""
        tab_name = 'ReportByFieldFrom SAS'
        change_threshold = 10

        data = pd.read_excel(self.dbl_file_location, sheet_name=tab_name, header=None, index_col=0).T
        prev = pd.read_excel(self.prev_dbl_file_location, sheet_name=tab_name, header=None, index_col=0).T

        errors = []

        must_100 = ['MAILING NAME', 'MAILING NAME(LAST)', 'MAILING NAME(FIRST)']
        for field in must_100:
            if data[field].values[1] != 1:
                errors.append(f'FIELD - "{field}" - IS NOT 100%')

        for field in data.columns.values[1:-2]:
            val1 = prev[field].values[1]
            val2 = data[field].values[1]
            change = get_percent_change(val1, val2)
            if change >= change_threshold:
                errors.append(f'FIELD - "{field}" - CHANGED BY {change}% - {val1} TO {val2} - EXCEEDS THRESHOLD')

        obs_count = data['OBSERVATION COUNT'].values[0]
        if obs_count != self.current_dls_file_read:
            errors.append('OBSERVATION COUNT DOES NOT MATCH DLS FILE READ COUNT')
        supplement = data['SUPPLEMENT NUMBER'].values[0]
        if supplement != self.supplement_number:
            errors.append('SUPPLEMENT NUMBER DOES NOT MATCH')

        self.tab_validations[tab_name] = {}

        if len(errors) == 0:
            self.tab_validations['ReportByFieldFrom SAS']['status'] = 'PASSING'
        else:
            self.tab_validations['ReportByFieldFrom SAS']['status'] = 'FAILING'
            self.tab_validations['ReportByFieldFrom SAS']['errors'] = errors

    def validate_tab3(self):
        """ChangeByFieldCount"""
        tab_name = 'ChangeByFieldCount'
        data = pd.read_excel(self.dbl_file_location, sheet_name=tab_name, header=None, index_col=0).T
        # prev = pd.read_excel(self.prev_dbl_file_location, sheet_name=tab_name, header=None, index_col=0).T

        errors = []

        supplement = data['SUPPLEMENT NUMBER'].values[0]
        if supplement != self.supplement_number:
            errors.append('SUPPLEMENT NUMBER DOES NOT MATCH')

        self.tab_validations[tab_name] = {}

        if len(errors) == 0:
            self.tab_validations['ChangeByFieldCount']['status'] = 'PASSING'
        else:
            self.tab_validations['ChangeByFieldCount']['status'] = 'FAILING'
            self.tab_validations['ChangeByFieldCount']['errors'] = errors

    def validate_tab4(self):
        """RecordActionExtract"""
        tab_name = 'RecordActionExtract'

        data = pd.read_excel(self.dbl_file_location, sheet_name=tab_name, header=None, index_col=0).T
        # prev = pd.read_excel(self.prev_dbl_file_location, sheet_name=3, header=None, index_col=0).T

        errors = []

        for me in data.columns.values:
            if len(me) != 11 and me not in ['ME NUMBER', 'SUPPLEMENT NUMBER']:
                errors.append(f'ME # "{me}" IS NOT 11 CHARACTERS')
        add_deletes = set(data.T.reset_index().drop(0)[1].values[:-1])  # gets the set of values, should be ('A', 'D')
        for value in add_deletes:
            if value != 'A' and value != 'D':
                errors.append(f'ERRONEOUS ADD/DELETE VALUE FOUND - "{value}"')

        self.tab_validations[tab_name] = {}

        if len(errors) == 0:
            self.tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self.tab_validations[tab_name]['status'] = 'FAILING'
            self.tab_validations[tab_name]['errors'] = errors

    def validate_tab5(self):
        """ChangeByRecordCount"""
        tab_name = 'ChangeByRecordCount'

        data = pd.read_excel(self.dbl_file_location, sheet_name=tab_name, header=None, index_col=0).T
        # prev = pd.read_excel(self.prev_dbl_file_location, sheet_name=tab_name, header=None, index_col=0).T

        errors = []

        supplement = data['SUPPLEMENT NUMBER'].values[0]
        if supplement != self.supplement_number:
            errors.append('SUPPLEMENT NUMBER DOES NOT MATCH')

        self.tab_validations[tab_name] = {}

        if len(errors) == 0:
            self.tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self.tab_validations[tab_name]['status'] = 'FAILING'
            self.tab_validations[tab_name]['errors'] = errors

    def validate_tab6(self):
        """PE Counts"""
        tab_name = 'PE Counts'
        change_threshold = 5

        data = pd.read_excel(self.dbl_file_location, sheet_name=tab_name, header=1, index_col=0).T
        prev = pd.read_excel(self.prev_dbl_file_location, sheet_name=tab_name, header=1, index_col=0).T

        errors = []

        for pe in data.columns.values[:-1]:  # [:-1] to exclude Supplement Number (last value in series)
            val1 = prev[pe].values[1]
            val2 = data[pe].values[1]
            change = get_percent_change(val1, val2)
            if change >= change_threshold:
                errors.append(f'PE - "{pe}" - CHANGED BY {change}% - {val1} TO {val2} - EXCEEDS THRESHOLD')

        total = data['Grand Total'].values[1]
        if total != self.current_dls_file_read:
            errors.append('GRAND TOTAL != DLS FILE READ COUNT')

        self.tab_validations[tab_name] = {}

        if len(errors) == 0:
            self.tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self.tab_validations[tab_name]['status'] = 'FAILING'
            self.tab_validations[tab_name]['errors'] = errors

    def validate_tab7(self):
        """TOP Counts"""
        tab_name = 'TOP Counts'
        change_threshold = 5

        data = pd.read_excel(self.dbl_file_location, sheet_name=tab_name, header=1, index_col=0).T
        prev = pd.read_excel(self.prev_dbl_file_location, sheet_name=tab_name, header=1, index_col=0).T

        errors = []

        for top in data.columns.values[:-1]:  # exclude Supplement Number
            val1 = prev[top].values[1]
            val2 = data[top].values[1]
            change = get_percent_change(val1, val2)
            if change >= change_threshold:
                errors.append(f'TOP - "{top}" - CHANGED BY {change}% - {val1} TO {val2} - EXCEEDS THRESHOLD')

        total = data['Grand Total'].values[1]
        if total != self.current_dls_file_read:
            errors.append('GRAND TOTAL != DLS FILE READ COUNT')

        self.tab_validations[tab_name] = {}

        if len(errors) == 0:
            self.tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self.tab_validations[tab_name]['status'] = 'FAILING'
            self.tab_validations[tab_name]['errors'] = errors

    def validate_tab8(self):
        """TOP by PE"""
        tab_name = 'TOP by PE'
        change_threshold = 5

        data = pd.read_excel(self.dbl_file_location, sheet_name=tab_name, header=1, index_col=0).T
        prev = pd.read_excel(self.prev_dbl_file_location, sheet_name=tab_name, header=1, index_col=0).T

        errors = []

        # get previous values
        previous = {}
        for i, row in prev.iterrows():
            if len(i) == 3:
                previous[i] = row['Grand Total']

        # get current values
        current = {}
        for i, row in data.iterrows():
            if len(i) == 0:
                current[i] = row['Grand Total']

        # compare
        for val in current:
            if val in previous:
                val1 = previous[val]
                val2 = current[val]
                change = get_percent_change(val1, val2)
                if change >= change_threshold:
                    errors.append(f'PE - "{val}" - CHANGED BY {change}% - {val1} TO {val2} - EXCEEDS THRESHOLD')

        total = data['Grand Total'].values[-1]
        if total != self.current_dls_file_read:
            errors.append('GRAND TOTAL != DLS FILE READ COUNT')

        self.tab_validations[tab_name] = {}

        if len(errors) == 0:
            self.tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self.tab_validations[tab_name]['status'] = 'FAILING'
            self.tab_validations[tab_name]['errors'] = errors

    def validate_tab9(self):
        """PrimSpecbyMPA"""
        tab_name = 'PrimSpecbyMPA'
        change_threshold = 5

        data = pd.read_excel(self.dbl_file_location, sheet_name=tab_name, header=1, index_col=0).T
        prev = pd.read_excel(self.prev_dbl_file_location, sheet_name=tab_name, header=1, index_col=0).T

        errors = []

        # get previous values
        previous = {}
        for i, row in prev.iterrows():
            if i not in ['Grand Total', 'Description']:
                previous[i] = row['Grand Total']

        # get current values
        current = {}
        for i, row in data.iterrows():
            if i not in ['Grand Total', 'Description']:
                current[i] = row['Grand Total']

        # compare
        for val in current:
            if val in previous:
                val1 = previous[val]
                val2 = current[val]
                change = get_percent_change(val1, val2)
                if change >= change_threshold:
                    errors.append(f'Spec - "{val}" - CHANGED BY {change}% - {val1} TO {val2} - EXCEEDS THRESHOLD')

        # "unspecified counts must be LOWER than the unspecified counts in the 10th tab (SecSpecbyMPA)"
        unspecified = data.reset_index()[['index', 'US']]

        unspecified10 = pd.read_excel(
            self.dbl_file_location,
            sheet_name='SecSpecbyMPA',
            header=1,
            index_col=0
        ).T.reset_index()[
            ['index', 'US']
        ].rename(columns={'US': 'US-SEC'})
        unspecified = unspecified.merge(unspecified10, on='index', how='inner')
        unspecified['less'] = unspecified['US'] <= unspecified['US-SEC']

        failing = unspecified[~unspecified['less']]
        if len(failing) > 0:
            failing_codes = failing['SPEC Code'].values
            for code in failing_codes:
                errors.append(f'UNSPECIFIED PRIMARY COUNTS > UNSPECIFIED SECONDARY COUNTS - {code}')

        total = data['Grand Total'].values[-1]
        if total != self.current_dls_file_read:
            errors.append('GRAND TOTAL != DLS FILE READ COUNT')

        self.tab_validations[tab_name] = {}

        if len(errors) == 0:
            self.tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self.tab_validations[tab_name]['status'] = 'FAILING'
            self.tab_validations[tab_name]['errors'] = errors

    def validate_tab10(self):
        """SecSpecbyMPA"""
        tab_name = 'SecSpecbyMPA'
        change_threshold = 5

        data = pd.read_excel(self.dbl_file_location, sheet_name=tab_name, header=1, index_col=0).T
        prev = pd.read_excel(self.prev_dbl_file_location, sheet_name=tab_name, header=1, index_col=0).T

        errors = []

        # get previous values
        previous = {}
        for i, row in prev.iterrows():
            if i not in ['Grand Total', 'Description']:
                previous[i] = row['Grand Total']

        # get current values
        current = {}
        for i, row in data.iterrows():
            if i not in ['Grand Total', 'Description']:
                current[i] = row['Grand Total']

        # compare
        for val in current:
            if val in previous:
                val1 = previous[val]
                val2 = current[val]
                change = get_percent_change(val1, val2)
                if change >= change_threshold:
                    errors.append(f'Spec - {val} - CHANGED BY {change}% - {val1} TO {val2} - EXCEEDS THRESHOLD')

        total = data['Grand Total'].values[-1]
        if total != self.current_dls_file_read:
            errors.append('GRAND TOTAL != DLS FILE READ COUNT')

        self.tab_validations[tab_name] = {}

        if len(errors) == 0:
            self.tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self.tab_validations[tab_name]['status'] = 'FAILING'
            self.tab_validations[tab_name]['errors'] = errors

    def write_log_file(self):
        prev_dbl_report_filename = self._get_dbl_filename(prev=True)
        self.log_file = f'{self.log_file_directory}{self._get_dbl_filename().replace(".xlsx", "")}_log.txt'

        with open(self.log_file, 'w') as f:
            f.writelines(
                [
                    'AUTOMATED DBL REPORT REVIEW\n\n',
                    f'FILE REVIEWED - {self._get_dbl_filename()}\n',
                    f'PREVIOUS FILE - {prev_dbl_report_filename}\n',
                    f'PERFORMED {str(datetime.now().date())}',
                    '\n\n']
            )
            for tab in self.tab_validations:
                f.write(tab.ljust(22))
                f.write(str(self.tab_validations[tab]) + '\n')

    def print_report(self):
        """print('\nAUTOMATED DBL REPORT REVIEW -', self.dbl_file_location.replace('\\', '/').split('/')[-1], end='')
        print(' - PREVIOUS VERSION')
        print()
        for tab in self.tab_validations:
            print(tab.ljust(22), end='')
            print(self.tab_validations[tab])"""
        with open(self.log_file, 'r') as f:
            for line in f.readlines():
                print(line, end='')

    def _load_environment_variables(self):
        self.dbl_file_location = os.environ.get('DBL_REPORT_FILE')
        self.prev_dbl_file_location = os.environ.get('PREV_DBL_REPORT_FILE')
        self.log_file_directory = os.environ.get('LOG_FILE_DIRECTORY')

    def _get_dbl_filename(self, prev=False):
        # get filename out of full path
        if prev:
            f = self.prev_dbl_file_location
        else:
            f = self.dbl_file_location
        return f.replace('\\', '/').split('/')[-1]


validator = DBLReportValidation()
results = validator.run()
validator.print_report()
