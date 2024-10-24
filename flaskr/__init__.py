import os

from flask import Flask, render_template,url_for,request
import json 
from werkzeug.utils import secure_filename
from .utils import (makedir_for_group, 
                    get_group_path, 
                    cal_game_1_score, 
                    cal_game_2_score, 
                    db_get_group,
                    db_save_eval_result,
                    db_fetch_game_rank)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    from . import db
    from .db import get_db
    db.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    # game1_rank_list = [{"order":"1","name":"测试队伍","score":"78"},
    #                    {"order":"2","name":"测试队伍","score":"80"}]
    # game2_rank_list = [{"order":"1","name":"测试队伍","score":"79"}]
    @app.route('/')
    def hello():
        db = get_db()
        game1_rank_list = db_fetch_game_rank(db, "赛题1")
        game2_rank_list = db_fetch_game_rank(db, "赛题2")
        return render_template("index.html",
                               game1_rank_list=game1_rank_list,
                               game2_rank_list = game2_rank_list)
    
    
    def allowed_file(file_name):
        allowed_extention = {"xlsx"}
        return "." in file_name and file_name.split(".")[-1].lower() in allowed_extention

    @app.route('/submitpred', methods=('GET','POST'))
    def submit_pred():
        ret_dict = {"status":"ok",
                "msg":"",
                "data":{}
                }
        
        if request.method == 'POST':
            # data = json.loads(request.data.decode())
            
            group_name = request.form["groupname"]
            game_tag = request.form["gametag"]
            if not group_name or not game_tag:
                ret_dict["status"] = "error"
                ret_dict["msg"] = "用户名或赛道未选择！"
                return json.dumps(ret_dict)
            db = get_db()
            # print(group_name)
            db_group = db_get_group(db, groupname=group_name)
            # print(db_group["id"])
            group_path = get_group_path(group_name)
            makedir_for_group(group_name)
            if 'file' not in request.files:
                ret_dict["status"] = "error"
                ret_dict["msg"] = "未上传文件！"
                return json.dumps(ret_dict)
            _file = request.files["file"]
            if _file.filename == "":
                ret_dict["status"] = "error"
                ret_dict["msg"] = "未上传文件！"
                return json.dumps(ret_dict)
            if _file and allowed_file(_file.filename):
                filename = secure_filename(_file.filename)
                saved_file_path = os.path.join(group_path, filename)
                _file.save(saved_file_path)
                if game_tag.replace(" ","") == "赛题1":
                    score = cal_game_1_score(saved_file_path)
                else:
                    score = cal_game_2_score(saved_file_path)
                
                ret_dict["data"] = {"score":score}
                db_save_eval_result(db, db_group["id"],game_tag, score)
                return json.dumps(ret_dict)
            ret_dict["status"] = "error"
            ret_dict["msg"] = "存在未知错误！"
            return json.dumps(ret_dict)

    return app