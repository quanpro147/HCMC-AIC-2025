from elasticsearch import Elasticsearch
import json

# Kết nối tới Elasticsearch (giống như trong file helpers.py)
client = Elasticsearch("http://localhost:9200")

def print_results(response):
    """Hàm tiện ích để in kết quả tìm kiếm cho đẹp."""
    print(f"Tìm thấy tổng cộng: {response['hits']['total']['value']} kết quả.")
    if not response['hits']['hits']:
        print("Không có kết quả nào phù hợp.")
        return

    for hit in response['hits']['hits']:
        score = hit['_score']
        source = hit['_source']
        vid_name = source['vid_name']
        keyframe_id = source['keyframe_id']
        text = source['text']
        
        print("-" * 50)
        print(f"Score: {score:.2f}")
        print(f"Video: {vid_name}")
        print(f"Keyframe ID: {keyframe_id}")
        # In một đoạn trích ngắn của văn bản
        print(f"Text Snippet: {text[:200]}...")

if __name__ == "__main__":
    print("\n--- [TEST 1: TÌM KIẾM ĐƠN GIẢN VỚI TỪ 'công nghệ'] ---")
    query_text_1 = "công nghệ"
    
    query_body_1 = {
        "query": {
            "match": {
                "text": query_text_1
            }
        }
    }
    
    response_1 = client.search(index="ocr", body=query_body_1)
    print_results(response_1)