"""
License validation for AWS Marketplace integration
"""
import boto3
import json
from datetime import datetime
from loguru import logger

class LicenseValidator:
    def __init__(self):
        self.marketplace_client = boto3.client('marketplace-metering')
        self.product_code = "your-aws-marketplace-product-code"
    
    def validate_license(self):
        """Validate AWS Marketplace subscription"""
        try:
            # Check marketplace entitlement
            response = self.marketplace_client.meter_usage(
                ProductCode=self.product_code,
                Timestamp=datetime.utcnow(),
                UsageDimension='queries',
                UsageQuantity=1
            )
            
            return {
                "valid": True,
                "subscription": "active",
                "metering_record_id": response.get('MeteringRecordId')
            }
            
        except Exception as e:
            logger.warning(f"License validation failed: {e}")
            return {
                "valid": False,
                "error": str(e),
                "message": "Please subscribe via AWS Marketplace"
            }
    
    def check_usage_limits(self, current_usage: int):
        """Check if user exceeded daily limits"""
        daily_limit = 100  # Lite edition limit
        
        if current_usage >= daily_limit:
            return {
                "allowed": False,
                "message": f"Daily limit of {daily_limit} queries exceeded. Upgrade to Pro for unlimited queries."
            }
        
        return {
            "allowed": True,
            "remaining": daily_limit - current_usage
        }