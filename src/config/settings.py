# src/config/settings.py
import os


class Settings:
    def __init__(self):
        self.use_ml = True
        self.model_size = os.environ.get("MODEL_SIZE", "large")  # 'small' or 'large'
        # local model path (if bundled) or cache path for download
        self.local_model_small = os.environ.get("MODEL_SMALL_PATH", "/opt/models/small")
        self.local_model_large = os.environ.get("MODEL_LARGE_PATH", "/opt/models/large")
        self.model_id_small = "microsoft/DialoGPT-small"
        self.model_id_large = "microsoft/DialoGPT-large"
        self.aws_default_region = os.environ.get("AWS_REGION", "us-west-1")


SETTINGS = Settings()
