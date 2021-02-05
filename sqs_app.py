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

sqs.create_queue(QueueName=QUEUE_NAME)

queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)

while True:
    print("다음 메세지 기다리는 중...")
    messages = queue.receive_messages()
    for message in messages:
        print("메세지 총" + str(len(messages)) + "개 발견됨")
        rand_sleeptime = random.randrange(15, 31)
        print("내용이 " + message.body + "인 메세지를 제거합니다... 약 15~30 초 소요")
        time.sleep(rand_sleeptime)
        message.delete()
        print("제거 완료")