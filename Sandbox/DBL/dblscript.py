import file_names
import xlsxwriter
import xlwt

def readInputFile(filename, header):
    return pd.read_csv(filename, delimiter='|',names=header)

def createSheets(df, writer, name)
    df.to_excel(writer,name)
    return writer

def writeOutput(dataframes):
    #create a Pandas Excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter('dataframes.xlsx', engine='xlsxwriter')

    #write each DataFrame to a specific sheet
    df1.to_excel(writer, sheet_name='first dataset')
    df2.to_excel(writer, sheet_name='second dataset')
    df3.to_excel(writer, sheet_name='third dataset')

    writer = createSheets(PDRP,writer,"PDRP_PrimSpecCounts.txt")
    writer = createSheets(PSC,writer, "PreferredStateCounts.txt")
    writer = createSheets(topbyPE,writer,  "topbyPEcounts.txt")
    writer = createSheets(TOP,writer,  "TOP_counts.txt")
    writer = createSheets(Sec,writer,  "SecSpecbyMPA.txt")
    writer = createSheets(ReportBy,writer,  "ReportByFieldFrom_SAS.txt")
    writer = createSheets(record,writer,  "recordactionextraction.txt")
    writer = createSheets(Prim,writer,  "PrimSpecbyMPA.txt")
    writer = createSheets(PE,writer,  "PE_counts.txt")
    writer = createSheets(count,writer,  "countofchangesbyfieldextract.txt")
    writer = createSheets(changefile,writer,  "changefileaudit.txt")
    writer = createSheets(changerecord,writer,  "changebyrecordcount.txt")

    #close the Pandas Excel writer and output the Excel file
    writer.save()

PDRP = readInputFile("PDRP_PrimSpecCounts.txt", [])
PSC = readInputFile("PreferredStateCounts.txt", [])
topbyPE = readInputFile("topbyPEcounts.txt", ["Sum of Count PE Code", "Description", "PE Code", "Grand Total"])
TOP = readInputFile("TOP_counts.txt", ["Sum of Count TOP Code", "Description", "Total"])
Sec = readInputFile("SecSpecbyMPA.txt", ["Sum of Count SPEC Code", "Description", "MPA Code", "Grand Total"])
ReportBy = readInputFile("ReportByFieldFrom_SAS.txt", ["FIELD", "COUNT", "PERCENTAGE"])
record = readInputFile("recordactionextraction.txt", ["ME NUMBER", "ADD/DELETE"])
Prim = readInputFile("PrimSpecbyMPA.txt", ["Sum of Count MPA Code", "Description", "MPA Code"])
PE = readInputFile("PE_counts.txt", ["Sum of Count PE Code", "Description", "Total"])
count = readInputFile("countofchangesbyfieldextract.txt", ["FIELD", "CHANGE", "SECTION TOTAL"])
changefile = readInputFile("changefileaudit.txt", [])
changerecord = readInputFile("changebyrecordcount.txt", ["FIELD", "COUNT", "PERCENTAGE"])

ReportBy.loc['PERCENTAGE'] = ((ReportBy.loc['PERCENTAGE']/ReportBy.loc['PERCENTAGE'])
                              .apply('{:.0%}'.format))
changerecord.loc['PERCENTAGE'] = ((changerecord.loc['PERCENTAGE']/changerecord.loc['PERCENTAGE'])
                              .apply('{:.0%}'.format))



