import ConfigParser


conf = ConfigParser.ConfigParser()
conf.read('./caesar.conf')

api_key = conf.get('credentials', 'api_key')
secret = conf.get('credentials', 'secret')
