""" Windows-specific Excel functions. save_formatted_output should be able to be used on any platform (no win32com) """
import pandas as pd

import datalabs.feature as feature

if feature.enabled('WINDOWS'):
    import win32com  # pylint: disable=import-error
    from win32com import client  # pylint: disable=import-error


def save_formatted_output(data: pd.DataFrame, file, sheet_name='Sheet1'):
    """
    Saves a DataFrame to an Excel file with common report format:
        - centered bold column names
        - freeze-panes on headers

    :param data: DataFrame
    :param file: Target path or BytesIO
    :param sheet_name:
    :return:
    """
    writer = pd.ExcelWriter(file, engine='xlsxwriter')  # pylint: disable=abstract-class-instantiated
    data.to_excel(excel_writer=writer,
                  startrow=1,
                  header=False,
                  sheet_name=sheet_name,
                  index=False)
    workbook = writer.book  # pylint: disable=no-member
    worksheet = writer.sheets[sheet_name]
    header_format = workbook.add_format({'bold': True,
                                         'align': 'center'})

    # writes columns in first row with specified format
    for col, val in enumerate(data.columns.values):
        worksheet.write(0, col, val, header_format)
    worksheet.freeze_panes(1, 0)  # freeze pane on top row

    writer.save()
    return file


def add_password_to_xlsx(file_path, password):
    """
    Since ExcelWriters such as xlsxwriter cannot encrypt workbooks, use win32 to use Excel API directly.
    :param file_path:
    :param password:
    :return:
    """
    if feature.enabled('WINDOWS'):
        app = win32com.client.Dispatch('Excel.Application')
        app.DisplayAlerts = False
        file = app.Workbooks.Open(file_path)

        file.Password = password
        file.Save()
        file.Close()

        app.DisplayAlerts = True
        app.Quit()
        del app


def remove_password_from_xlsx(file_path, password, new_file):
    app = client.Dispatch('Excel.Application')
    app.DisplayAlerts = False
    file = app.Workbooks.Open(file_path, False, False, None, password)

    file.Unprotect(password)
    file.UnprotectSharing(password)
    file.SaveAs(new_file, None, '', '')
    file.Close()

    app.DisplayAlerts = True
    app.Quit()
    del app
