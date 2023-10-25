from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection
import requests
import time
from configparser import ConfigParser

# Package source: https://github.com/Salamek/huawei-lte-api

def notify(msg):

    #Read config.ini file
    config_object = ConfigParser()
    config_object.read("config.ini")

    #Get the password
    telinfo = config_object["TELEGRAM"]

    t_bot = format(telinfo["bot"])
    t_key = format(telinfo["key"])
    t_chat = format(telinfo["chat"])

    tel_message=requests.utils.quote(msg)
    tel_url = f"https://api.telegram.org/bot{t_bot}:{t_key}/sendMessage?chat_id={t_chat}&text={tel_message}"
    requests.get(tel_url)

def test_set_apn():
    #Read config.ini file
    config_object = ConfigParser()
    config_object.read("config.ini")

    #Get the password
    routerinfo = config_object["ROUTERINFO"]

    r_ip = format(routerinfo["ip"])
    r_login = format(routerinfo["loginid"])
    r_pass = format(routerinfo["password"])

    r_conn = f'http://{r_login}:{r_pass}@{r_ip}/'

    with Connection(r_conn) as connection:
        client = Client(connection) # This just simplifies access to separate API groups, you can use device = Device(connection) if you want

        apn_result = client.dial_up.profiles()

        s_text = 'ws.afrihost.fwa'

        found_ind = 0

        for key, value in apn_result.items():
            if s_text in str(key) or s_text in str(value):
                found_ind = 1

        if found_ind == 1:
            print(f"Found '{s_text}' ")
        else:
            print("No APN found, creating now...")
            client.dial_up.create_profile('AfriMTN',apn='ws.afrihost.fwa')
            time.sleep(30)
            notify("Created new Profile: AfriMTN")

def test_internet_access():
    while True:
        itt = 1
        try:
            r1 = requests.get('http://google.com', timeout=5)
            rt = r1.text

            index = rt.find('google')
            if index != -1:
                print(f"{itt}")
            else:
                print(f"'google not found!")
                try:
                    test_set_apn()
                except:
                    print("Cant set APN, sleep for 1 minute and try again")
                    time.sleep(60)
            itt = itt + 1

        except (requests.ConnectionError, requests.Timeout):
            print("No internet access!")
            print("Try to set APN")
            try:
                test_set_apn()
            except:
                print("Cant set APN, sleep for 1 minute and try again")
                time.sleep(60)

        # print("sleping now")
        time.sleep(60)


# Run the function
# notify("Router status tracking started")
test_internet_access()
