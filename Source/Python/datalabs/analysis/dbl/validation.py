""" New DBL Report Validation - Sanity Checks / Comparisons to Previous Report """
from datetime import datetime
import pandas as pd


class Validater:
    def __init__(self, new_report, old_report):
        self._new = new_report
        self._old = old_report

        self._supplement_number = None
        self._current_dls_file_read = None

        self._tab_validations = {}
        self._log = ""

        self._passing = False

    def validate(self):
        if self._old is not None:
            self._validate_tab1()
            self._validate_tab2()
            self._validate_tab3()
            self._validate_tab4()
            self._validate_tab5()
            self._validate_tab6()
            self._validate_tab7()
            self._validate_tab8()
            self._validate_tab9()
            self._validate_tab10()

        self._make_result_log_string()

        self._passing = self._is_passing()

    @property
    def passing(self):
        return self._passing

    @property
    def log(self):
        return self._log

    @property
    def tab_validations(self):
        return self._tab_validations

    # pylint: disable=too-many-statements
    def _validate_tab1(self):
        """ChangeFileAudit"""
        tab_name = 'ChangeFileAudit'

        data = pd.read_excel(self._new, sheet_name=tab_name, header=None, index_col=0, engine='openpyxl').dropna().T
        prev = pd.read_excel(self._old, sheet_name=tab_name, header=None, index_col=0, engine='openpyxl').dropna().T

        self._current_dls_file_read = data['CURRENT DLS FILE READ'].values[0]

        errors = []

        prev_dls_file_read = prev['CURRENT DLS FILE READ'].values[0]
        cur_prev_dls_file_read = data['PREVIOUS DLS FILE READ'].values[0]

        if prev_dls_file_read != cur_prev_dls_file_read:
            errors.append("CURRENT REPORT'S 'PREVIOUS DLS FILE READ' DOES NOT MATCH PREVIOUS REPORT'S 'CURRENT' COUNT")

        prev_supplement = prev['SUPPLEMENT NUMBER'].values[0]
        supplement = data['SUPPLEMENT NUMBER'].values[0]

        if prev_supplement + 1 != supplement:
            errors.append("SUPPLEMENT NUMBER HAS NOT CORRECTLY INCREMENTED FROM PREVIOUS REPORT")

        self._supplement_number = supplement

        self._tab_validations[tab_name] = {}

        if len(errors) == 0:
            self._tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self._tab_validations[tab_name]['status'] = 'FAILING'
            self._tab_validations[tab_name]['errors'] = errors

    # pylint: disable=too-many-statements
    def _validate_tab2(self):
        """ReportByFieldFrom SAS"""
        tab_name = 'ReportByFieldFrom SAS'
        change_threshold = 10

        data = pd.read_excel(self._new, sheet_name=tab_name, header=None, index_col=0, engine='openpyxl').T
        prev = pd.read_excel(self._old, sheet_name=tab_name, header=None, index_col=0, engine='openpyxl').T

        errors = []

        must_100 = ['MAILING NAME', 'MAILING NAME(LAST)', 'MAILING NAME(FIRST)']
        for field in must_100:
            if data[field].values[1] != 1:
                errors.append(f'FIELD - "{field}" - IS NOT 100%')

        for field in data.columns.values[1:-2]:
            val1 = prev[field].values[1]
            val2 = data[field].values[1]
            change = self._percent_change(val1, val2)
            if change >= change_threshold:
                errors.append(f'FIELD - "{field}" - CHANGED BY {change}% - {val1} TO {val2} - EXCEEDS THRESHOLD')

        obs_count = data['OBSERVATION COUNT'].values[0]
        if obs_count != self._current_dls_file_read:
            errors.append('OBSERVATION COUNT DOES NOT MATCH DLS FILE READ COUNT')
        supplement = data['SUPPLEMENT NUMBER'].values[0]
        if supplement != self._supplement_number:
            errors.append('SUPPLEMENT NUMBER DOES NOT MATCH')

        self._tab_validations[tab_name] = {}

        if len(errors) == 0:
            self._tab_validations['ReportByFieldFrom SAS']['status'] = 'PASSING'
        else:
            self._tab_validations['ReportByFieldFrom SAS']['status'] = 'FAILING'
            self._tab_validations['ReportByFieldFrom SAS']['errors'] = errors

    def _validate_tab3(self):
        """ChangeByFieldCount"""
        tab_name = 'ChangeByFieldCount'
        data = pd.read_excel(self._new, sheet_name=tab_name, header=None, index_col=0, engine='openpyxl').T
        # prev = pd.read_excel(self._old, sheet_name=tab_name, header=None, index_col=0, engine='openpyxl').T

        errors = []

        supplement = data['SUPPLEMENT NUMBER'].values[0]
        if supplement != self._supplement_number:
            errors.append('SUPPLEMENT NUMBER DOES NOT MATCH')

        self._tab_validations[tab_name] = {}

        if len(errors) == 0:
            self._tab_validations['ChangeByFieldCount']['status'] = 'PASSING'
        else:
            self._tab_validations['ChangeByFieldCount']['status'] = 'FAILING'
            self._tab_validations['ChangeByFieldCount']['errors'] = errors

    def _validate_tab4(self):
        """RecordActionExtract"""
        tab_name = 'RecordActionExtract'

        data = pd.read_excel(self._new, sheet_name=tab_name, header=None, index_col=0, engine='openpyxl').T
        # prev = pd.read_excel(self._old, sheet_name=3, header=None, index_col=0, engine='openpyxl').T

        errors = []

        for me_number in data.columns.values:
            if len(me_number) != 11 and me_number not in ['ME NUMBER', 'SUPPLEMENT NUMBER']:
                errors.append(f'ME # "{me_number}" IS NOT 11 CHARACTERS')
        add_deletes = set(data.T.reset_index().drop(0)[1].values[:-1])  # gets the set of values, should be ('A', 'D')
        for value in add_deletes:
            if value not in 'AD':
                errors.append(f'ERRONEOUS ADD/DELETE VALUE FOUND - "{value}"')

        self._tab_validations[tab_name] = {}

        if len(errors) == 0:
            self._tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self._tab_validations[tab_name]['status'] = 'FAILING'
            self._tab_validations[tab_name]['errors'] = errors

    def _validate_tab5(self):
        """ChangeByRecordCount"""
        tab_name = 'ChangeByRecordCount'

        data = pd.read_excel(self._new, sheet_name=tab_name, header=None, index_col=0, engine='openpyxl').T
        # prev = pd.read_excel(self._old, sheet_name=tab_name, header=None, index_col=0, engine='openpyxl').T

        errors = []

        supplement = data['SUPPLEMENT NUMBER'].values[0]
        if supplement != self._supplement_number:
            errors.append('SUPPLEMENT NUMBER DOES NOT MATCH')

        self._tab_validations[tab_name] = {}

        if len(errors) == 0:
            self._tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self._tab_validations[tab_name]['status'] = 'FAILING'
            self._tab_validations[tab_name]['errors'] = errors

    # pylint: disable=too-many-statements
    def _validate_tab6(self):
        """Present Employment Counts"""
        tab_name = 'PE Counts'
        change_threshold = 5

        data = pd.read_excel(self._new, sheet_name=tab_name, header=1, index_col=0, engine='openpyxl').T
        prev = pd.read_excel(self._old, sheet_name=tab_name, header=1, index_col=0, engine='openpyxl').T

        errors = []

        for present_employment in data.columns.values[:-1]:  # [:-1] to exclude Supplement Number (last value in series)
            val1 = prev[present_employment].values[1]
            val2 = data[present_employment].values[1]
            change = self._percent_change(val1, val2)
            if change >= change_threshold:
                errors.append(
                    f'PE - "{present_employment}" - CHANGED BY {change}% - {val1} TO {val2} - EXCEEDS THRESHOLD'
                )

        total = data['Grand Total'].values[1]
        if total != self._current_dls_file_read:
            errors.append('GRAND TOTAL != DLS FILE READ COUNT')

        self._tab_validations[tab_name] = {}

        if len(errors) == 0:
            self._tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self._tab_validations[tab_name]['status'] = 'FAILING'
            self._tab_validations[tab_name]['errors'] = errors

    # pylint: disable=too-many-statements
    def _validate_tab7(self):
        """TOP Counts"""
        tab_name = 'TOP Counts'
        change_threshold = 5

        data = pd.read_excel(self._new, sheet_name=tab_name, header=1, index_col=0, engine='openpyxl').T
        prev = pd.read_excel(self._old, sheet_name=tab_name, header=1, index_col=0, engine='openpyxl').T

        errors = []

        for top in data.columns.values[:-1]:  # exclude Supplement Number
            val1 = prev[top].values[1]
            val2 = data[top].values[1]
            change = self._percent_change(val1, val2)
            if change >= change_threshold:
                errors.append(f'TOP - "{top}" - CHANGED BY {change}% - {val1} TO {val2} - EXCEEDS THRESHOLD')

        total = data['Grand Total'].values[1]
        if total != self._current_dls_file_read:
            errors.append('GRAND TOTAL != DLS FILE READ COUNT')

        self._tab_validations[tab_name] = {}

        if len(errors) == 0:
            self._tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self._tab_validations[tab_name]['status'] = 'FAILING'
            self._tab_validations[tab_name]['errors'] = errors

    # pylint: disable=too-many-statements
    def _validate_tab8(self):
        """TOP by PE"""
        tab_name = 'TOP by PE'
        change_threshold = 5
        errors = []

        previous_data = pd.read_excel(self._old, sheet_name=tab_name, header=0, index_col=0, engine='openpyxl').T
        current_data = pd.read_excel(self._new, sheet_name=tab_name, header=0, index_col=0, engine='openpyxl').T

        errors = self._generate_grand_total_percent_change_errors(previous_data, current_data, change_threshold)

        total = current_data['Grand Total'].values[-1]
        if total != self._current_dls_file_read:
            errors.append('GRAND TOTAL != DLS FILE READ COUNT')

        self._tab_validations[tab_name] = {}

        if len(errors) == 0:
            self._tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self._tab_validations[tab_name]['status'] = 'FAILING'
            self._tab_validations[tab_name]['errors'] = errors

    # pylint: disable=too-many-statements
    def _validate_tab9(self):
        """PrimSpecbyMPA"""
        tab_name = 'PrimSpecbyMPA'
        change_threshold = 5
        errors = []

        previous_data = pd.read_excel(self._old, sheet_name=tab_name, header=1, index_col=0, engine='openpyxl').T
        current_data = pd.read_excel(self._new, sheet_name=tab_name, header=1, index_col=0, engine='openpyxl').T

        errors = self._generate_grand_total_percent_change_errors(previous_data, current_data, change_threshold)

        # "unspecified counts must be LOWER than the unspecified counts in the 10th tab (SecSpecbyMPA)"
        unspecified = current_data.reset_index()[['index', 'US']]

        unspecified10 = pd.read_excel(
            self._new,
            sheet_name='PrimSpecbyMPA',
            header=1,
            index_col=0,
            engine='openpyxl'
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

        total = current_data['Grand Total'].values[-1]
        if total != self._current_dls_file_read:
            errors.append('GRAND TOTAL != DLS FILE READ COUNT')

        self._tab_validations[tab_name] = {}

        if len(errors) == 0:
            self._tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self._tab_validations[tab_name]['status'] = 'FAILING'
            self._tab_validations[tab_name]['errors'] = errors

    # pylint: disable=too-many-statements
    def _validate_tab10(self):
        """SecSpecbyMPA"""
        tab_name = 'SecSpecbyMPA'
        change_threshold = 5
        errors = []

        previous_data = pd.read_excel(self._old, sheet_name=tab_name, header=1, index_col=0, engine='openpyxl').T
        current_data = pd.read_excel(self._new, sheet_name=tab_name, header=1, index_col=0, engine='openpyxl').T

        errors = self._generate_grand_total_percent_change_errors(previous_data, current_data, change_threshold)

        total = current_data['Grand Total'].values[-1]
        if total != self._current_dls_file_read:
            errors.append('GRAND TOTAL != DLS FILE READ COUNT')

        self._tab_validations[tab_name] = {}

        if len(errors) == 0:
            self._tab_validations[tab_name]['status'] = 'PASSING'
        else:
            self._tab_validations[tab_name]['status'] = 'FAILING'
            self._tab_validations[tab_name]['errors'] = errors

    def _make_result_log_string(self):
        report_lines = [
            'AUTOMATED DBL REPORT REVIEW\n\n',
            f'PERFORMED {str(datetime.now().date())}',
            '\n\n'
        ]

        for tab, valdiation in self._tab_validations.items():
            report_lines.append(tab.ljust(22))
            report_lines.append(str(valdiation) + '\n')

        self._log = '\n'.join(report_lines)

    def _is_passing(self):
        passing = True

        for validation in self._tab_validations.values():
            if validation['status'] == 'FAILING':
                passing = False

        return passing

    @classmethod
    def _generate_grand_total_percent_change_errors(cls, previous_data, current_data, change_threshold):
        previous_values = {}
        current_values = {}
        errors = []

        # get previous values
        for index, row in previous_data.iterrows():
            if index not in ['Grand Total', 'Description']:
                previous_values[index] = row['Grand Total']

        # get current values
        for index, row in current_data.iterrows():
            if index not in ['Grand Total', 'Description']:
                current_values[index] = row['Grand Total']

        # compare
        for name, current_value in current_values.items():
            if name in previous_values:
                previous_value = previous_values[name]
                change = cls._percent_change(previous_value, current_value)

                if change >= change_threshold:
                    info = f'Spec - "{name}" - CHANGED BY {round(change, 2)}% - {previous_value} TO {current_value} ' \
                            f'- EXCEEDS THRESHOLD of {change_threshold}%'
                    errors.append(info)

        return errors

    @classmethod
    def _percent_change(cls, val1, val2):
        percent_change = 0

        if val1 not in (val2, 0):
            difference = abs(val1 - val2)
            percent_change = (100.0 * difference) / val1

        return percent_change
