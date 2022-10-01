from flask import Flask, request, abort
import ssl
import requests
import psutil
import platform
import json
import datetime
import pandas as pd
import json
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.powerbidedicated import PowerBIDedicated
from db import *

credential = AzureCliCredential()
subscription_id = ''
resource_client = ResourceManagementClient(credential, subscription_id)
powerbi_client = PowerBIDedicated(credential, subscription_id)

#create telegram bot to receive token. used to send updates
def telegram_bot_sendtext(botmessage):
    TOKEN = ''
    contactID = ''
    send_text = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + contactID + '&parse_mode=Markdown&text=' + botmessage
    response = requests.get(send_text)


app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        r = request.json
        print('webhook received')
        current_tier = powerbi_client.capacities.get_details('Platform', 'gen2embedded')
        if r['data']['context']['name'] == 'Less than 30':
            if int(current_tier.sku.name[1]) == 1:
                print(f'No need to scale {current_tier.sku.name}')
                telegram_bot_sendtext(f'No need to scale {current_tier.sku.name}')
                telegram_bot_sendtext(f"Metric Value: {r['data']['context']['condition']['allOf'][0]['metricValue']}")
 
            else:
                print(f'Scaling down from {current_tier.sku.name}')
                telegram_bot_sendtext(f'Scaling down from {current_tier.sku.name}')
                telegram_bot_sendtext(f"Metric Value: {r['data']['context']['condition']['allOf'][0]['metricValue']}")
                powerbi_client.capacities.begin_update('Platform', 'gen2embedded', {'sku': {'name': f'A{int(current_tier.sku.name[1]) - 1}'}})

        elif r['data']['context']['name'] == 'More than 80':
            if int(current_tier.sku.name[1]) == 4:
                print(f'No need to scale {current_tier.sku.name}')
                telegram_bot_sendtext(f'No need to scale {current_tier.sku.name}')
                telegram_bot_sendtext(f"Metric Value: {r['data']['context']['condition']['allOf'][0]['metricValue']}")
            else:
                print(f'Scaling up from {current_tier.sku.name}')
                telegram_bot_sendtext(f'Scaling up from {current_tier.sku.name}')
                telegram_bot_sendtext(f"Metric Value: {r['data']['context']['condition']['allOf'][0]['metricValue']}")
                powerbi_client.capacities.begin_update('Platform', 'gen2embedded', {'sku': {'name': f'A{int(current_tier.sku.name[1]) + 1}'}})
        else:
            print(r['data']['context']['name'])
            telegram_bot_sendtext(r['data']['context']['name'])
            telegram_bot_sendtext(f'Current tier is {current_tier.sku.name}')



        return 'sucess', 200
    else:
        abort(400)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
