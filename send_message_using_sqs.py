import boto3
import random
import time
import os
from dotenv import load_dotenv

load_dotenv()
QUEUE_NAME=os.getenv("AWS_QUEUE_NAME")

sqs = boto3.resource('sqs',
                     region_name=os.getenv("AWS_REGION"),
                     aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                     aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
                     )

queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)

while True:
    send_delay = random.randrange(1,16)
    print("새로운 메세지 보내는중...")
    time.sleep(send_delay)
    response = queue.send_message(MessageBody='hello, ' + QUEUE_NAME)
    print("메세지 전송 완료")