"""
Hybrid NLP utilities: rules-first, optional ML classifier (zero-shot).
Rules: deterministic regex for bucket names, region, resource names.
ML: optional HF zero-shot; guarded so missing torch or transformers won't crash.
"""
import re
import logging
import os

logger = logging.getLogger(__name__)

# Optional local ML classifier initialization (lazy)
_CLASSIFIER = None
try:
    from transformers import pipeline
    import torch
except Exception:
    pipeline = None
    torch = None

INTENT_LABELS = [
    "create_s3_bucket",
    "list_s3_buckets",
    "delete_s3_bucket",
    "list_s3_objects",
    "put_s3_object",
    "create_dynamodb_table",
    "list_dynamodb_tables",
    "list_ec2_instances",
    "describe_ec2_instances",
    "list_lambda_functions",
    "invoke_lambda_function",
    "list_iam_users",
    "create_iam_user",
    "delete_iam_user",
    "create_rds_instance",
    "list_rds_instances",
    "delete_rds_instance",
    "create_sqs_queue",
    "list_sqs_queues",
    "create_sns_topic",
    "list_sns_topics",
    "create_cloudformation_stack",
    "list_cloudformation_stacks",
    "list_cloudwatch_logs",
    "list_cloudwatch_metrics",
]

# simple rules (regex)
RE_BUCKET = re.compile(r'\b(?:s3\s+bucket|bucket)\s+(?:(?:named|called|name)\s+)?([a-z0-9][a-z0-9\-\._]{2,62})\b', re.I)
RE_REGION = re.compile(r'\b(us|eu|ap|sa|ca|me)[\-\_]?[a-z0-9\-]+-\d\b', re.I)
RE_NAME = re.compile(r'\bname[d]?[:\s]+([A-Za-z0-9\-\_]+)\b', re.I)
RE_TABLE = re.compile(r'\b(?:table|dynamodb table)\s+(?:named|called)?\s*([A-Za-z0-9\-\_]+)\b', re.I)
RE_DB = re.compile(r'\b(?:instance|database|db)\s+(?:named|called)?\s*([A-Za-z0-9\-\_]+)\b', re.I)
RE_POLICY_ARN = re.compile(r'(arn:aws:iam::aws:policy/[A-Za-z0-9+=,.@_-]+)', re.I)
RE_POLICY_NAME = re.compile(r'(ReadOnlyAccess|AdministratorAccess|PowerUserAccess)', re.I)
RE_USER = re.compile(r'\buser\s+(?:(?:named|called|name)\s+)?([A-Za-z0-9\-\_]+)\b', re.I)
RE_FUNCTION = re.compile(r'\bfunction\s+(?:(?:named|called|name)\s+)?([A-Za-z0-9\-\_]+)\b', re.I)
RE_QUEUE = re.compile(r'\bqueue\s+(?:(?:named|called|name)\s+)?([A-Za-z0-9\-\_]+)\b', re.I)
RE_TOPIC = re.compile(r'\btopic\s+(?:(?:named|called|name)\s+)?([A-Za-z0-9\-\_]+)\b', re.I)
RE_STACK = re.compile(r'\bstack\s+(?:(?:named|called|name)\s+)?([A-Za-z0-9\-\_]+)\b', re.I)

# --- S3 specific rule fallbacks ---
S3_RULES = [
    # create bucket
    (r"(?:create|make|add)\s+(?:an\s+)?s3\s+bucket(?:\s+(?:named|called|name))?\s+([A-Za-z0-9\-\._]+)(?:\s+in\s+([a-z0-9\-]+))?",
     ("create_s3_bucket", lambda m: {"bucket": m.group(1), "region": (m.group(2) or None)})),
    # list buckets
    (r"(?:list|show)\s+(?:all\s+)?s3\s+buckets",
     ("list_s3_buckets", lambda m: {})),
    # delete bucket
    (r"(?:delete|remove)\s+(?:s3\s+)?bucket\s+([A-Za-z0-9\-\._]+)",
     ("delete_s3_bucket", lambda m: {"bucket": m.group(1)})),
    # list objects
    (r"(?:list|show)\s+(?:objects|files)\s+(?:in|from)\s+(?:s3\s+)?bucket\s+([A-Za-z0-9\-\._]+)(?:\s+prefix\s+([A-Za-z0-9\-\._\/]+))?",
     ("list_s3_objects", lambda m: {"bucket": m.group(1), "prefix": m.group(2) if m.group(2) else None})),
    # put object (upload)
    (r"(?:upload|put)\s+file\s+([^\s]+)\s+(?:to|into)\s+(?:s3\s+)?bucket\s+([A-Za-z0-9\-\._]+)(?:\s+key\s+([A-Za-z0-9\-\._\/]+))?",
     ("put_s3_object", lambda m: {"local_path": m.group(1), "bucket": m.group(2), "key": m.group(3) if m.group(3) else None})),
]

