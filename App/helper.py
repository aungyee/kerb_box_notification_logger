from datetime import datetime
from googledrive import append_row_to_google_sheets

def parseMessage(message):
    splitMessage = message.split(',')
    output = {
        'hostname':'',
        'action':'',
        'plate_number':'',
        'vehicle_type':'',
        'vehicle_color':'',
        'vehicle_model_make':'',
        'lo':'',
        'eth0':'',
        'wlan0':'',
        'tun0':'',
        'ppp0':'',
        'docker0':'',
        'vpn':'',
        'extra':'',
        'raw':message
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
            output['vehicle_type'] = item[item.find(' and vehicletype is ') + 20 :]
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
    return output


def writeToCSV(timestamp, parsedMessage):
    timestamp = datetime.fromtimestamp(float(timestamp))
    text = '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15}'\
        .format(
            timestamp.strftime("%m/%d/%Y"),
            timestamp.strftime("%H:%M:%S"),
            parsedMessage['hostname'],
            parsedMessage['action'],
            parsedMessage['plate_number'],
            parsedMessage['vehicle_type'],
            parsedMessage['vehicle_color'],
            parsedMessage['vehicle_model_make'],
            parsedMessage['lo'],
            parsedMessage['eth0'],
            parsedMessage['wlan0'],
            parsedMessage['tun0'],
            parsedMessage['ppp0'],
            parsedMessage['docker0'],
            parsedMessage['vpn'],
            parsedMessage['extra']
        )
    with open('logs/kerb_box_log.csv','a') as file:
        file.write(text)
        file.write('\n')


if __name__ == '__main__':
    writeToCSV('1638015202.003300',None)

def writeToGoogleSheet(timestamp, parsedMessage):
    timestamp = datetime.fromtimestamp(float(timestamp))
    message = [timestamp.strftime("%m/%d/%Y"),
            timestamp.strftime("%H:%M:%S"),
            parsedMessage['hostname'],
            parsedMessage['action'],
            parsedMessage['plate_number'],
            parsedMessage['vehicle_type'],
            parsedMessage['vehicle_color'],
            parsedMessage['vehicle_model_make'],
            parsedMessage['lo'],
            parsedMessage['eth0'],
            parsedMessage['wlan0'],
            parsedMessage['tun0'],
            parsedMessage['ppp0'],
            parsedMessage['docker0'],
            parsedMessage['vpn'],
            parsedMessage['extra']]
    
    append_row_to_google_sheets(message)