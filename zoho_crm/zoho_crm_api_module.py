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

    url = 'https://accounts.zoho.com/oauth/v2/token?client_id=1000.8ZWIGIGFJGL2XE23M81L2FPLB7WQXC&grant_type=refresh_token&client_secret=eb10f3fd944667ff8e4facb7b217f1531acd07b280&refresh_token=1000.19b991b064e9ea14d8ef866ee57966dc.9875f2a0656f1f9f33b22ff6a974ab67'

    # post data menggunakan request
    response = requests.post(url)

    # konversi request.models.response to json
    json_data = json.loads(response.text)
    token = json_data['access_token']

    return token


def get_past_guest_data(token, cols):
    array_df = []

    # mencari tanggal hari ini
    first_date = '2022-12-23'
    second_date = '2022-12-23'

    start_date = '\''+first_date+'T00:00:01+08:00\''
    end_date = '\''+second_date+'T23:59:59+08:00\''

    for x in range(99999):
        limit = 200
        offset = str(x*limit)

        query = "select Created_Time, id, First_Name, Last_Name, Email, Phone, Mobile, Brand, Lead_Sub_Brand, Lead_Source, Lead_Locations, Lead_Regions, City, Nationality, Country, Booking_Status, Guest_Type, Email_Opt_In, Email_Opt_Out, BookRef from Leads where Brand = 'Karma Resorts' and ( Created_Time between "+start_date+" and "+end_date+") offset "+offset+" limit 200"

        url_get_lead = 'https://www.zohoapis.com/crm/v2/coql'
        headers = {'Authorization': 'Zoho-oauthtoken '+token}
        body = {
            "select_query": query
        }

        content_res = requests.post(url_get_lead, headers=headers, json=body).json()
        normalize = json_normalize(content_res['data'])
        df = pd.DataFrame(normalize)
        new_df = df[cols].copy()
        
        # jika jumlah data sudah habis atau 0 maka akan menghentikan loop
        # memasukan df kedalam array_df
        if (content_res['info']['more_records'] == False):
            array_df.append(new_df)
            break
        # jika jumlah data yang diloop masih ada atau lebih dari 0
        else:
            array_df.append(new_df)

    concat_df = pd.concat(array_df, ignore_index=True)

    concat_df['Lead_Locations'] = concat_df['Lead_Locations'].astype('string')
    concat_df['Lead_Locations'].replace('\[|\]|\'','', regex=True, inplace=True)

    return concat_df

def get_past_guest_data_filter(df):
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

def get_newsletter_data(token, cols):
    array_df = []

    # mencari tanggal 8 hari kebelekang
    calculate_date = datetime.now() - timedelta(days=8)
    new_cal_date = str(calculate_date.strftime("%Y-%m-%d")).split(' ')
    first_date = new_cal_date[0]
    # first_date = '2022-12-06'

    # mencari tanggal hari ini
    today = date.today()
    second_date = today.strftime("%Y-%m-%d")
    # second_date = '2022-12-14'

    start_date = '\''+first_date+'T00:00:01+08:00\''
    end_date = '\''+second_date+'T23:59:59+08:00\''

    for x in range(99999):
        limit = 200
        offset = str(x*limit)

        query = "select Created_Time, id, First_Name, Last_Name, Email, Phone, Mobile, Brand, Lead_Sub_Brand, Lead_Source, Lead_Locations, Lead_Regions, City, Nationality, Country, Booking_Status, Guest_Type, Email_Opt_In, Email_Opt_Out, Email_status, Odyssey_Members, Do_Not_Mail, Do_Not_Contact, BookRef from Leads where Brand = 'Karma Group' and ( Created_Time between "+start_date+" and "+end_date+") offset "+offset+" limit 200"

        url_get_lead = 'https://www.zohoapis.com/crm/v2/coql'
        headers = {'Authorization': 'Zoho-oauthtoken '+token}
        body = {
            "select_query": query
        }

        content_res = requests.post(url_get_lead, headers=headers, json=body).json()
        normalize = json_normalize(content_res['data'])
        df = pd.DataFrame(normalize)
        new_df = df[cols].copy()

        # jika jumlah data yang diloop masih ada atau lebih dari 0
        # memasukan df kedalam array_df
        if (content_res['info']['more_records'] == False):
            array_df.append(new_df)
            break
        # jika jumlah data sudah habis atau 0 maka akan menghentikan loop
        else:
            array_df.append(new_df)
    
    concat_df = pd.concat(array_df, ignore_index=True)

    concat_df['Lead_Locations'] = concat_df['Lead_Locations'].astype('string')
    concat_df['Lead_Locations'].replace('\[|\]|\'','', regex=True, inplace=True)

    concat_df['Email_status'] = concat_df['Email_status'].astype('string')
    concat_df['Email_status'].replace('\[|\]|\'','', regex=True, inplace=True)

    return concat_df


