import os
import sys
import subprocess
import pkg_resources
import configparser
import traceback

required = {'telethon' , 'tqdm', 'requests'} 
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    # implement pip as a subprocess:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install',*missing])

from telethon.sync import TelegramClient, events
from telethon.tl.types import InputMessagesFilterDocument
from tqdm import tqdm
import  requests

def sendWebhook(dictParams):
    if config['DEFAULT']['webhook_path']:
        try:
            url = config['DEFAULT']['webhook_path']
            r = requests.post(url, json = dictParams )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e :
            print("Server is down")
        except Exception as e:
            print(e)
    
class DownloadProgressBar(tqdm):
    def update_to(self, current, total):
        self.total = total
        self.update(current - self.n)

config = configparser.ConfigParser()

# You need change the values in example.ini or creat your own config.ini
configName = 'config.ini'
os.path.join(os.path.dirname(__file__), configName)

if not config.read(os.path.join(os.path.dirname(__file__), configName)):
    configName = 'example.ini'
    config.read(os.path.join(os.path.dirname(__file__), configName))

api_id = int(config['DEFAULT']['api_id'])
api_hash = config['DEFAULT']['api_hash']
try:
    with TelegramClient('session_name', api_id, api_hash) as client:
        messages = client.get_messages(config['DEFAULT']['group_name'],
                                        offset_id=int(config['DEFAULT']['offset_id']),
                                        min_id=int(config['DEFAULT']['min_id']),
                                        limit=99999999,
                                        filter=InputMessagesFilterDocument)
        toDownload = []
        # Fetching messages to know what will we download before we actually start to avoid timeout during the download
        for msg in tqdm(messages):
            if msg.file is not None:
                toDownload.append(msg.id)


        print(toDownload)
        print()
        
        totalsize = len(toDownload)
        current = 0

        # Start the actual ripping 
        for msgId in tqdm(reversed(toDownload), position=0):
            current += 1

            # Fetching the message again because if we use the first one we would get timeout after few hours.
            # offset_id is the maximum message ID, thus we need to add 1 a message to get the requested message. 
            y = client.get_messages(config['DEFAULT']['group_name'], limit=1, offset_id=msgId+1)
            
            # Photo might not have filename
            filename = y[0].file.name if y[0].file.name is not None else y[0].text
            info = str(current) + "of" + str(totalsize) + "\n\rMESSAGE_ID: " + str(msgId) + "\n\r" + filename
            print(info)

            with DownloadProgressBar(unit='B', unit_scale=True) as t:
                # The actual download operation
                client.download_media(y[0], config['DEFAULT']['folder_path'] , progress_callback=t.update_to)

            # Finished download, mark as complete 
            config['DEFAULT']['min_id'] = str(msgId)
            with open(os.path.join(os.path.dirname(__file__), configName), 'w') as configfile:
                config.write(configfile)

            # Eknowledge to server that 
            sendWebhook( dict( Text = info ))

# In there was a problem, tell us about it.
except KeyboardInterrupt:
    # Nothing we can ignore
    pass
except Exception as e:
    sendWebhook(dict(Error = traceback.format_exception(*sys.exc_info())))
    raise e # reraises the exception so it would be visible on VPS log.
