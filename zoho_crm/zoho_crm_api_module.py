import pandas as pd
import requests
import json
from pandas import json_normalize
import re
import datetime
from datetime import date
from datetime import datetime, timedelta

def get_crm_token():
    import requests

    url = 'https://accounts.zoho.com/oauth/v2/token?client_id=1000.WI17CSUCBKZY77CWMLFENP8KXWKXWB&grant_type=refresh_token&client_secret=6d8e4d364f228ec2ac7b9ec69ad36a4d1e03e73d7f&refresh_token=1000.10bc17e276de7cf42e63f7b0e7208d34.5e81bf57a2132b3426154bba3c336c5b'

    # post data menggunakan request
    response = requests.post(url)

    # konversi request.models.response to json
    json_data = json.loads(response.text)
    token = json_data['access_token']

    return token

import requests
import pandas as pd
from pandas import json_normalize

import requests
import pandas as pd
from pandas import json_normalize


import requests
import pandas as pd
from pandas import json_normalize


def get_leads_data(token, cols=None):
    url = "https://www.zohoapis.com/crm/v2/coql"
    headers = {"Authorization": f"Zoho-oauthtoken {token}"}
    page_size = 200

    start_dt = "'2025-01-01T00:00:01+08:00'"
    end_dt = "'2025-12-30T23:59:59+08:00'"

    dataframes = []
    offset = 0

    while True:
        query = (
            "select Created_Time, id, Last_Name, Email, Phone, City, Country, "
            "Lead_Status, Lead_Type1, Agents "
            "from Leads "
            f"where Created_Time between {start_dt} and {end_dt} "
            f"limit {offset}, {page_size}"
        )

        response = requests.post(url, headers=headers, json={"select_query": query})
        result = response.json()

        if "data" not in result:
            print("Zoho error:", result)
            break

        df = pd.DataFrame(json_normalize(result["data"]))

        # 👉 Filter columns only if cols is provided and not empty
        if cols:
            df = df[[c for c in cols if c in df.columns]]

        dataframes.append(df)

        if not result.get("info", {}).get("more_records"):
            break

        offset += page_size

    if not dataframes:
        return pd.DataFrame(columns=cols if cols else None)

    return pd.concat(dataframes, ignore_index=True)


def get_leads_data_filter(df):
    f_1 = (df['Brand'] == 'Karma Resorts')
    f_2 = (df['Lead_Sub_Brand'] == 'Other')
    f_3 = (df['Lead_Source'] == 'Past Guests')
    f_4 = (~df['Email'].str.contains('karmagroup.com'))
    f_5 = (df['Email']!='empty')
    f_6 = (df['Email_Opt_Out']==False)

    # mengambil data yang email, phone dan mobilenya tidak kosong
        
    final_filter = (
        f_1 & 
        f_2 & 
        f_3 & 
        f_4 & 
        f_5 & 
        f_6
    )

    zoho_df = df.loc[final_filter].copy() # menggunakan copy untuk menghindari setting copy warning
    zoho_df.reset_index(drop=True, inplace=True)
    zoho_df

    return zoho_df
