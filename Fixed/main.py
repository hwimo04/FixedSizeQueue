import os
from flask import Flask, request, jsonify

app = Flask(__name__)

class FixedQueue:
    def __init__(self, capacity: int = 20):
        self.capacity = capacity
        self.que = [None] * capacity
        self.num = 0       # 현재 데이터 개수
        self.front = 0     # 맨 앞 인덱스
        self.rear = 0      # 맨 끝 다음 인덱스

    def is_empty(self) -> bool:
        return self.num <= 0

    def is_full(self) -> bool:
        return self.num >= self.capacity

    def push(self, value):
        if self.is_full():
            return False, "Queue is Full"
        self.que[self.rear] = value
        self.rear = (self.rear + 1) % self.capacity
        self.num += 1
        return True, "Success"

    def pop(self):
        if self.is_empty():
            return None, "Queue is Empty"
        val = self.que[self.front]
        self.que[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.num -= 1
        return val, "Success"

    def peek(self):
        if self.is_empty():
            return None, "Queue is Empty"
        return self.que[self.front], "Success"

    def clear(self):
        self.num = 0
        self.front = 0
        self.rear = 0
        self.que = [None] * self.capacity

    def to_list(self):
        result = []
        for i in range(self.num):
            idx = (self.front + i) % self.capacity
            result.append(self.que[idx])
        return result

    def find_indices(self, value):
        # Front 기준 논리적 오프셋 인덱스 리스트 반환
        indices = []
        for i in range(self.num):
            idx = (self.front + i) % self.capacity
            if self.que[idx] == value:
                indices.append(i)
        return indices

    def count(self, value):
        return sum(1 for i in range(self.num) if self.que[(self.front + i) % self.capacity] == value)

    def contains(self, value):
        return any(self.que[(self.front + i) % self.capacity] == value for i in range(self.num))

# 전역 큐 인스턴스 (초기 크기 20)
queue = FixedQueue(20)

@app.route("/", methods=["GET", "POST"])
def queue_controller():
    global queue
    data = request.get_json(silent=True) or {}
    action = data.get("action", "dump")

    # 1) 초기화
    if action == "init":
        capacity = int(data.get("capacity", 20))
        queue = FixedQueue(capacity)
        return jsonify({"status": "success", "message": f"Queue initialized with capacity {capacity}", "capacity": capacity})

    # 2) Push / Multi-Push
    elif action == "push":
        values = data.get("values")
        if values is not None and isinstance(values, list):
            results = []
            for v in values:
                ok, msg = queue.push(v)
                results.append({"val": v, "success": ok, "message": msg})
            return jsonify({"status": "success", "results": results, "current_size": queue.num})
        else:
            val = data.get("value")
            ok, msg = queue.push(val)
            return jsonify({"status": "success" if ok else "fail", "message": msg, "current_size": queue.num})

    # 2) Pop
    elif action == "pop":
        val, msg = queue.pop()
        return jsonify({"status": "success" if val is not None else "fail", "value": val, "message": msg, "current_size": queue.num})

    # 3) 현재 데이터 개수 반환
    elif action == "size":
        return jsonify({"status": "success", "size": queue.num, "capacity": queue.capacity})

    # 4) 상태 검사 (full, empty)
    elif action == "status":
        return jsonify({
            "status": "success",
            "is_empty": queue.is_empty(),
            "is_full": queue.is_full(),
            "size": queue.num,
            "capacity": queue.capacity
        })

    # 5) 전면(Front) 데이터 확인
    elif action == "peek":
        val, msg = queue.peek()
        return jsonify({"status": "success" if val is not None else "fail", "front_value": val, "message": msg})

    # 6) 큐 전체 데이터 삭제
    elif action == "clear":
        queue.clear()
        return jsonify({"status": "success", "message": "Queue cleared", "size": queue.num})

    # 7) & 8) 값의 index 검색 및 개수 반환
    elif action == "search":
        val = data.get("value")
        indices = queue.find_indices(val)
        count = queue.count(val)
        return jsonify({"status": "success", "value": val, "indices": indices, "count": count})

    # 9) 값의 존재 여부 검사
    elif action == "contains":
        val = data.get("value")
        exists = queue.contains(val)
        return jsonify({"status": "success", "value": val, "exists": exists})

    # 10) Front부터 Rear까지 출력
    elif action == "dump":
        return jsonify({
            "status": "success",
            "queue": queue.to_list(),
            "size": queue.num,
            "capacity": queue.capacity,
            "is_empty": queue.is_empty(),
            "is_full": queue.is_full()
        })

    return jsonify({"status": "error", "message": "Unknown action"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
