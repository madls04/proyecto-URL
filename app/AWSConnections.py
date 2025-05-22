from dotenv import load_dotenv
import boto3
import os

class AWSConnections:
  def _init_(self):
    load_dotenv()
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = os.getenv("AWS_SHARED_CREDENTIALS_FILE")
    os.environ["AWS_CONFIG_FILE"] = os.getenv("AWS_CONFIG_FILE")
    os.environ["AWS_PROFILE"] = os.getenv("AWS_PROFILE")

    self.session = boto3.Session()

  def getSession(self):
    return self.session