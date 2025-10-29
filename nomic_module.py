import nomic
from nomic import AtlasDataset
import pandas as pd
import re


# ==============================
# 🔹 Nomic 基本ユーティリティ
# ==============================

def extract_map_name(url_or_name: str) -> str:
    """URLまたはmap名からmap_name部分を取り出す"""
    if not url_or_name:
        return ""
    match = re.search(r"/data/[^/]+/([^/]+)(?:/map)?$", url_or_name)
    if match:
        return match.group(1)
    return url_or_name


def get_data(token, domain, map_url):
    try:
        nomic.login(token=token, domain=domain)
        map_id = extract_map_name(map_url)
        dataset = AtlasDataset(map_id)

        df_meta, df_topics, df_data = get_map_data(dataset.maps[0])
        return df_meta, df_topics, df_data, None
    except Exception as e:
        return None,None,None, str(e)

def create_nomic_dataset(token, domain, map_url):
    """Nomic Atlasからデータセットを取得し、マスターデータを生成"""
    try:
        nomic.login(token=token, domain=domain)
        map_id = extract_map_name(map_url)
        dataset = AtlasDataset(map_id)

        df_meta, df_topics, df_data = get_map_data(dataset.maps[0])
        df_master = prepare_master_dataframe(df_meta, df_topics, df_data)
        return df_master, None
    except Exception as e:
        return None, str(e)


def get_map_data(map_data):
    """map_dataからtopicsとmetadataをDataFrameとして取り出す"""
    df_metadata = map_data.topics.metadata
    df_topics = map_data.topics.df
    df_data = map_data.data.df
    return df_metadata, df_topics, df_data


# ==============================
# 🔹 マスターデータ生成関数群
# ==============================

def create_master_dataframe(df_metadata):
    """metadataからマスターデータの基本構造を作成"""
    df_master = pd.DataFrame({
        "depth": df_metadata["depth"].astype(str),
        "topic_id": df_metadata["topic_id"].astype(str),
        "Nomic Topic: Broad": df_metadata["topic_depth_1"].astype(str),
        "Nomic Topic: Medium": df_metadata["topic_depth_2"].astype(str),
        "キーワード": df_metadata["topic_description"].astype(str),
    })
    return df_master


def add_item_count(df_master, df_topics):
    """各トピックのアイデア数をカウントしてdf_masterに追加"""
    df_master["アイデア数"] = 0
    for idx, row in df_master.iterrows():
        if row["depth"] == "1":
            count = (df_topics["topic_depth_1"] == row["Nomic Topic: Broad"]).sum()
        elif row["depth"] == "2":
            count = (df_topics["topic_depth_2"] == row["Nomic Topic: Medium"]).sum()
        else:
            count = 0
        df_master.at[idx, "アイデア数"] = count
    return df_master


def add_average_scores(df_master, df_topics, df_data):
    """各トピックの平均スコア計算"""
    df_master["平均スコア"] = 0.0
    df_master["新規性平均スコア"] = 0.0
    df_master["市場性平均スコア"] = 0.0
    df_master["実現性平均スコア"] = 0.0

    for idx, row in df_master.iterrows():
        depth = row["depth"]
        if depth == "1":
            mask = df_topics["topic_depth_1"] == row["Nomic Topic: Broad"]
        elif depth == "2":
            mask = df_topics["topic_depth_2"] == row["Nomic Topic: Medium"]
        else:
            continue

        rows = df_topics.loc[mask, "row_number"]
        df_sub = df_data[df_data["row_number"].isin(rows)]
        if df_sub.empty:
            continue

        total_score = (
            df_sub["novelty_score"] +
            df_sub["feasibility_score"] +
            df_sub["marketability_score"]
        )
        df_master.at[idx, "平均スコア"] = round(total_score.mean(), 2)
        df_master.at[idx, "新規性平均スコア"] = round(df_sub["novelty_score"].mean(), 2)
        df_master.at[idx, "市場性平均スコア"] = round(df_sub["marketability_score"].mean(), 2)
        df_master.at[idx, "実現性平均スコア"] = round(df_sub["feasibility_score"].mean(), 2)
    return df_master


