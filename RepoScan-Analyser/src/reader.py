import chardet
import os
from typing import Tuple, Optional

class FileReader:
    @staticmethod
    def read_file(file_path: str) -> Tuple[Optional[str], str]:
        """
        Reads a file and returns its content and encoding.
        Returns (content, encoding) or (None, error_message).
        """
        try:
            # First, try reading as binary to detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            
            if not encoding:
                # Fallback to utf-8 if detection fails
                encoding = 'utf-8'
                
            # If confidence is low, might be worth trying utf-8 first
            try:
                content = raw_data.decode(encoding)
            except UnicodeDecodeError:
                # Fallback: try common encodings
                for enc in ['utf-8', 'windows-1252', 'latin-1']:
                    try:
                        content = raw_data.decode(enc)
                        encoding = enc
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    return None, "Failed to decode file with detected or fallback encodings."

            return content, encoding

        except Exception as e:
            return None, str(e)
