import pandas as pd 
import os 
import sys 
from sklearn.metrics import accuracy_score,f1_score, root_mean_squared_error

root_path = os.path.dirname(os.path.abspath(__file__))
print(root_path)

game_1_path = os.path.join(root_path,"dataset","test_with_label_1.xlsx")
game_2_path = os.path.join(root_path,"dataset","test_with_label_2.xlsx")

df_game_1 = pd.read_excel(game_1_path)
df_game_2 = pd.read_excel(game_2_path) 
game_1_id_list = df_game_1["id"].to_list()
game_1_label_list = [int(item) for item in df_game_1["label"].to_list()]

game_2_id_list = df_game_2["id"].to_list()
game_2_label_list = [int(item) for item in df_game_2["rating"].to_list()]

save_dir = os.path.join(root_path,"temp")

def cal_game_1_score(test_path):
    df = pd.read_excel(test_path)
    id_list = df["id"].to_list()
    pred_list = df["label"].to_list()
    pred_dict = dict()
    for _id , pred in zip(id_list, pred_list):
        pred_dict[_id] = int(pred)
    full_pred = []
    for ind, _id  in enumerate(game_1_id_list):
        tmp_pred = pred_dict.get(_id, 1-game_1_label_list[ind])
        full_pred.append(tmp_pred)
    f1 = f1_score(game_1_label_list, full_pred)
    return f1*100

def cal_game_2_score(test_path):
    df = pd.read_excel(test_path)
    id_list = df["id"].to_list()
    pred_list = df["rating"].to_list()
    pred_dict = dict()
    for _id , pred in zip(id_list, pred_list):
        pred_dict[_id] = float(pred)
    full_pred = []
    for ind, _id  in enumerate(game_2_id_list):
        tmp_pred = pred_dict.get(_id, game_2_label_list[ind]+5)
        full_pred.append(tmp_pred)
    rmse = root_mean_squared_error(game_2_label_list, full_pred, )
    return 100 - min(25*rmse,100)

def get_group_path(groupname):
    group_path = os.path.join(save_dir, groupname)
    return group_path

def makedir_for_group(groupname):
    _path = get_group_path(groupname)
    if not os.path.exists(_path):
        os.makedirs(_path)
        print("make dir {}".format(_path))

def db_get_group(db, groupname):
    # print(groupname)
    group = db.execute(
            'SELECT * FROM usergroup WHERE username = ?', (groupname,)
        ).fetchone()
    if not group:
        db.execute(
        'Insert INTO usergroup (username)'
        ' VALUES (?)',
        (groupname,))
        db.commit()
        group = db.execute(
        'SELECT * FROM usergroup WHERE username = ?', (groupname,)
        ).fetchone()
    return group

def db_save_eval_result(db, group_id, game_tag, score):
    db.execute(
        'Insert INTO gamesubmit (group_id, game_tag, score)'
        ' VALUES (?,?,?)',
        (group_id, game_tag, str(score)))
    db.commit()

def db_fetch_game_rank(db, game_tag):
    all_submit = db.execute(
        'Select * from gamesubmit where game_tag = ?',(game_tag,)
    ).fetchall()
    res_dict = dict()
    for item in all_submit:
        if item["group_id"] in res_dict:
            res_dict[item["group_id"]]["score"] = max(res_dict[item["group_id"]]["score"], float(item["score"]))
        else:
            group = db.execute(
        'Select * from usergroup where  id = ?',(item["group_id"],)
        ).fetchone()
            res_dict[item["group_id"]] = {"name":group["username"],"score":float(item["score"])}
    tmp_list = []
    for k,v in res_dict.items():
        tmp_list.append(v)
    tmp_list = sorted(tmp_list, key=lambda x:x["score"], reverse=True)
    for ind in range(len(tmp_list)):
        tmp_list[ind]["order"] = ind+1 
    return tmp_list


if __name__ == "__main__":

    print(cal_game_1_score(game_1_path))
    print(cal_game_2_score(game_2_path))

