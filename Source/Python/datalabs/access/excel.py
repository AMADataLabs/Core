import pandas as pd
import win32com


def save_formatted_output(data: pd.DataFrame, file, sheet_name='Sheet1'):
    """
    Saves a DataFrame to an Excel file with common report format:
        - centered bold column names
        - freeze-panes on headers

    :param data: DataFrame
    :param file: Target path for output file
    :param sheet_name:
    :return:
    """
    writer = pd.ExcelWriter(file, engine='xlsxwriter')
    data.to_excel(excel_writer=writer,
                  startrow=1,
                  header=False,
                  sheet_name=sheet_name,
                  index=False)
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    header_format = workbook.add_format({'bold': True,
                                         'align': 'center'})

    # writes columns in first row with specified format
    for col, val in enumerate(data.columns.values):
        worksheet.write(0, col, val, header_format)
    worksheet.freeze_panes(1, 0)  # freeze pane on top row

    writer.save()


def add_password_to_xlsx(file_path, password):
    """
    Since ExcelWriters such as xlsxwriter cannot encrypt workbooks, use win32 to use Excel API directly.
    :param file_path:
    :param password:
    :return:
    """
    app = win32com.client.Dispatch('Excel.Application')
    app.DisplayAlerts = False
    file = app.Workbooks.Open(file_path)

    file.Password = password
    file.Save()
    file.Close()

    app.DisplayAlerts = True
    app.Quit()
    del app


