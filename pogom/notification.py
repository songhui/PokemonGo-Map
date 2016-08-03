from .utils import get_pokemon_name
from pogom.utils import get_args
from datetime import datetime

import twitter
import yaml
import pytz
from tzlocal import get_localzone
from time import strftime, ctime

from . import config

args = get_args()
#temporarily disabling because -o and -i is removed from 51f651228c00a96b86f5c38d1a2d53b32e5d9862
#IGNORE = None
#ONLY = None
#if args.ignore:
#    IGNORE =  [i.lower().strip() for i in args.ignore.split(',')]
#elif args.only:
#    ONLY = [i.lower().strip() for i in args.only.split(',')]

class Notifier:
    def __init__(self, config):
        self.config = config
        self.filter = []
        for idstr in config['pokemons']:
            if type(idstr) is int:
                self.filter.append(idstr)
                continue
            assert type(idstr) is str
            idstr = idstr.strip()
            try:
                id = int(idstr)
                self.filter.append(id)
            except ValueError:
                if '-' in idstr:
                    (head, tail) = idstr.split("-")
                    self.filter.extend(range(int(head.strip()), int(tail.strip())+1))
        print self.filter

    def notify(self, id, name, lat, lng, expire):
        #print "!"+config['MULTI_POS_NAMES']
        if id in self.filter:
            self._notify(id, name, lat, lng, expire)

    def _notify(self, id, name, lat, lng, expire):
        pass

class TwitterNotifier(Notifier):
    def __init__(self, config):
        credential = config['credential']
        self.api = twitter.Api(**credential)
        #print(self.api.VerifyCredentials())
        Notifier.__init__(self, config)

    def _notify(self, id, name, lat, lng, expire):
        expire = expire.replace(tzinfo=pytz.timezone('UTC'))
        expire = expire.astimezone(get_localzone())
        timestr = expire.strftime("%H:%M:%S %Z")
        message = "A wild %s is here until %s http://maps.google.com/?q=%f,%f" % (name,timestr,lat,lng)
        try:
            prefix = config['MULTI_POS_NAMES'][config['CURRENT']]
            message = prefix + message
        except:
            pass

        print message
        try:
            status = self.api.PostUpdate(status=message) #TODO: Not using twitter for duplication checking
        except twitter.TwitterError:
            return
        #print(status)

notifiers = []

try:
    conf_file_path = args.background_notification
    conf_file = file(conf_file_path, 'r')
    notifiers_conf = yaml.load(conf_file)
    for config in notifiers_conf:
        if ('disabled' in config) and config['disabled']:
            continue
        if config['type'] == 'twitter':
            notifiers.append(TwitterNotifier(config))
except:
    print 'Invalid configuration file is invalid.'




def notifyPokemon(id,lat,lng,itime):

    pokemon_name = get_pokemon_name(id).encode('utf-8')
    pokemon_id = str(id)
    doPrint = True

    for notifier in notifiers:
        notifier.notify(id, pokemon_name, lat, lng, itime)
