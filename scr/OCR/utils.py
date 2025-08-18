# utils.py

import os
from typing import List

def list_file_recursively(base_path: str) -> List[str]:
    """
    Lấy danh sách đường dẫn tương đối của tất cả các file trong một thư mục
    và các thư mục con của nó.

    Args:
        base_path (str): Đường dẫn đến thư mục gốc.

    Returns:
        List[str]: Danh sách các đường dẫn file tương đối.
    """
    file_list = []
    for root, _, files in os.walk(base_path):
        for file in files:
            # Tạo đường dẫn tương đối từ thư mục gốc
            relative_path = os.path.relpath(os.path.join(root, file), base_path)
            file_list.append(relative_path)
    return file_list