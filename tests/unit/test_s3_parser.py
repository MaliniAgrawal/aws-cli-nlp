import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.parsers.s3 import parser as s3p

def test_create_s3_bucket():
    result = s3p.generate_command("create_s3_bucket", {"bucket": "my-bucket", "region": "us-west-1"})
    assert "my-bucket" in result["command"]
    assert "us-west-1" in result["command"]
    assert "aws s3 mb" in result["command"]

def test_list_buckets():
    result = s3p.generate_command("list_s3_buckets", {})
    assert result["command"] == "aws s3 ls"
    assert "Lists S3 buckets" in result["explanation"]

def test_delete_bucket():
    result = s3p.generate_command("delete_s3_bucket", {"bucket": "my-bucket"})
    assert "aws s3 rb s3://my-bucket --force" in result["command"]
    assert "Deletes S3 bucket" in result["explanation"]

def test_list_objects():
    result = s3p.generate_command("list_s3_objects", {"bucket": "my-bucket"})
    assert "aws s3 ls s3://my-bucket" in result["command"]
    assert "Lists objects" in result["explanation"]

def test_get_service():
    service = s3p.get_service()
    assert service["name"] == "s3"
    assert "create_s3_bucket" in service["intents"]
    assert "delete_s3_bucket" in service["intents"]
