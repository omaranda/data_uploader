"""Endpoint notifier module for MadXXX API integration."""

import os
import time
from typing import List, Dict, Any, Optional


class EndpointNotifier:
    """Build payloads for MadXXX job endpoint."""

    def __init__(self, api_key: str, api_endpoint: str = None):
        """Initialize endpoint notifier.

        Args:
            api_key: API key for authentication
            api_endpoint: API endpoint URL (optional, reads from MADXXX_API_URL env var)
        """
        self.api_key = api_key
        # Priority: parameter > env var
        # No hardcoded default - must be provided via parameter or MADXXX_API_URL env var
        self.api_endpoint = api_endpoint or os.getenv('MADXXX_API_URL')

        if not self.api_endpoint:
            raise ValueError(
                "API endpoint URL is required. Set MADXXX_API_URL environment variable "
                "or provide api_endpoint parameter."
            )

    def build_job_payload(
        self,
        s3_paths: List[str],
        job_name: Optional[str] = None,
        function_name: str = "register_audiofiles",
        module_name: str = "madxxx_workbench.audio.register_audio",
        sqs_queue: str = "madXXX_tasks_data_registration",
        sqs_region: str = "eu-west-1",
        custom_keywords: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build job payload for the MadXXX API.

        Args:
            s3_paths: List of S3 paths to process
            job_name: Job name (auto-generated if not provided)
            function_name: Function to call on backend
            module_name: Module path
            sqs_queue: SQS queue name
            sqs_region: SQS region
            custom_keywords: Custom keywords for job

        Returns:
            Payload dictionary
        """
        timestamp = int(time.time())
        job_name = job_name or f"register_audiofiles_{timestamp}"

        # Clean keywords: convert tuples to lists
        keywords = custom_keywords or {}
        cleaned_keywords = {}
        for key, value in keywords.items():
            if isinstance(value, tuple):
                cleaned_keywords[key] = list(value)
            else:
                cleaned_keywords[key] = value

        # Build payload: arguments must be a list of lists
        payload = {
            "job": {
                "arguments": [s3_paths],  # List of lists
                "function_name": function_name,
                "keywords": cleaned_keywords,
                "module_name": module_name,
                "name": job_name
            },
            "sqs_queue": sqs_queue,
            "sqs_region": sqs_region
        }

        return payload

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API.

        Returns:
            Headers dictionary
        """
        if not self.api_key:
            return {}

        return {
            'accept': 'application/json',
            'api_key': self.api_key,
            'Content-Type': 'application/json'
        }

    def build_s3_paths_from_session(
        self,
        bucket_name: str,
        s3_prefix: str,
        file_list: Optional[List[str]] = None
    ) -> List[str]:
        """Build S3 paths from session information.

        Args:
            bucket_name: S3 bucket name
            s3_prefix: S3 prefix
            file_list: Optional list of relative file paths

        Returns:
            List of S3 paths in format s3://bucket/prefix/file
        """
        if file_list:
            # If we have a specific file list, use it
            s3_paths = []
            for file_path in file_list:
                # Handle both absolute and relative paths
                if file_path.startswith('s3://'):
                    s3_paths.append(file_path)
                else:
                    # Remove leading slash if present
                    file_path = file_path.lstrip('/')
                    s3_path = f"s3://{bucket_name}/{s3_prefix}/{file_path}"
                    s3_paths.append(s3_path)
            return s3_paths
        else:
            # Return prefix path - API will need to list files
            return [f"s3://{bucket_name}/{s3_prefix}"]
