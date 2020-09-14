import re
import pandas as pd
from glob import glob
import columns

def create_file_paths():
    '''
    Returns a dictionary of three important file paths
    '''
    file_paths = {'input_directory': 'U:/Source Files/Data Analytics/Data Engineering/SFMC/SFMC-7.3.20/',
                  'input_table_pattern': 'U:/Source Files/Data Analytics/Data Engineering/SFMC/SFMC-7.3.20/*.txt',
                  'output_directory': 'U:/Source Files/Data Analytics/Data Engineering/SFMC/SFMC-7.3.20/'}
    return (file_paths)


def create_tables(file_paths):
    '''
    Returns a list of pandas dataframes of all the original input tables from Valid

            Parameters:
                file_paths (dictionary): file paths
            Returns:
                list of pandas dataframes of all the raw input tables
    '''
    # create a list of text flat file names in the directory
    filenames = glob(file_paths['input_table_pattern'])

    # import all the files in the directory
    files = [pd.read_csv(file, delimiter="\t", encoding="ISO-8859-1") for file in filenames]

    # create a list of table names
    start = 'SFMC_'
    end = '_2020'
    tablenames = [name[name.find(start) + len(start):name.rfind(end)].lower() for name in filenames]

    tablenames = [re.sub(r'_\d{8}.tx', '', name) for name in tablenames]

    # dynamic naming of tables
    tables = dict(zip(tablenames, files))
    return (tables)


def create_pbd_table(pbd_orders, pbd_returns, pbd_cancels):  # staging table
    '''
    Returns a table of pbd transactions minus cancels and refunds

            Parameters:
                    pbd_orders (pandas dataframe): PBD Orders
                    pbd_returns (pandas dataframe): PBD returns
                    pbd_cancels (pandas dataframe): PBD cancels

            Returns:
                    pbd_table (pandas dataframe): table of PBD orders without canceled and refunded transactions
    '''
    import pandas as pd
    pbd_order_columns = columns.PBD_ORDER_COLUMNS
    pbd_cancels_columns = columns.PBD_CANCELS_COLUMNS
    pbd_returns_columns = columns.PBD_RETURNS_COLUMNS
    # subset columns
    pbd_orders = pbd_orders[pbd_order_columns]
    pbd_returns = pbd_returns[pbd_returns_columns]
    pbd_cancels = pbd_cancels[pbd_cancels_columns]

    # merge all pbd tables using left join to combine all histories of Print/Book/Digital transactions
    pbd_table = pbd_orders[~pbd_orders.ORDER_NO.isin(pbd_cancels.ORDER_NO)]
    pbd_table = pbd_table[~pbd_table.ORDER_NO.isin(pbd_returns.ORDER_NO)]

    # Create Date columns
    pbd_table['ORDER_DATE'] = pd.to_datetime(pbd_table['ORDER_DATE']).dt.date
    pbd_table['ORDER_DATE'] = pd.to_datetime(pbd_table['ORDER_DATE'], format='%Y/%m/%d %H:%M:%S')
    pbd_table['ORDER_MONTH'] = pd.DatetimeIndex(pbd_table['ORDER_DATE']).month
    pbd_table['ORDER_YEAR'] = pd.DatetimeIndex(pbd_table['ORDER_DATE']).year

    return pbd_table


def create_pbd_sales_table(pbd_table):  # staging table
    '''
    Returns a table of unique PBD order

            Parameters:
                    pbd_table (pandas dataframe): PBD table

            Returns:
                    sales (pandas dataframe): table with orders aggregated over each item transaction

    '''
    sales = pbd_table.groupby(['ORDER_NO', 'ORDER_YEAR', 'ORDER_MONTH'])['ORDTDOL'].sum().reset_index()
    new_column_names = ['Order ID', 'Year', 'Month', 'Revenue']
    sales = sales.rename(columns=dict(zip(sales.columns.tolist(),
                                          new_column_names)))
    sales = sales.sort_values(by=['Year', 'Month'])
    sales['Type'] = 'PBD'
    return sales


