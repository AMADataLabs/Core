import win32com.client


# Auto-fits column widths and saves a file with a password if specified.
def format_and_save(xlsx_path, password=None):
    app = win32com.client.Dispatch('Excel.Application')
    app.DisplayAlerts = False
    file = app.Workbooks.Open(xlsx_path)

    # adjust column widths
    for sheet in file.Sheets:
        sheet.Columns.AutoFit()

    # if password is given, set password
    if password is not None:
        file.Password = password

    # file.SaveAs(Filename=output_path)
    file.SaveAs(Filename=xlsx_path, Local=True)
    file.Close()

    app.DisplayAlerts = True
    app.Quit()
    del app
    return
