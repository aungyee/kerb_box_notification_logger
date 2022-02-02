import pandas as pd
from dateutil import tz
from datetime import datetime
from googledrive import append_row_to_notif_google_sheets, append_row_to_customer_support_google_sheets


def parseNotificationMessage(message):
    splitMessage = message.split(',')
    output = {
        'hostname': '',
        'hostname0': '',
        'hostname1': '',
        'hostname2': '',
        'hostname3': '',
        'hostname4': '',
        'hostname5': '',
        'hostname6': '',
        'action': '',
        'plate_number': '',
        'plate_number_prob': '',
        'vehicle_type': '',
        'vehicle_type_prob': '',
        'vehicle_color': '',
        'vehicle_color_prob': '',
        'vehicle_model_make': '',
        'vehicle_model_make_prob': '',
        'lo': '',
        'eth0': '',
        'wlan0': '',
        'tun0': '',
        'ppp0': '',
        'docker0': '',
        'vpn': '',
        'extra': '',
        'raw': message
    }

    for item in splitMessage:
        item = item.strip().lower()
        if item.startswith('hostname: '):
            output['hostname'] = item[10:]
        elif item.startswith('open gate') and item.find('plate') == -1:
            output['action'] = 'open gate'
        elif item.startswith('open gate for plate ') and ' and vehicletype is ' in item:
            output['action'] = 'open gate'
            output['plate_number'] = item[20:item.find(' and vehicletype is ')]
            output['vehicle_type'] = item[item.find(' and vehicletype is ') + 20:]
        elif item.startswith('open gate for plate none'):
            output['action'] = 'open gate'
            output['plate_number'] = 'None'
        elif item.startswith('vehiclecolor '):
            output['vehicle_color'] = item[13:]
        elif item.startswith('vehiclemodelmake '):
            output['vehicle_model_make'] = item[17:]
        elif item.startswith('network: lo: '):
            output['action'] = 'reset'
            output['lo'] = item[13:]
        elif item.startswith('eth0: '):
            output['action'] = 'reset'
            output['eth0'] = item[6:]
        elif item.startswith('wlan0: '):
            output['action'] = 'reset'
            output['wlan0'] = item[7:]
        elif item.startswith('tun0: '):
            output['action'] = 'reset'
            output['tun0'] = item[6:]
        elif item.startswith('ppp0:'):
            output['action'] = 'reset'
            output['ppp0'] = item[6:]
        elif item.startswith('docker0: '):
            output['action'] = 'reset'
            output['docker0'] = item[9:]
        elif item.find('failover connection to') != -1:
            output['action'] = 'connection error'
            output['hostname'] = item[:item.find('failover') - 1]
            output['vpn'] = item[item.find('failover') + 23:]
        else:
            output['extra'] = item[0:]

    if output['hostname'].find('power disconnected') != -1:
        output['hostname'] = output['hostname'][:output['hostname'].find(' messagges: power')]
        output['action'] = 'power disconnected'

    if output['hostname'].find('power connected again') != -1:
        output['hostname'] = output['hostname'][:output['hostname'].find(' messagges: power')]
        output['action'] = 'power connected'

    if output['hostname'] != '':
        hostname = output['hostname']
        hostnameList = hostname.split('-')

        for index, value in enumerate(hostnameList):
            output['hostname' + str(index)] = value

    if output['plate_number'] != '' and output['plate_number'].find('(') != -1:
        plateNumber = output['plate_number']
        output['plate_number_prob'] = plateNumber[plateNumber.find('(') + 1:plateNumber.find(')')]
        output['plate_number'] = plateNumber[:plateNumber.find('(')]

    if output['vehicle_type'] != '':
        vehicleType = output['vehicle_type']
        output['vehicle_type_prob'] = vehicleType[vehicleType.find('(') + 1:vehicleType.find(')')]
        output['vehicle_type'] = vehicleType[:vehicleType.find('(')]

    if output['vehicle_color'] != '':
        vehicleColor = output['vehicle_color']
        output['vehicle_color_prob'] = vehicleColor[vehicleColor.find('(') + 1:vehicleColor.find(')')]
        output['vehicle_color'] = vehicleColor[:vehicleColor.find('(')]

    if output['vehicle_model_make'] != '':
        vehicleModel = output['vehicle_model_make']
        output['vehicle_model_make_prob'] = vehicleModel[vehicleModel.find('(') + 1:vehicleModel.find(')')]
        output['vehicle_model_make'] = vehicleModel[:vehicleModel.find('(')]

    return output


