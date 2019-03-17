import ConfigParser


conf = ConfigParser.ConfigParser()
conf.read('./caesar.conf')

api_key = conf.get('credentials', 'api_key')
secret = conf.get('credentials', 'secret')

strategy = conf.get('caesar', 'strategy').lower()
check_period = int(conf.get('caesar', 'check_period'))

if conf.get('caesar', 'backtesting') == 'True':
    backtesting = True
else:
    backtesting = False

period = int(conf.get('backtesting', 'period'))

fee = float(conf.get('strategy', 'fee'))
profit = float(conf.get('strategy', 'profit'))
loss = float(conf.get('strategy', 'loss'))
pair = conf.get('strategy', 'pair')
balance_percentage = float(conf.get('strategy', 'balance_percentage'))
desired_hole = float(conf.get('strategy', 'desired_hole'))

partitions = int(conf.get('chespirito', 'partitions'))
