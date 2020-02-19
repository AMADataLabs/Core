import logging
import logging.handlers
import sys
from mongolog.handlers import MongoHandler

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

filehandler = logging.FileHandler(filename='local.log')
filehandler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
filehandler.setFormatter(formatter)
root.addHandler(filehandler)
root.addHandler(MongoHandler.to(db='mongolog', collection='log'))


'''
The above code uses three different handlers. A MongoDB handler, a file handler, and the
standard out of the system. These are all added as handlers to the logger.
'''
logging.info("Logs")

'''
You can view the logged message under msg neatly with the following.
db.log.find({}, {"msg":1, "asctime":1, "host":1}).pretty()
'''