def parseCustomerSupportGateMessage(message):

    output = {
        'hostname': '',
        'hostname0': '',
        'hostname1': '',
        'hostname2': '',
        'hostname3': '',
        'hostname4': '',
        'hostname5': '',
        'hostname6': '',
        'problem': '',
        'raw': message}

    splitMessage = message.lower().split(' ')
    output['hostname'] = splitMessage[0]

    error = ''

    for i in range(1,len(splitMessage)):
        error = error + splitMessage[i] + ' '

    output['problem'] = error.strip()

    if output['hostname'] != '':
        hostname = output['hostname']
        hostnameList = hostname.split('-')

        for index, value in enumerate(hostnameList):
            output['hostname' + str(index)] = value

    return output


def getLocalTime(timestamp, hostname):

    boxes = pd.read_csv('config/boxes.csv')
    if hostname in boxes['hostname'].values:
        row = boxes[boxes['hostname'] == hostname]
        timezone = tz.gettz(row['timezone'].values[0])
        localTime = datetime.fromtimestamp(float(timestamp), tz = timezone)
        return localTime, row['timezone'].values[0]
    else:
        formats = pd.read_csv('config/format.csv')
        hostname0 = hostname.split('-')[0]
        if hostname0 in formats['hostname0'].values:
            timezone = formats[formats['hostname0'] == hostname0]['timezone'][0]
            with open('config/boxes.csv','a') as file:
                stringToWrite = hostname + ',' + ',' + ',' + timezone
                file.write(stringToWrite)
                file.write('\n')
            return getLocalTime(timestamp,hostname)
        else:
            return None, None


def writeToNotificationGoogleSheet(timestamp, parsedMessage):
    utcTime = datetime.fromtimestamp(float(timestamp))
    localDatetime = 'Unknown'
    localDate = 'Unknown'
    localTime = 'Unknown'
    timezone = 'Unknown'

    ltime, tzone = getLocalTime(timestamp, parsedMessage['hostname'])

    if ltime:
        localTime = ltime.strftime("%H:%M:%S")
        localDate = ltime.strftime("%d/%m/%Y")
        localDatetime = ltime.strftime("%d/%m/%Y %H:%M:%S")
        timezone = tzone

    message = [utcTime.strftime("%d/%m/%Y %H:%M:%S"),
               utcTime.strftime("%d/%m/%Y"),
               utcTime.strftime("%H:%M:%S"),
               localDatetime,
               localDate,
               localTime,
               timezone,
               parsedMessage['hostname'],
               parsedMessage['hostname0'],
               parsedMessage['hostname1'],
               parsedMessage['hostname2'],
               parsedMessage['hostname3'],
               parsedMessage['hostname4'],
               parsedMessage['hostname5'],
               parsedMessage['hostname6'],
               parsedMessage['action'],
               parsedMessage['plate_number'],
               parsedMessage['plate_number_prob'],
               parsedMessage['vehicle_type'],
               parsedMessage['vehicle_type_prob'],
               parsedMessage['vehicle_color'],
               parsedMessage['vehicle_color_prob'],
               parsedMessage['vehicle_model_make'],
               parsedMessage['vehicle_model_make_prob'],
               parsedMessage['lo'],
               parsedMessage['eth0'],
               parsedMessage['wlan0'],
               parsedMessage['tun0'],
               parsedMessage['ppp0'],
               parsedMessage['docker0'],
               parsedMessage['vpn'],
               parsedMessage['extra'],
               parsedMessage['raw']]

    append_row_to_notif_google_sheets(message)


def writeToSupportGoogleSheet(timestamp, parsedMessage):
    utcTime = datetime.fromtimestamp(float(timestamp))
    localDatetime = 'Unknown'
    localDate = 'Unknown'
    localTime = 'Unknown'
    timezone = 'Unknown'

    ltime, tzone = getLocalTime(timestamp, parsedMessage['hostname'])

    if ltime:
        localTime = ltime.strftime("%H:%M:%S")
        localDate = ltime.strftime("%d/%m/%Y")
        localDatetime = ltime.strftime("%d/%m/%Y %H:%M:%S")
        timezone = tzone

    message = [utcTime.strftime("%d/%m/%Y %H:%M:%S"),
               utcTime.strftime("%d/%m/%Y"),
               utcTime.strftime("%H:%M:%S"),
               localDatetime,
               localDate,
               localTime,
               timezone,
               parsedMessage['hostname'],
               parsedMessage['hostname0'],
               parsedMessage['hostname1'],
               parsedMessage['hostname2'],
               parsedMessage['hostname3'],
               parsedMessage['hostname4'],
               parsedMessage['hostname5'],
               parsedMessage['hostname6'],
               parsedMessage['problem'],
               parsedMessage['raw']
               ]

    append_row_to_customer_support_google_sheets(message)
