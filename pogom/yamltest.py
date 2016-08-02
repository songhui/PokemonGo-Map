import yaml
import twitter
conf_file = file('../huis_notification.yml', 'r')
config = yaml.load(conf_file)

print config[0]['type']
credential = config[0]['credential']

api = twitter.Api(**credential)
print(api.VerifyCredentials())

status = api.PostUpdate('My first twitter')
print(status)
