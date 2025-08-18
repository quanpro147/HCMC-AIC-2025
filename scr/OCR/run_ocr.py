import os
import glob
import json
import easyocr
from tqdm import tqdm
from ocr_database import OcrDB

def extract_text_from_keyframes(keyframe_paths: list, lang: list = ['vi', 'en']):
    """
    Sử dụng easyocr để trích xuất văn bản từ một danh sách các ảnh keyframe.
    """
    print(f"Khởi tạo EasyOCR cho ngôn ngữ: {lang}...")
    reader = easyocr.Reader(lang, gpu=True) 
    
    ocr_results = {}
    print(f"Bắt đầu xử lý OCR cho {len(keyframe_paths)} keyframes...")
    
    for image_path in tqdm(keyframe_paths, desc="OCR Processing"):
        try:
            keyframe_id = os.path.basename(image_path)
            text_list = reader.readtext(image_path, detail=0, paragraph=True)
            combined_text = " ".join(text_list)
            ocr_results[keyframe_id] = combined_text
        except Exception as e:
            print(f"Lỗi khi xử lý file {image_path}: {e}")
            ocr_results[os.path.basename(image_path)] = ""

    return ocr_results

def save_ocr_to_json(ocr_data: dict, output_path: str):
    """
    Lưu dữ liệu OCR (dictionary) vào một file JSON.
    """
    print(f"Đang lưu kết quả OCR vào {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ocr_data, f, ensure_ascii=False, indent=4)
    print("Lưu thành công!")


if __name__ == "__main__":
    BASE_KEYFRAMES_DIR = "./keyframes"
    OCR_OUTPUT_DIR = "./texts_extracted"

    try:
        video_folders = [d for d in os.listdir(BASE_KEYFRAMES_DIR) if os.path.isdir(os.path.join(BASE_KEYFRAMES_DIR, d))]
    except FileNotFoundError:
        print(f"LỖI: Thư mục '{BASE_KEYFRAMES_DIR}' không tồn tại. Vui lòng tạo thư mục này.")
        exit() 

    if not video_folders:
        print(f"Không tìm thấy thư mục video con nào trong '{BASE_KEYFRAMES_DIR}'.")
    else:
        print(f"Tìm thấy {len(video_folders)} thư mục video. Bắt đầu xử lý...")
        
        for video_name in video_folders:
            print(f"\n{'='*20} BẮT ĐẦU XỬ LÝ VIDEO: {video_name} {'='*20}")

            current_video_keyframes_dir = os.path.join(BASE_KEYFRAMES_DIR, video_name)
            output_json_path = os.path.join(OCR_OUTPUT_DIR, f"{video_name}.json")

            # MỚI: Kiểm tra xem video này đã được xử lý chưa để tiết kiệm thời gian
            if os.path.exists(output_json_path):
                print(f"File '{output_json_path}' đã tồn tại. Bỏ qua xử lý OCR cho video này.")
                continue # Chuyển sang video tiếp theo

            # Lấy danh sách tất cả các file ảnh keyframe
            keyframe_paths = glob.glob(os.path.join(current_video_keyframes_dir, "*.jpg"))
            if not keyframe_paths:
                print(f"Không tìm thấy keyframe (.jpg) nào trong thư mục: {current_video_keyframes_dir}. Bỏ qua.")
                continue
            
            # Thực hiện OCR
            ocr_data = extract_text_from_keyframes(keyframe_paths, lang=['vi', 'en'])
            
            # Lưu kết quả ra file JSON
            save_ocr_to_json(ocr_data, output_json_path)

    print("\n==========================================================")
    print("Hoàn tất xử lý OCR cho tất cả các video.")
    print("Bắt đầu lập chỉ mục toàn bộ dữ liệu OCR vào Elasticsearch...")
    
    ocr_db = OcrDB(OCR_base_path=OCR_OUTPUT_DIR, remove_old_index=True)
    
    print("\nQuy trình hoàn tất! Dữ liệu đã sẵn sàng để truy vấn.")