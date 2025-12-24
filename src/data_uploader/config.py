"""Configuration management for data uploader."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Configuration for upload session."""

    local_directory: str
    bucket_name: str
    s3_prefix: str
    max_workers: int = 15
    aws_region: str = "eu-west-1"
    times_to_retry: int = 3
    aws_profile: str = "default"
    use_find: bool = True

    # Database configuration
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "data_uploader"
    db_user: str = "uploader"
    db_password: str = "uploader_pass"

    # Optional endpoint for downstream processing
    endpoint_url: Optional[str] = None

    @classmethod
    def from_json_file(cls, config_path: str) -> "Config":
        """Load configuration from JSON file.

        Args:
            config_path: Path to JSON configuration file

        Returns:
            Config object

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid JSON
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            data = json.load(f)

        # Convert use_find string to boolean
        if isinstance(data.get('use_find'), str):
            data['use_find'] = data['use_find'].lower() in ('yes', 'true', '1')

        return cls(**data)

    @classmethod
    def from_env(cls) -> "Config":
        """Load database configuration from environment variables.

        Returns:
            Config object with database settings from environment
        """
        return cls(
            local_directory="",
            bucket_name="",
            s3_prefix="",
            db_host=os.getenv("DB_HOST", "localhost"),
            db_port=int(os.getenv("DB_PORT", "5432")),
            db_name=os.getenv("DB_NAME", "data_uploader"),
            db_user=os.getenv("DB_USER", "uploader"),
            db_password=os.getenv("DB_PASSWORD", "uploader_pass"),
        )

    def merge_with_env(self) -> "Config":
        """Merge configuration with environment variables.

        Database credentials from environment take precedence.

        Returns:
            Updated Config object
        """
        self.db_host = os.getenv("DB_HOST", self.db_host)
        self.db_port = int(os.getenv("DB_PORT", str(self.db_port)))
        self.db_name = os.getenv("DB_NAME", self.db_name)
        self.db_user = os.getenv("DB_USER", self.db_user)
        self.db_password = os.getenv("DB_PASSWORD", self.db_password)
        return self

    def to_dict(self) -> dict:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "local_directory": self.local_directory,
            "bucket_name": self.bucket_name,
            "s3_prefix": self.s3_prefix,
            "max_workers": self.max_workers,
            "aws_region": self.aws_region,
            "times_to_retry": self.times_to_retry,
            "aws_profile": self.aws_profile,
            "use_find": self.use_find,
            "endpoint_url": self.endpoint_url,
        }

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.local_directory:
            raise ValueError("local_directory is required")

        if not os.path.exists(self.local_directory):
            raise ValueError(f"local_directory does not exist: {self.local_directory}")

        if not self.bucket_name:
            raise ValueError("bucket_name is required")

        if not self.s3_prefix:
            raise ValueError("s3_prefix is required")

        if self.max_workers < 1:
            raise ValueError("max_workers must be at least 1")

        if self.times_to_retry < 0:
            raise ValueError("times_to_retry must be non-negative")