def create_month_and_year_columns(df, date):  # helper function
    '''
    Returns a dataframe with new month and year columns

            Parameters:
                    df (pandas dataframe): any dataframe with datetime column
                    date (datetime): date column

            Returns:
                    df (pandas dataframe): dataframe with new date columns

    '''
    df[date] = pd.to_datetime(df[date], format='%Y/%m/%d %H:%M:%S')
    df['MONTH'] = pd.DatetimeIndex(df[date]).month
    df['YEAR'] = pd.DatetimeIndex(df[date]).year
    return df


def create_olsub_sales_table(olsub_orders):  # staging table
    '''
    Returns a table of OLsub orders

            Parameters:
                    olsub_orders (pandas dataframe): OLsub transactions

            Returns:
                    sales (pandas dataframe): table of olsub orders with aggregated transactions

    '''
    olsub_order_columns = columns.OLSUB_ORDER_COLUMNS

    # subset columns
    olsub_orders = olsub_orders[olsub_order_columns]

    # create month and year columns
    olsub_orders = create_month_and_year_columns(olsub_orders, 'SUB_DATE')

    # merge two tables using left join to combine all histories of online transactions
    sales = olsub_orders.groupby(['ORDER_ID', 'YEAR', 'MONTH'])['ORDTDOL'].sum().reset_index()
    new_column_names = ['Order ID', 'Year', 'Month', 'Revenue']
    sales = sales.rename(columns=dict(zip(sales.columns.tolist(),
                                          new_column_names)))
    sales = sales.sort_values(by=['Year', 'Month'])
    sales['Type'] = 'OLSub'
    return sales


def create_sales_kpi(sales, pbd_table):  # final table
    '''
    Returns a dataframe with monthly kpi's

            Parameters:
                    sales (pandas dataframe): sales dataframe from above
                    pbd_table (pandas dataframe): pbd_table dataframe from above

            Returns:
                    sales_kpi (pandas dataframe): dataframe with monthly KPI's

    '''
    sales['Date'] = pd.to_datetime(sales[['Year', 'Month']].assign(DAY=1))
    # Number of Unique Order
    no_unique_order = sales.groupby('Date')['Order ID'].nunique()
    # Monthly Total Sales
    total_sales = sales.groupby('Date')['Revenue'].sum()
    # Average Sale Value per Order
    average_sale_per_order = total_sales / no_unique_order
    pbd_table['Date'] = pd.to_datetime(pbd_table['ORDER_YEAR'].astype(str) + '-' + pbd_table['ORDER_MONTH'].astype(str))
    # Number of Unique Customers
    no_unique_customers = pbd_table.groupby('Date')['EMPPID'].nunique()
    # Subset for every customer the first order date
    first_orders = pbd_table.groupby('EMPPID')['Date'].min().reset_index()
    # Number of New Customers
    no_new_customers = first_orders.groupby('Date')['EMPPID'].nunique()
    # Average Purchase Frequency
    avg_purchase_frequency = no_unique_order / no_unique_customers
    # Average Spending per Customer
    avg_spending_per_customer = total_sales / no_unique_customers
    # Average Customer Value
    avg_customer_value = avg_spending_per_customer / avg_purchase_frequency
    # Put together
    sales_kpi = pd.DataFrame({'Number of Unique Orders': no_unique_order,
                              'Total Sales': total_sales,
                              'Average Sale': average_sale_per_order,
                              'Number of Unique Customers': no_unique_customers,
                              'Number of New Customers': no_new_customers,
                              'Average Purchase Frequency': avg_purchase_frequency,
                              'Average Spending Per Customer': avg_spending_per_customer,
                              'Average Customer Value': avg_customer_value})
    return sales_kpi


def create_pbd_items_table(pbd_table, pbd_items):  # staging table
    '''
    Returns PBD sales table at an item level

            Parameters:
                    pbd_table (pandas dataframe): dataframe from above
                    pbd_items (pandas dataframe): pbd_items dataframe from above

            Returns:
                    pbd_items_table (pandas dataframe): pbd sales table at item level

    '''
    # subset columns
    pbd_items_columns =  columns.PBD_ITEMS_COLUMNS
    pbd_items = pbd_items[pbd_items_columns]
    pbd_items['ORDER_DATE'] = pd.to_datetime(pbd_items['ORDER_DATE'], format='%Y/%m/%d %H:%M:%S')

    # merge with item table
    pbd_items_table = pd.merge(pbd_table, pbd_items, on=['ORDER_NO', 'ORDER_DATE'], how='inner')

    # drop columns
    pbd_items_table = pbd_items_table.drop(['EMPPID_y'], axis=1).rename(columns={'EMPPID_x': 'EMPPID'})

    return pbd_items_table


