import json, configparser, calendar, boto3, datetime, requests

NOW = datetime.datetime.now().strftime("%Y-%m-%d")
CURRDATE = datetime.datetime.strptime(NOW, '%Y-%m-%d')

REGION = 'eu-west-1'
CONFIGPATH = 'keyrotationConfig.txt'
config = configparser.ConfigParser()
config.read(CONFIGPATH)

USER_MAX_KEY_AGE = config['KEY']['AGE']
TELEGRAM_BOT_TOKEN = config['SECURITY']['BOT_TOKEN']
CHAT_ID = config['SECURITY']['CHAT_ID']
TGRAMURL = 'https://api.telegram.org/bot' + TELEGRAM_BOT_TOKEN + '/sendMessage?chat_id=' + CHAT_ID + '&text='

def lambda_handler(event, context):
    IAMCLIENT = boto3.client('iam')
    USERS = []
    KEYLIST = []
    RESPONSE = IAMCLIENT.list_users()
    NUMUSERS = len(RESPONSE['Users'])
    
    for INDEX in range(NUMUSERS):
      USERS.append(RESPONSE['Users'][INDEX]['UserName'])
    
    for USER in USERS:
        RESPONSE = IAMCLIENT.list_access_keys(UserName=USER)
        NUMKEYS = len(RESPONSE['AccessKeyMetadata'])

        for INDEX in range(NUMKEYS):
            USER_KEY_STATUS = RESPONSE['AccessKeyMetadata'][INDEX]['Status']
            USER_KEY_ID = RESPONSE['AccessKeyMetadata'][INDEX]['AccessKeyId']

            if USER_KEY_STATUS == 'Active':
                USER_KEY_DATE_CREATED = datetime.datetime.strptime(RESPONSE['AccessKeyMetadata'][INDEX]['CreateDate'].strftime("%Y-%m-%d"), '%Y-%m-%d')
                USER_KEY_AGE = CURRDATE - USER_KEY_DATE_CREATED

                if USER_KEY_AGE.days > int(USER_MAX_KEY_AGE):
                    USER_NAME = RESPONSE['AccessKeyMetadata'][INDEX]['UserName']
                    KEYLIST.append("Key: " + str(USER_KEY_ID) + " for IAM user: " + USER_NAME + " is required to be rotated. Key Age = " + str(USER_KEY_AGE.days) + " days.")
      
    if len(KEYLIST) > 0:        
        MSG = '\n'.join(map(str, KEYLIST))
        RESPONSE = requests.post(TGRAMURL + MSG)

