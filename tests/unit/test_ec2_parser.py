# tests/unit/test_ec2_parser.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from parsers.ec2 import parser as ec2p


def test_list_instances_no_region():
    res = ec2p.list_ec2_instances_handler({}, "list ec2 instances")
    assert "describe-instances" in res["command"]
    assert res["intent"] == "list_ec2_instances"


def test_list_instances_with_region():
    res = ec2p.list_ec2_instances_handler({}, "list ec2 instances in us-west-1")
    assert "--region us-west-1" in res["command"]
    assert res["entities"].get("region") == "us-west-1"


def test_start_stop_terminate_instance_missing_id():
    res = ec2p.start_ec2_instance_handler({}, "start instance")
    assert "Specify" in res["command"] or res["validation"]["reason"].startswith("missing")
    res2 = ec2p.stop_ec2_instance_handler({}, "stop instance")
    assert "Specify" in res2["command"] or res2["validation"]["reason"].startswith("missing")
    res3 = ec2p.terminate_ec2_instance_handler({}, "terminate instance")
    assert "Specify" in res3["command"] or res3["validation"]["reason"].startswith("missing")


def test_start_with_id_and_region():
    txt = "start instance i-0123456789abcdef0 in us-west-2"
    res = ec2p.start_ec2_instance_handler({}, txt)
    assert "start-instances" in res["command"]
    assert "i-0123456789abcdef0" in res["command"]
    assert "us-west-2" in res["command"]


def test_create_keypair_and_list():
    res = ec2p.create_ec2_keypair_handler({}, "create keypair named mykey")
    assert "create-key-pair" in res["command"]
    assert "mykey" in res["command"]
    res2 = ec2p.list_ec2_keypairs_handler({}, "list keypairs in us-west-1")
    assert "describe-key-pairs" in res2["command"]


def test_describe_instance_types():
    res = ec2p.describe_instance_types_handler({}, "describe instance types")
    assert "describe-instance-types" in res["command"]