# --- IAM specific rule fallbacks ---
def _extract_iam_entities(match):
    text = match.group(0)
    entities = {}
    policy_arn = RE_POLICY_ARN.search(text)
    policy_name = RE_POLICY_NAME.search(text)
    if policy_arn:
        entities["policy"] = policy_arn.group(1)
    elif policy_name:
        entities["policy"] = policy_name.group(1)
    user_match = RE_USER.search(text)
    if user_match:
        entities["user"] = user_match.group(1)
    return entities

IAM_INTENT_PATTERNS = [
    (r"(?:create|make|add)\s+(?:iam\s+)?user(?:\s+(?:named|called|name))?\s+([A-Za-z0-9\-\_]+)", ("create_iam_user", lambda m: {"user": m.group(1)})),
    (r"(?:delete|remove)\s+(?:production\s+)?(?:iam\s+)?user(?:\s+(?:named|called|name))?\s+([A-Za-z0-9\-\_]+)", ("delete_iam_user", lambda m: {"user": m.group(1)})),
    (r"attach\s+(\w+)\s+to\s+user\s+(\w+)", ("attach_user_policy", lambda m: {"policy": m.group(1), "user": m.group(2)})),
    (r"attach\s+.*policy.*\s+to\s+user\s+(\w+)", ("attach_user_policy", _extract_iam_entities)),
    (r"detach\s+(\w+)\s+from\s+user\s+(\w+)", ("detach_user_policy", lambda m: {"policy": m.group(1), "user": m.group(2)})),
    (r"detach\s+.*policy.*\s+from\s+user\s+(\w+)", ("detach_user_policy", _extract_iam_entities)),
    (r"list\s+.*policies.*\s+user\s+(\w+)", ("list_attached_user_policies", lambda m: {"user": m.group(1)})),
]

# Unified rules list - S3 rules first for priority
RULES = S3_RULES + [(pattern, (intent, extractor)) for pattern, (intent, extractor) in IAM_INTENT_PATTERNS]

def _get_local_classifier():
    global _CLASSIFIER
    if _CLASSIFIER is not None:
        return _CLASSIFIER
    if pipeline is None:
        logger.info("Transformers not available - ML classifier disabled.")
        return None
    try:
        _CLASSIFIER = pipeline("zero-shot-classification", model="typeform/distilbert-mnli")  # smaller model id
        logger.info("Local ML classifier initialized")
    except Exception as e:
        logger.exception("Failed to init local classifier: %s", e)
        _CLASSIFIER = None
    return _CLASSIFIER

def _ml_intent(text: str):
    clf = _get_local_classifier()
    if clf is None:
        return None
    res = clf(text, candidate_labels=INTENT_LABELS)
    # confidence check
    if len(res.get("scores", [])) and res["scores"][0] > 0.6:
        return res["labels"][0]
    return None

