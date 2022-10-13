#Define function
def validate_numbers():
    #Define the filepah:
    filename = input ("Where is the phone numbers file?  ")
    print("The phone cumbers column should have the header 'OFFICE_TELEPHONE'")

    #import dependencies
    import pandas as pd
    import requests
    from key import API_key

    #Make pandas dataframe:
    df = pd.read_csv(filename)

    #Define url and format
    base_url = "https://api.realvalidation.com/rpvWebService/RealPhoneValidationTurbo.php"
    output = "json"

    #Loop through dataframe, call API on each number and write new dataframe to csv
    results_dict_list = []
    for row in df.itertuples():
        new_dict = {}
        phone = row.OFFICE_TELEPHONE
        new_dict["OFFICE_TELEPHONE"] = phone
        parameters = {'output':output, 'phone' : phone, 'token': API_key}
        response =  requests.get(base_url, params=parameters)
        results = response.json()
        status = results['status']
        new_dict['status']=status
        results_dict_list.append(new_dict)
    new_df = pd.DataFrame(results_dict_list)
    final_df = pd.merge(new_df, df, on='OFFICE_TELEPHONE')
    final_df.to_csv("real_phone_validated_results.csv", index=False)
    return(final_df)

#Run function when called
if __name__ == "__main__":
    validate_numbers()