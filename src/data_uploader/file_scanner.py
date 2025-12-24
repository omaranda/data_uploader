"""File discovery module supporting both find command and Python-based scanning."""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Generator, Callable, Optional


class FileScanner:
    """Scan directories for files to upload."""

    SUPPORTED_EXTENSIONS = {'.wav', '.jpg', '.jpeg', '.mp4', '.mov', '.avi'}

    def __init__(self, use_find: bool = True, progress_callback: Optional[Callable[[int], None]] = None):
        """Initialize file scanner.

        Args:
            use_find: Use native find command (faster) vs Python walking
            progress_callback: Optional callback for progress updates (called every 10k files)
        """
        self.use_find = use_find and self._can_use_find()
        self.progress_callback = progress_callback

    @staticmethod
    def _can_use_find() -> bool:
        """Check if find command is available.

        Returns:
            True if find command is available (Linux/macOS)
        """
        return sys.platform != 'win32'

    def scan(self, directory: str) -> List[str]:
        """Scan directory for supported files.

        Args:
            directory: Directory to scan

        Returns:
            List of file paths

        Raises:
            ValueError: If directory doesn't exist
        """
        if not os.path.exists(directory):
            raise ValueError(f"Directory does not exist: {directory}")

        if not os.path.isdir(directory):
            raise ValueError(f"Path is not a directory: {directory}")

        if self.use_find:
            return self._scan_with_find(directory)
        else:
            return self._scan_with_python(directory)

    def _scan_with_find(self, directory: str) -> List[str]:
        """Scan using native find command.

        Args:
            directory: Directory to scan

        Returns:
            List of file paths
        """
        # Build find command for all supported extensions
        extensions_lower = [ext.lower() for ext in self.SUPPORTED_EXTENSIONS]
        extensions_upper = [ext.upper() for ext in self.SUPPORTED_EXTENSIONS]
        all_extensions = extensions_lower + extensions_upper

        # Build find command with -iname for case-insensitive matching
        find_conditions = []
        for ext in self.SUPPORTED_EXTENSIONS:
            find_conditions.extend(['-o', '-iname', f'*{ext}'])

        # Remove leading '-o'
        find_conditions = find_conditions[1:]

        cmd = ['find', directory, '-type', 'f', '('] + find_conditions + [')']

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            files = [line.strip() for line in result.stdout.split('\n') if line.strip()]

            # Report progress
            if self.progress_callback:
                for i, _ in enumerate(files, 1):
                    if i % 10000 == 0:
                        self.progress_callback(i)

            return files

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Find command failed: {e.stderr}")

    def _scan_with_python(self, directory: str) -> List[str]:
        """Scan using Python's os.walk.

        Args:
            directory: Directory to scan

        Returns:
            List of file paths
        """
        files = []
        count = 0

        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    files.append(os.path.join(root, filename))
                    count += 1

                    if self.progress_callback and count % 10000 == 0:
                        self.progress_callback(count)

        return files

    def scan_streaming(self, directory: str) -> Generator[str, None, None]:
        """Scan directory and yield files as they're found.

        Useful for very large directories to avoid loading all paths into memory.

        Args:
            directory: Directory to scan

        Yields:
            File paths
        """
        if not os.path.exists(directory):
            raise ValueError(f"Directory does not exist: {directory}")

        if self.use_find:
            yield from self._scan_with_find_streaming(directory)
        else:
            yield from self._scan_with_python_streaming(directory)

    def _scan_with_find_streaming(self, directory: str) -> Generator[str, None, None]:
        """Stream files using find command.

        Args:
            directory: Directory to scan

        Yields:
            File paths
        """
        find_conditions = []
        for ext in self.SUPPORTED_EXTENSIONS:
            find_conditions.extend(['-o', '-iname', f'*{ext}'])
        find_conditions = find_conditions[1:]

        cmd = ['find', directory, '-type', 'f', '('] + find_conditions + [')']

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        count = 0
        for line in process.stdout:
            file_path = line.strip()
            if file_path:
                yield file_path
                count += 1

                if self.progress_callback and count % 10000 == 0:
                    self.progress_callback(count)

        process.wait()
        if process.returncode != 0:
            stderr = process.stderr.read()
            raise RuntimeError(f"Find command failed: {stderr}")

    def _scan_with_python_streaming(self, directory: str) -> Generator[str, None, None]:
        """Stream files using Python's os.walk.

        Args:
            directory: Directory to scan

        Yields:
            File paths
        """
        count = 0
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    yield os.path.join(root, filename)
                    count += 1

                    if self.progress_callback and count % 10000 == 0:
                        self.progress_callback(count)

    @staticmethod
    def get_file_type(file_path: str) -> str:
        """Get file type from extension.

        Args:
            file_path: Path to file

        Returns:
            File type (WAV, JPG, or VIDEO)
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.wav':
            return 'WAV'
        elif ext in {'.jpg', '.jpeg'}:
            return 'JPG'
        elif ext in {'.mp4', '.mov', '.avi'}:
            return 'VIDEO'
        else:
            return 'UNKNOWN'

    @staticmethod
    def get_relative_path(file_path: str, base_directory: str) -> str:
        """Get relative path for S3 key generation.

        Args:
            file_path: Absolute file path
            base_directory: Base directory to make relative to

        Returns:
            Relative path
        """
        return os.path.relpath(file_path, base_directory)
