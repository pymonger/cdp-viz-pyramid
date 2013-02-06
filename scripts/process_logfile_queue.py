#!/usr/bin/env python
import pika, socket, time

from cdp_viz.lib.pikaUtils import pika_callback
from cdp_viz.handlers.services.logfile import uploadAndIndex

pika.log.setup(pika.log.DEBUG, color=True)


@pika_callback("logfile_upload")
def logfile_callback(ch, method, properties, body):
    uploadAndIndex(body)
    
if __name__ == "__main__":
    connection = None
    print "Starting up queue worker for logfile_upload."
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host='localhost'))
            break
        except socket.error, e:
            print "Failed to connect: %s" % str(e)
            time.sleep(1)
    
    #set logfile upload worker
    channel = connection.channel()
    channel.queue_declare(queue='logfile_upload', durable=True)
    pika.log.info(' [*] Waiting for logfiles to process.')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(logfile_callback,
                          queue='logfile_upload')
    
    pika.log.info('To exit press CTRL+C')

    channel.start_consuming()