def check_karma_beach_exists(token, cols, email, phone):

    # # mencari tanggal 8 hari kebelekang
    # calculate_date = datetime.now() - timedelta(days=8)
    # new_cal_date = str(calculate_date.strftime("%Y-%m-%d")).split(' ')
    # first_date = new_cal_date[0]
    # # first_date = '2022-12-06'

    # # mencari tanggal hari ini
    # today = date.today()
    # second_date = today.strftime("%Y-%m-%d")
    # # second_date = '2022-12-14'

    # start_date = '\''+first_date+'T00:00:01+08:00\''
    # end_date = '\''+second_date+'T23:59:59+08:00\''

    query = "select Created_Time, id, First_Name, Last_Name, Email, Phone, Mobile, Brand, Lead_Sub_Brand, Lead_Source, Lead_Locations, Lead_Regions, City, Nationality, Country, Booking_Status, Guest_Type, Email_Opt_In, Email_Opt_Out, Email_status, Odyssey_Members, Do_Not_Mail, Do_Not_Contact, BookRef from Leads where Lead_Sub_Brand = 'Karma Beach' and ( Email = '"+email+"' or Phone = '"+phone+"')"

    url_get_lead = 'https://www.zohoapis.com/crm/v2/coql'
    headers = {'Authorization': 'Zoho-oauthtoken '+token}
    body = {
            "select_query": query
        }

    try :
        content_res = requests.post(url_get_lead, headers=headers, json=body).json()
        normalize = json_normalize(content_res['data'])
        df = pd.DataFrame(normalize)
        new_df = df[cols].copy()

        new_df['Lead_Locations'] = new_df['Lead_Locations'].astype('string')
        new_df['Lead_Locations'].replace('\[|\]|\'','', regex=True, inplace=True)

        new_df['Email_status'] = new_df['Email_status'].astype('string')
        new_df['Email_status'].replace('\[|\]|\'','', regex=True, inplace=True)

        result = 'Exists'

    except ValueError:

        result = 'Not Exists'

        
    return result

def get_newsletter_data_filter(df):
    f_1 = (df['Lead_Sub_Brand'] == 'Other')
    f_2 = (df['Lead_Source'].str.contains('Newsletter', flags=re.I, regex=True))
    f_3 = (df['Email'] != 'empty')
    f_4 = (~df['Email_status'].str.contains('Bounce|Invalid|Unsubscribed', regex=True))
    f_5 = (df['Odyssey_Members'] == False)
    f_6 = (df['Do_Not_Mail'] == False)
    f_7 = (df['Do_Not_Contact'] == False)
    f_8 = (~df['Email'].str.contains('@karmagroup.com', flags=re.I, regex=True))

    # mengambil data yang email, phone dan mobilenya tidak kosong
        
    final_filter = (
        f_1 &
        f_2 &
        f_3 &
        f_4 &
        f_5 &
        f_6 &
        f_7 &
        f_8 
    )

    zoho_df = df.loc[final_filter].copy() # menggunakan copy untuk menghindari setting copy warning
    zoho_df.reset_index(drop=True, inplace=True)
    zoho_df

    return zoho_df

