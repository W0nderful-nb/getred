# main.py
from flask import Flask, request, jsonify
from loguru import logger
from apis.xhs_pc_apis import XHS_Apis
from xhs_utils.data_util import handle_note_info

app = Flask(__name__)
xhs_api = XHS_Apis()

@app.route("/search", methods=["POST"])
def search_notes():
    try:
        data = request.get_json()
        query = data.get("query")
        cookies_str = data.get("cookies")

        if not query or not cookies_str:
            return jsonify({"code": 400, "message": "参数 query 和 cookies 不能为空"}), 400

        # 调用搜索 API 获取前十条笔记
        success, msg, notes = xhs_api.search_some_note(
            query=query,
            require_num=10,
            cookies=cookies_str,
            sort_type=0,
            note_type=0,
            note_time=0,
            note_range=0,
            pos_distance=0,
            geo=None,
            proxies=None
        )

        if not success:
            return jsonify({"code": 500, "message": str(msg)}), 500

        result = []
        for note in notes:
            if note.get("model_type") != "note":
                continue
            note_url = f"https://www.xiaohongshu.com/explore/{note['id']}?xsec_token={note['xsec_token']}"
            success, msg, note_info = xhs_api.get_note_info(note_url, cookies_str)
            if success and note_info:
                raw_note = note_info['data']['items'][0]
                raw_note['url'] = note_url
                cleaned = handle_note_info(raw_note)
                result.append({
                    "title": cleaned.get("title", ""),
                    "desc": cleaned.get("desc", ""),
                    "url": note_url,
                    "media": cleaned.get("media", [])
                })

        return jsonify({"code": 200, "message": "成功", "data": result})

    except Exception as e:
        logger.exception("搜索接口异常")
        return jsonify({"code": 500, "message": str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8000))  # Railway 自动注入 PORT
    app.run(host="0.0.0.0", port=port)

