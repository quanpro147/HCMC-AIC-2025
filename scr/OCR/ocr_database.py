# ocr_database.py

import os
import json
from elasticsearch import helpers

# Import các thành phần từ 2 file vừa tạo
from helpers import elastic_client, vietnamese_index_settings
from utils import list_file_recursively

class OcrDB:
    def __init__(self, OCR_base_path="./texts_extracted", remove_old_index=False):
        """
        Khởi tạo cơ sở dữ liệu OCR, kết nối tới Elasticsearch và lập chỉ mục dữ liệu.
        
        Args:
            OCR_base_path (str): Thư mục chứa các file JSON kết quả OCR.
            remove_old_index (bool): Cờ để quyết định có xóa và tạo lại index cũ không.
        """
        self.remove_old_index = remove_old_index
        # self.db = self.load_ocr(OCR_base_path) # Dòng này không cần thiết cho việc lập chỉ mục
        self.elastic_client = elastic_client
        self.create_index(OCR_base_path)

    def create_index(self, base_path):
        """
        Tạo index trong Elasticsearch và nạp dữ liệu từ các file JSON.
        """
        index_name = "ocr" # Đặt tên cho index

        if self.elastic_client.indices.exists(index=index_name):
            print(f"Index '{index_name}' đã tồn tại.")
            if not self.remove_old_index:
                print("Bỏ qua việc tạo index mới.")
                return
            print(f"Xóa index cũ '{index_name}'...")
            self.elastic_client.indices.delete(index=index_name, ignore=[400, 404])

        print(f"Tạo index mới '{index_name}' với cài đặt tiếng Việt...")
        self.elastic_client.indices.create(index=index_name, body=vietnamese_index_settings)

        ocr_files = list_file_recursively(base_path)
        
        if not ocr_files:
            print(f"Cảnh báo: Không tìm thấy file OCR nào trong thư mục '{base_path}'.")
            return

        print(f"Tìm thấy {len(ocr_files)} file OCR. Bắt đầu lập chỉ mục...")
        
        actions = []
        for ocr_file in ocr_files:
            if not ocr_file.endswith(".json"):
                print(f"Cảnh báo: Bỏ qua file không phải JSON: {ocr_file}")
                continue

            video_path = os.path.join(base_path, ocr_file)
            vid_name = os.path.splitext(ocr_file)[0] # Lấy tên video (bỏ phần .json)

            with open(video_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for keyframe_name, text in data.items():
                # Tiền xử lý văn bản
                clean_text = text.lower().replace("\n", " ").replace("_", " ")
                
                # Lấy ID keyframe (chỉ lấy phần số)
                keyframe_id_str = os.path.splitext(keyframe_name)[0]
                
                document = {
                    "_index": index_name,
                    "_source": {
                        "vid_name": vid_name,
                        "keyframe_id": int(keyframe_id_str) if keyframe_id_str.isdigit() else 0,
                        "text": clean_text,
                    }
                }
                actions.append(document)

        # Sử dụng helpers.bulk để đẩy dữ liệu hiệu quả
        helpers.bulk(self.elastic_client, actions)
        print("Lập chỉ mục hoàn tất!")

    # Hàm này dùng để load dữ liệu vào RAM, không cần thiết cho việc lập chỉ mục vào ES
    # def load_ocr(self, OCR_base_path):
    #     database = []
    #     ocr_relative_path = list_file_recursively(OCR_base_path)
    #     for vid in ocr_relative_path:
    #         path_to_file = os.path.join(OCR_base_path, vid)
    #         vid_name =  vid[:-5]
    #         with open(path_to_file, "r", encoding="utf-8") as f:
    #             data = json.load(f)
    #         database.append((vid_name, data))
    #     return database