def create_product_sales_table(pbd_items_table):  # staging table
    '''
    Returns PBD sales table at an item level with clean clumns

            Parameters:
                    pbd_items_table (pandas dataframe): dataframe from above

            Returns:
                    product_sales (pandas dataframe): cleaned columns

    '''
    pbd_items_table['ORDER_DATE'] = pd.to_datetime(pbd_items_table['ORDER_DATE'], format='%Y/%m/%d %H:%M:%S')
    pbd_items_table['ORDER_MONTH'] = pd.DatetimeIndex(pbd_items_table['ORDER_DATE']).month
    pbd_items_table['ORDER_YEAR'] = pd.DatetimeIndex(pbd_items_table['ORDER_DATE']).year
    product_sales = pbd_items_table.groupby(['PRODUCT_NO', 'PRODUCT_DESC', 'ORDER_YEAR', 'ORDER_MONTH'])[
        'ITEMEXTPRICE'].sum().reset_index()
    new_column_names = ['Item Number', 'Product Names', 'Year', 'Month', 'Revenue']
    product_sales = product_sales.rename(columns=dict(zip(product_sales.columns.tolist(),
                                                          new_column_names)))
    return product_sales


def unmatched_budget_codes(row):  # helper function
    '''
    Returns row with new budget code matching on item numbers that are not found in the matching dictionary

            Parameters:
                    row (dataframe's row): row containing Item Number column of product

            Returns:
                    budget code matching

    '''
    if re.search('^EP', row['Item Number']):
        return 'AC36'
    elif re.search('^ER', row['Item Number']):
        return 'AC21'
    else:
        return "Other"


def match_budget_codes(product_sales, budget_code):  # helper function
    '''
    Returns product sales table with budget codes matching from dictionary and custom function for budget matching

            Parameters:
                    pbd_table (pandas dataframe): dataframe from above
                    pbd_items (pandas dataframe): pbd_items dataframe from above

            Returns:
                    pbd_items_table (pandas dataframe): pbd sales table at item level

    '''
    # non-zero revenue only
    product_sales = product_sales[product_sales['Revenue'] > 0]
    # subscripts of interest 16-21
    product_sales = product_sales[product_sales['Item Number'].str.contains('16\Z|17\Z|18\Z|19\Z|20\Z|21\Z')]
    # create a set of rows joined with budget code
    product_sales_matched = product_sales.merge(budget_code, on=['Item Number'])
    # create another set of rows not joined with budget code
    product_sales_unmatched = product_sales[~product_sales['Item Number'].isin(budget_code['Item Number'])].dropna()
    # fill up the remaining budget codes
    product_sales_unmatched['Budget Code'] = product_sales_unmatched.apply(unmatched_budget_codes, axis=1)
    product_sales_coded = pd.concat([product_sales_matched, product_sales_unmatched])
    return (product_sales_coded)


def create_product_main_table(product_sales_coded):
    main_product_names = ['CPT PROFESSIONAL', 'CPT CHANGES', 'ICD-10-PCS', 'ICD-10-CM' 'HCPCS']
    main_product_indices = product_sales_coded['Product Names'].str.contains('|'.join(main_product_names))
    product_main = product_sales_coded[main_product_indices]
    return (product_main)


def create_product_remainder_table(product_sales_coded):
    main_product_names = ['BUDGET_DESC','CPT PROFESSIONAL', 'CPT CHANGES', 'ICD-10-PCS', 'ICD-10-CM' 'HCPCS']
    main_product_indices = product_sales_coded['Product Names'].str.contains('|'.join(main_product_names))
    product_remainder = product_sales_coded[~main_product_indices]
    return (product_remainder)