def get_kbb_vip_data(token, cols):
    array_df = []

    # mencari tanggal 8 hari kebelekang
    calculate_date = datetime.now() - timedelta(days=8)
    new_cal_date = str(calculate_date.strftime("%Y-%m-%d")).split(' ')
    first_date = new_cal_date[0]
    # first_date = '2022-12-06'

    # mencari tanggal hari ini
    today = date.today()
    second_date = today.strftime("%Y-%m-%d")
    # second_date = '2022-12-14'

    start_date = '\''+first_date+'T00:00:01+08:00\''
    end_date = '\''+second_date+'T23:59:59+08:00\''

    for x in range(99999):
        limit = 200
        offset = str(x*limit)

        query = "select id, Created_Time, First_Name, Last_Name, Email, Birthdate, Phone, Street, City, Country, Brand, Lead_Sub_Brand, Lead_Source, Lead_Source_Description, Lead_Locations, Lead_History, Website, Card_Number, Card_Expired, Do_you_live_in_Bali from Leads where ( Created_Time between "+start_date+" and "+end_date+") offset "+offset+" limit 200"

        url_get_lead = 'https://www.zohoapis.com/crm/v2/coql'
        headers = {'Authorization': 'Zoho-oauthtoken '+token}
        body = {
            "select_query": query
        }

        content_res = requests.post(url_get_lead, headers=headers, json=body).json()
        normalize = json_normalize(content_res['data'])
        df = pd.DataFrame(normalize)
        new_df = df[cols].copy()

        # jika jumlah data yang diloop masih ada atau lebih dari 0
        # memasukan df kedalam array_df
        if (content_res['info']['more_records'] == False):
            array_df.append(new_df)
            break
        # jika jumlah data sudah habis atau 0 maka akan menghentikan loop
        else:
            array_df.append(new_df)
    
    concat_df = pd.concat(array_df, ignore_index=True)

    concat_df['Lead_Locations'] = concat_df['Lead_Locations'].astype('string')
    concat_df['Lead_Locations'].replace('\[|\]|\'','', regex=True, inplace=True)

    return concat_df

def get_kbb_vip_filter(df):
    f_1 = (df['Lead_Source_Description'].str.contains('Karma Beach VIP membership sign up|Karma Beach Bali offer sign up|Karma Beach VIP membership sign up 2023', flags=re.I, regex=True))

    # mengambil data yang email, phone dan mobilenya tidak kosong
        
    final_filter = (
        f_1
    )

    zoho_df = df.loc[final_filter].copy() # menggunakan copy untuk menghindari setting copy warning
    zoho_df.reset_index(drop=True, inplace=True)
    zoho_df

    return zoho_df

def get_fb_ads_wedding_data(token, cols):
    array_df = []

    # mencari tanggal 8 hari kebelekang
    calculate_date = datetime.now() - timedelta(days=8)
    new_cal_date = str(calculate_date.strftime("%Y-%m-%d")).split(' ')
    first_date = new_cal_date[0]
    # first_date = '2022-12-06'

    # mencari tanggal hari ini
    today = date.today()
    second_date = today.strftime("%Y-%m-%d")
    # second_date = '2022-12-14'

    start_date = '\''+first_date+'T00:00:01+08:00\''
    end_date = '\''+second_date+'T23:59:59+08:00\''

    for x in range(99999):
        limit = 200
        offset = str(x*limit)

        query = "select id, Created_Time, Campaign_Name, First_Name, Last_Name, Email, Phone, Street, City, Country, Brand, Lead_Sub_Brand, Lead_Source, Lead_Source_Description, Lead_Locations, Lead_History, Website from Leads where ( Created_Time between "+start_date+" and "+end_date+") offset "+offset+" limit 200"

        url_get_lead = 'https://www.zohoapis.com/crm/v2/coql'
        headers = {'Authorization': 'Zoho-oauthtoken '+token}
        body = {
            "select_query": query
        }

        content_res = requests.post(url_get_lead, headers=headers, json=body).json()
        normalize = json_normalize(content_res['data'])
        df = pd.DataFrame(normalize)
        new_df = df[cols].copy()

        # jika jumlah data yang diloop masih ada atau lebih dari 0
        # memasukan df kedalam array_df
        if (content_res['info']['more_records'] == False):
            array_df.append(new_df)
            break
        # jika jumlah data sudah habis atau 0 maka akan menghentikan loop
        else:
            array_df.append(new_df)
    
    concat_df = pd.concat(array_df, ignore_index=True)

    concat_df['Lead_Locations'] = concat_df['Lead_Locations'].astype('string')
    concat_df['Lead_Locations'].replace('\[|\]|\'','', regex=True, inplace=True)

    return concat_df

def get_fb_ads_wedding_filter(df):
    f_1 = (df['Lead_History'].str.contains('meta', flags=re.I, regex=True))
    f_2 = (df['Lead_Locations'].str.contains('Karma Salford Hall|Karma Lake of Menteith', flags=re.I, regex=True))

    # mengambil data yang email, phone dan mobilenya tidak kosong
        
    final_filter = (
        f_1 & 
        f_2
    )

    zoho_df = df.loc[final_filter].copy() # menggunakan copy untuk menghindari setting copy warning
    zoho_df.reset_index(drop=True, inplace=True)
    zoho_df

    return zoho_df