def add_excellent_ideas(df_master, df_topics, df_data):
    """優秀アイデア(12点以上)の件数と比率を追加"""
    df_master["優秀アイデア数(12点以上)"] = 0
    df_master["優秀アイデアの比率(12点以上)"] = "0%"
    for idx, row in df_master.iterrows():
        if row["depth"] == "1":
            mask = df_topics["topic_depth_1"] == row["Nomic Topic: Broad"]
        elif row["depth"] == "2":
            mask = df_topics["topic_depth_2"] == row["Nomic Topic: Medium"]
        else:
            continue

        df_sub = df_data[df_data["row_number"].isin(df_topics.loc[mask, "row_number"])]
        if df_sub.empty:
            continue

        total_score = (
            df_sub["novelty_score"] +
            df_sub["feasibility_score"] +
            df_sub["marketability_score"]
        )
        excellent_count = (total_score >= 12).sum()
        df_master.at[idx, "優秀アイデア数(12点以上)"] = excellent_count

        idea_count = row["アイデア数"]
        ratio = (excellent_count / idea_count * 100) if idea_count > 0 else 0
        df_master.at[idx, "優秀アイデアの比率(12点以上)"] = f"{round(ratio, 1)}%"
    return df_master


def add_detailed_scores(df_master, df_topics, df_data):
    """スコア別(4点以上)の平均・件数・比率を追加"""
    score_types = {
        "novelty_score": "新規性",
        "marketability_score": "市場性",
        "feasibility_score": "実現可能性"
    }

    for key, label in score_types.items():
        mean_col = f"{key}({label})\n平均スコア"
        count_col = f"{key}({label})\n優秀アイデア数(4点以上)"
        ratio_col = f"{key}({label})\n優秀アイデア比率(4点以上)"

        df_master[mean_col] = 0.0
        df_master[count_col] = 0
        df_master[ratio_col] = "0%"

        for idx, row in df_master.iterrows():
            if row["depth"] == "1":
                mask = df_topics["topic_depth_1"] == row["Nomic Topic: Broad"]
            elif row["depth"] == "2":
                mask = df_topics["topic_depth_2"] == row["Nomic Topic: Medium"]
            else:
                continue

            df_sub = df_data[df_data["row_number"].isin(df_topics.loc[mask, "row_number"])]
            if df_sub.empty:
                continue

            mean_score = df_sub[key].mean()
            df_master.at[idx, mean_col] = round(mean_score, 2)
            excellent_count = (df_sub[key] >= 4).sum()
            ratio = (excellent_count / len(df_sub) * 100) if len(df_sub) > 0 else 0
            df_master.at[idx, count_col] = int(excellent_count)
            df_master.at[idx, ratio_col] = f"{round(ratio, 1)}%"
    return df_master


def add_best_ideas(df_master, df_topics, df_data):
    """トピックごとの最優秀アイデアを抽出"""
    df_data["total_score"] = (
        df_data["novelty_score"] +
        df_data["feasibility_score"] +
        df_data["marketability_score"]
    )

    for col in ["アイデア名","Summary","カテゴリー","合計スコア","新規性スコア","市場性スコア","実現性スコア"]:
        df_master[col] = "" if col in ["アイデア名","Summary","カテゴリー"] else 0

    for idx, row in df_master.iterrows():
        if row["depth"] == "1":
            mask = df_topics["topic_depth_1"] == row["Nomic Topic: Broad"]
        elif row["depth"] == "2":
            mask = df_topics["topic_depth_2"] == row["Nomic Topic: Medium"]
        else:
            continue

        df_sub = df_data[df_data["row_number"].isin(df_topics.loc[mask, "row_number"])]
        if df_sub.empty:
            continue

        best = df_sub.sort_values(by="total_score", ascending=False).iloc[0]
        df_master.at[idx, "アイデア名"] = best.get("title", "")
        df_master.at[idx, "Summary"] = best.get("summary", "")
        df_master.at[idx, "カテゴリー"] = best.get("category", "")
        df_master.at[idx, "合計スコア"] = best.get("total_score", 0)
        df_master.at[idx, "新規性スコア"] = best.get("novelty_score", 0)
        df_master.at[idx, "市場性スコア"] = best.get("marketability_score", 0)
        df_master.at[idx, "実現性スコア"] = best.get("feasibility_score", 0)
    return df_master


# ==============================
# 🔹 メイン統合処理
# ==============================

def prepare_master_dataframe(df_meta, df_topics, df_data):
    """一連の処理をまとめて実行"""
    df_master = create_master_dataframe(df_meta)
    df_master = add_item_count(df_master, df_topics)
    df_master = add_average_scores(df_master, df_topics, df_data)
    df_master = add_excellent_ideas(df_master, df_topics, df_data)
    df_master = add_detailed_scores(df_master, df_topics, df_data)
    df_master = add_best_ideas(df_master, df_topics, df_data)
    return df_master