def create_customer_table(pbd_table, contacts, aims_overlay):
    '''
    Returns a table at unique customer level with demographic info and transaction history

            Parameters:
                    pbd_table (pandas dataframe): dataframe from above
                    contacts (pandas dataframe): contact info of customers
                    aims_overlay (pandas dataframe): customer info from AIMS

            Returns:
                    customer (pandas dataframe): dataframe at a customer level

    '''
    contacts_columns = columns.CONTACTS_COLUMNS
    aims_overlay_columns = columns.AIMS_OVERLAY_COLUMNS
    # subset columns for contacts and aims_overlay
    contacts = contacts[contacts_columns]
    aims_overlay = aims_overlay[aims_overlay_columns]

    # retain only the very first information from contacts and aims_overlay
    contacts = contacts.groupby(['EMPPID']).first()
    aims_overlay = aims_overlay.groupby(['EMPPID']).first()

    # combined columns of interest from contacts and aims_overlay
    final_columns = contacts_columns + aims_overlay_columns[1:]

    # merge the tables
    customer = pd.merge(pbd_table, contacts, how='left', on='EMPPID').merge(aims_overlay, how='left', on='EMPPID')
    temp1 = customer.groupby(['EMPPID']).agg({'ITEMEXTPRICE': 'sum',
                                              'ORDER_DATE': 'max',
                                              'ORDER_NO': 'count'}).reset_index()
    temp2 = customer[final_columns].groupby(['EMPPID']).first().reset_index()
    customer = temp1.merge(temp2, on='EMPPID', how='inner')

    # rename columns
    new_column_names = columns.NEW_COLUMN_NAMES
    customer = customer.rename(columns=dict(zip(customer.columns.tolist(),
                                                new_column_names)))
    customer['Recency'] = pd.Timestamp('today').normalize() - customer['Recent Purchase Date']

    return customer


def clean_up_customer(customer):
    '''
    Returns a cleaned up customer dataframe above

            Parameters:
                    customer (pandas dataframe): customer dataframe from above

            Returns:
                    customer (pandas dataframe): customer dataframe cleaned up (Title and Industry descriptions)
    '''
    # fill up NaN with 'Unknown'
    customer['Title Description'] = customer['Title Description'].fillna('Unknown')
    # recode phyisican, doctor, etc
    customer['Title Description'] = customer['Title Description'].replace('Other (Specify)', 'Other').replace(
        'Purchasing Agent', 'Purchasing Agent/Buyer').replace(
        ['DR/ MD/ PHYSICIAN', 'Dr/MD/Physician', 'DR/MD/PHYSICIAN', 'Dr, MD, Physician'], 'Physician').replace(
        'Billing Manager/Sup/Director', 'Billing Manager/Supervisor/Director').replace(
        ['NURSE (RN/LPN/RNP)', 'Nurse (RN,LPN,RNP)', 'Nurse (RN,LPN,RNP)', 'NURSE RN/LPN/RNP', 'Nurse (RN LPN RNP)'],
        'NURSE')
    # Title strings
    customer['Title Description'] = customer['Title Description'].str.title().replace(
        ['General Management/Ceo/Cfo', 'General Management/Ceo/Coo/Cfo'], 'General Management/CEO/COO/CFO').replace(
        'Description Unknown', 'Unknown').replace('Medical Records/Doc Manager',
                                                  'Medical Records/Documentation Manager').replace(
        ['Coding Manager/Sup/Director', 'Coding/Manager/Supervisor/Director'],
        'Coding Manager/Supervisor/Director').replace('Nurse(Rn/Lpn/Rnp)', 'Nurse').replace(
        'Coders/Claims/Record Processors', 'Claims/Record Processor/Coder')
    customer['Industry Description'] = customer['Industry Description'].str.title()
    customer['Industry Description'] = customer['Industry Description'].fillna('Unknown')
    customer['Industry Description'] = customer['Industry Description'].replace(
        ['Hospital/Med Cntr/VA Hospital', 'Hospital/Med Center/Va Hosp'], 'Hospital/Med Center/VA Hosp').replace(
        ['Group Practice [3+ Physicians]', 'Insurance Co', '2-Yr/4-Yr College', 'Wgerber@Aol.Com',
         'Billing Company/Claims Processing', 'Hmo/Ppo/Managed Care', 'Description Unknown'],
        ['Group Practice (3+)', 'Insurance Company', '2-Year/4-Year College', 'Unknown',
         'Billing Company/Claims Processor', 'HMO/PPO/Managed Care', 'Unknown'])
    return customer