def parse_nlp(text: str):
    """ Return (intent, entities) """
    text = text.strip()
    
    # 1) try regex rules first
    for pattern, (intent, extractor) in RULES:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            entities = extractor(match)
            return intent, entities
    
    # 2) try basic rules
    # region
    region = None
    m = RE_REGION.search(text)
    if m:
        region = m.group(0)
    # bucket
    bucket = None
    m = RE_BUCKET.search(text)
    if m:
        bucket = m.group(1)
    # table name
    table = None
    m = RE_TABLE.search(text)
    if m:
        table = m.group(1)
    # database name
    db = None
    m = RE_DB.search(text)
    if m:
        db = m.group(1)
    # policy (ARN or name)
    policy = None
    m = RE_POLICY_ARN.search(text) or RE_POLICY_NAME.search(text)
    if m:
        policy = m.group(1)
    # user
    user = None
    m = RE_USER.search(text)
    if m:
        user = m.group(1)
    # lambda function
    function = None
    m = RE_FUNCTION.search(text)
    if m:
        function = m.group(1)
    # sqs queue
    queue = None
    m = RE_QUEUE.search(text)
    if m:
        queue = m.group(1)
    # sns topic
    topic = None
    m = RE_TOPIC.search(text)
    if m:
        topic = m.group(1)
    # cloudformation stack
    stack = None
    m = RE_STACK.search(text)
    if m:
        stack = m.group(1)
    # generic name
    name = None
    m = RE_NAME.search(text)
    if m:
        name = m.group(1)

    # quick heuristic map for simple phrases
    low = text.lower()
    if ("create" in low and "s3" in low) or ("create" in low and "bucket" in low):
        intent = "create_s3_bucket"
        entities = {"bucket": bucket or name or "my-bucket"}
        if region:
            entities["region"] = region
        return intent, entities
    if "list" in low and "s3" in low:
        return "list_s3_buckets", {"region": region} if region else {}
    if ("dynamodb" in low and "create" in low) or ("create" in low and "dynamo" in low):
        return "create_dynamodb_table", {"table": table or name or "myTable", "region": region} 
    if ("list" in low and "dynamodb" in low) or ("list" in low and "dynamo" in low):
        return "list_dynamodb_tables", {"region": region} if region else {}
    if "lambda" in low and "invoke" in low:
        return "invoke_lambda_function", {"function": function or name or "my-function", "region": region}
    if "lambda" in low and "list" in low:
        return "list_lambda_functions", {"region": region} if region else {}
    if "iam" in low and "create" in low:
        return "create_iam_user", {"user": user or name or "DevUser"}
    if "iam" in low and ("delete" in low or "remove" in low):
        if user or name:
            return "delete_iam_user", {"user": user or name}
        return "unknown", {"region": region, "bucket": bucket, "name": name}
    if ("iam" in low and "list" in low) or ("list iam" in low):
        return "list_iam_users", {}
    if ("rds" in low and "create" in low) or ("database" in low and "create" in low):
        return "create_rds_instance", {"db": db or name or "mydb", "region": region}
    if ("rds" in low and ("delete" in low or "remove" in low)) or ("database" in low and ("delete" in low or "remove" in low)):
        if db or name:
            return "delete_rds_instance", {"db": db or name, "region": region}
        return "unknown", {"region": region, "bucket": bucket, "name": name}
    if "rds" in low and "list" in low:
        return "list_rds_instances", {"region": region} if region else {}
    if "ec2" in low and ("list" in low or "describe" in low):
        return "list_ec2_instances", {"region": region} if region else {}
    if "sqs" in low and "create" in low:
        return "create_sqs_queue", {"queue": queue or name or "my-queue", "region": region}
    if "sqs" in low and "list" in low:
        return "list_sqs_queues", {"region": region} if region else {}
    if "sns" in low and "create" in low:
        return "create_sns_topic", {"topic": topic or name or "my-topic", "region": region}
    if "sns" in low and "list" in low:
        return "list_sns_topics", {"region": region} if region else {}
    if ("cloudformation" in low and "create" in low) or ("stack" in low and "create" in low):
        return "create_cloudformation_stack", {"stack": stack or name or "mystack", "region": region}
    if ("cloudformation" in low and "list" in low) or ("stack" in low and "list" in low):
        return "list_cloudformation_stacks", {"region": region} if region else {}
    if ("logs" in low and "cloudwatch" in low) or ("log group" in low):
        return "list_cloudwatch_logs", {"region": region} if region else {}
    if "metrics" in low and "cloudwatch" in low:
        return "list_cloudwatch_metrics", {"region": region} if region else {}

    # 3) try ML
    ml = _ml_intent(text)
    if ml:
        return ml, {"region": region, "bucket": bucket, "name": name}

    # fallback unknown
    return "unknown", {"region": region, "bucket": bucket, "name": name}
