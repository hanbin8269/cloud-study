import argparse
import boto3
import time

import os
from dotenv import load_dotenv

load_dotenv()

ec2 = boto3.resource(
    "ec2",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

parser = argparse.ArgumentParser()
parser.add_argument("--instance-id")
args = parser.parse_args()
instance_id = args.instance_id
instance = ec2.Instance(instance_id)
volume_id = instance.block_device_mappings[0]["Ebs"][
    "VolumeId"
]  # instance로부터 volumeId 가져오기
volume = ec2.Volume(volume_id)

snapshot = volume.create_snapshot()  # snapshot 생성
print("기존 Volume Snapshot 생성 중 ...")
snapshot.wait_until_completed()  # 생성될떄 까지 대기
print("기존 Volume Snapshot 생성 완료")

resp = snapshot.copy(Encrypted=True, SourceRegion=os.getenv("AWS_REGION"))
encrypted_snapshot = ec2.Snapshot(resp["SnapshotId"]) # 암호화된 Snapshot 생성
print("기존 Volume Snapshot으로 부터 암호화된 Volume Snapshot 생성 중...")

encrypted_snapshot.wait_until_completed()
print("암호화된 Volume Snapshot 생성 완료")

encrypted_volume = ec2.create_volume(
    AvailabilityZone=instance.subnet.availability_zone, SnapshotId=encrypted_snapshot.id
)  # snapshot으로 볼륨 생성
print("암호화된 Volume 생성 완료")

device = volume.attachments[0]["Device"]

instance.stop()
print("인스턴스 중지 중...")

instance.wait_until_stopped()
print("인스턴스 중지 완료")

volume.detach_from_instance()
print("기존 볼륨 분리 중...")

while True:
    volume.reload()
    if volume.state == 'available':
        break
    time.sleep(15)
print("기존 볼륨 분리 완료")

encrypted_volume.attach_to_instance(
    Device=device,
    InstanceId=instance.id
)
print("암호화된 볼륨 연결 중...")

while True:
    encrypted_volume.reload()
    if encrypted_volume.state == 'in-use':
        break
    time.sleep(15)
print("암호화된 볼륨 연결 완료")

instance.start()
print("인스턴스 다시 시작 중...")

instance.wait_until_running()
print("인스턴스 다시 시작 완료")

volume.delete()
print("기존 볼륨 제거 및 모든 과정 완료")