def create_email_campaign_table(email_campaign):
    email_campaign_columns = columns.EMAIL_CAMPAIGN_COLUMNS
    email_campaign = email_campaign[email_campaign_columns]
    new_email_campaign_columns = [*map(lambda x: x.title().replace('_', ' '), email_campaign_columns)]
    email_campaign = email_campaign.rename(columns=dict(zip(email_campaign_columns,
                                                            new_email_campaign_columns)))
    return email_campaign

def create_direct_mail_table(direct_mail):
    direct_mail_campaign_columns = ['CATALOG_DESC']
    direct_mail_campaign = direct_mail[direct_mail_campaign_columns]
    new_direct_mail_campaign_columns = [*map(lambda x: x.title().replace('_', ' '), direct_mail_campaign_columns)]
    direct_mail_campaign = direct_mail_campaign.rename(columns=dict(zip(direct_mail_campaign_columns,
                                                            new_direct_mail_campaign_columns)))
    return direct_mail_campaign

def export_tables(output_directory):
    pbd_table.to_csv(output_directory + os.environ['PBD_TABLE'], index=False)
    sales_pbd.to_csv(output_directory + os.environ['SALES_PBD'], index=False)
    sales_kpi.to_csv(output_directory + os.environ['SALES_KPI'])
    product_main.to_csv(output_directory + os.environ['PRODUCT_MAIN'], index=False)
    product_remainder.to_csv(output_directory + os.environ['PRODUCT_REMAINDER'], index=False)
    customer_clean.to_csv(output_directory + os.environ['CUSTOMER_CLEAN'])
    direct_mail.to_csv(output_directory + os.environ['DIRECT_MAIL'])
    fax.to_csv(output_directory + os.environ['FAX'])
    email_campaign.to_csv(output_directory + os.environ['EMAIL_CAMPAIGN'])

def transform_tables(tables):
    pbd_table = create_pbd_table(tables['pbd_orders'], tables['pbd_returns'], tables['pbd_cancels'])
    sales_pbd = create_pbd_sales_table(pbd_table)
    sales_olsub = create_olsub_sales_table(tables['olsub_orders'])
    sales = pd.concat([sales_pbd, sales_olsub], axis=0)
    sales_kpi = create_sales_kpi(sales, pbd_table)
    pbd_items_table = create_pbd_items_table(pbd_table, tables['pbd_items'])
    product_sales = create_product_sales_table(pbd_items_table)
    product_sales_coded = match_budget_codes(product_sales, budget_code)
    product_main = create_product_main_table(product_sales_coded)
    product_remainder = create_product_remainder_table(product_sales_coded)
    customer = create_customer_table(pbd_items_table, tables['contacts'], tables['aims_overlay'])
    customer_clean = clean_up_customer(customer)
    pbd_orders = tables['pbd_orders']
    direct_mail = create_email_campaign_table(pbd_orders[pbd_orders['ORDER_TYPE'] == 'Mail'])
    fax = pbd_orders[pbd_orders['ORDER_TYPE'] == 'FAX']
    email_campaign = create_email_campaign_table(tables['emailcampaign'])

def main():
    # define file paths
    file_paths = create_file_paths()
    # create tables using file paths
    tables = create_tables(file_paths)
    # define input and output directories
    input_directory = file_paths['input_directory']
    output_directory = file_paths['output_directory']
    # import budget code
    budget_code = pd.read_excel(input_directory + 'CPT_Products_Mapping_Budget_Codes.xlsx',
                                usecols=['Item Number', 'Budget Code'])
    # transform tables
    transform_tables(tables)
    # export tables
    export_tables(output_directory)


if __name__ == '__main__':
    main()






















