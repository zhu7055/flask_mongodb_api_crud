# 引入 Flask 和 PyMongo 套件
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_httpauth import HTTPBasicAuth
from bson import ObjectId
from bson.errors import InvalidId

# 建立 Flask 應用程式
app = Flask(__name__)

# 設定 MongoDB 連線資訊
# 請務必將 <db_password> 替換為您的實際密碼
app.config["MONGO_URI"] = "mongodb+srv://judy18258_db_user:XYMJwB5OeEc20DEW@flaskapi.52oxtsc.mongodb.net/visitors_db?retryWrites=true&w=majority&appName=FlaskAPI"
mongo = PyMongo(app)

# 建立 HTTPBasicAuth 物件
auth = HTTPBasicAuth()

# 設定帳號密碼驗證機制
@auth.verify_password
def verify_password(username, password):
    # 這是一個簡單的範例，實際應用中應使用更安全的驗證方式
    return username == "admin" and password == "123456"

# 處理訪客列表和新增訪客
@app.route("/visitors", methods=["GET", "POST"])
@auth.login_required
def visitors_collection():
    if request.method == "GET":
        # 取得所有或根據名稱查詢特定的訪客資料
        name = request.args.get("name")
        if name:
            visitor = mongo.db.visitors.find_one({"name": name})
            if visitor is None:
                return jsonify({"status": 404, "message": "Visitor not found"}), 404
            else:
                # 確保 ObjectId 被轉換為字串以便 JSON 化
                visitor['_id'] = str(visitor['_id'])
                return jsonify({"status": 200, "visitor": visitor}), 200
        else:
            # 取得所有訪客
            visitors = mongo.db.visitors.find()
            visitors_list = []
            for visitor in visitors:
                visitor['_id'] = str(visitor['_id'])
                visitors_list.append(visitor)
            return jsonify({"status": 200, "visitors": visitors_list}), 200

    elif request.method == "POST":
        data = request.get_json()
        required_fields = ["name", "age", "gender", "phone", "address"]
        if data and all(key in data for key in required_fields):
            try:
                result = mongo.db.visitors.insert_one(data)
                return jsonify({"status": 201, "id": str(result.inserted_id)}), 201
            except Exception as e:
                return jsonify({"status": 500, "message": f"Server error: {e}"}), 500
        else:
            return jsonify({"status": 400, "message": "Missing or invalid data"}), 400

# 處理特定訪客的查詢、更新和刪除
@app.route("/visitors/<id>", methods=["GET", "PUT", "DELETE"])
@auth.login_required
def visitor_document(id):
    try:
        obj_id = ObjectId(id)
    except InvalidId:
        return jsonify({"status": 400, "message": "Invalid ID format"}), 400

    if request.method == "GET":
        visitor = mongo.db.visitors.find_one({"_id": obj_id})
        if visitor:
            visitor['_id'] = str(visitor['_id'])
            return jsonify({"status": 200, "visitor": visitor}), 200
        else:
            return jsonify({"status": 404, "message": "Visitor not found"}), 404

    elif request.method == "PUT":
        data = request.get_json()
        required_fields = ["name", "age", "gender", "phone", "address"]
        if data and all(key in data for key in required_fields):
            try:
                result = mongo.db.visitors.update_one({"_id": obj_id}, {"$set": data})
                count = result.modified_count
                if count == 0:
                    return jsonify({"status": 404, "message": "Visitor not found or no changes were made"}), 404
                else:
                    return jsonify({"status": 200, "count": count}), 200
            except Exception as e:
                return jsonify({"status": 500, "message": f"Server error: {e}"}), 500
        else:
            return jsonify({"status": 400, "message": "Missing or invalid data"}), 400

    elif request.method == "DELETE":
        result = mongo.db.visitors.delete_one({"_id": obj_id})
        count = result.deleted_count
        if count == 0:
            return jsonify({"status": 404, "message": "Visitor not found"}), 404
        else:
            return jsonify({"status": 200, "count": count}), 200

# 啟動 Flask 應用程式
if __name__ == "__main__":
    # 在本機測試時使用 debug=True 會更方便
    app.run(debug=True)
