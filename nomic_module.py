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

def create_nomic_dataset(token, domain, map_url, n,f,m):
    """Nomic Atlasからデータセットを取得し、マスターデータを生成"""
    try:
        nomic.login(token=token, domain=domain)
        map_id = extract_map_name(map_url)
        dataset = AtlasDataset(map_id)

        df_meta, df_topics, df_data = get_map_data(dataset.maps[0])
        df_master = prepare_master_dataframe(df_meta, df_topics, df_data,n,f,m)
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


def add_average_scores(df_master, df_topics, df_data,n,f,m):
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
            df_sub[n] +
            df_sub[f] +
            df_sub[m]
        )
        df_master.at[idx, "平均スコア"] = round(total_score.mean(), 2)
        df_master.at[idx, "新規性平均スコア"] = round(df_sub[n].mean(), 2)
        df_master.at[idx, "市場性平均スコア"] = round(df_sub[m].mean(), 2)
        df_master.at[idx, "実現性平均スコア"] = round(df_sub[f].mean(), 2)
    return df_master


def add_excellent_ideas(df_master, df_topics, df_data,n,f,m):
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
            df_sub[n] +
            df_sub[f] +
            df_sub[m]
        )
        excellent_count = (total_score >= 12).sum()
        df_master.at[idx, "優秀アイデア数(12点以上)"] = excellent_count

        idea_count = row["アイデア数"]
        ratio = (excellent_count / idea_count * 100) if idea_count > 0 else 0
        df_master.at[idx, "優秀アイデアの比率(12点以上)"] = f"{round(ratio, 1)}%"
    return df_master


def add_detailed_scores(df_master, df_topics, df_data, n, f, m):
    """スコア別(4点以上)の平均・件数・比率を追加（列名ゆらぎ対応版）"""

    # UIの列見出しは従来のまま（左が出力のラベル、右が実データの列名）
    score_map = {
        "novelty_score":       {"label": "新規性",     "col": n},
        "marketability_score": {"label": "市場性",     "col": m},
        "feasibility_score":   {"label": "実現可能性", "col": f},
    }

    for key, meta in score_map.items():
        label = meta["label"]
        col   = meta["col"]  # ←実データ側で使う列名（n/f/mのいずれか）

        mean_col  = f"{key}({label})\n平均スコア"
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
            if df_sub.empty or col not in df_sub.columns:
                continue

            s = pd.to_numeric(df_sub[col], errors="coerce").fillna(0.0)
            df_master.at[idx, mean_col] = round(s.mean(), 2)
            excellent_count = (s >= 4).sum()
            ratio = (excellent_count / len(s) * 100) if len(s) > 0 else 0
            df_master.at[idx, count_col] = int(excellent_count)
            df_master.at[idx, ratio_col] = f"{round(ratio, 1)}%"
    return df_master

def _first_existing_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

def add_best_ideas(df_master, df_topics, df_data, n, f, m):
    # ---- 合計スコア（型安全）
    df_data["total_score"] = (
        pd.to_numeric(df_data.get(n, 0), errors="coerce").fillna(0.0) +
        pd.to_numeric(df_data.get(f, 0), errors="coerce").fillna(0.0) +
        pd.to_numeric(df_data.get(m, 0), errors="coerce").fillna(0.0)
    )

    # ---- 文字列系列の候補（必要なら増やしてOK）
    title_candidates   = ["title", "タイトル", "idea_title", "name", "document_title", "node_title"]
    summary_candidates = ["summary", "要約", "概要", "説明"]
    category_candidates= ["category", "カテゴリー", "アイデアカテゴリー"]

    title_col    = _first_existing_col(df_data, title_candidates)
    summary_col  = _first_existing_col(df_data, summary_candidates)
    category_col = _first_existing_col(df_data, category_candidates)

    # ---- 出力列の型を最初から正しい型で初期化（FutureWarning回避）
    for col in ["アイデア名", "Summary", "カテゴリー"]:
        df_master[col] = ""
    for col in ["合計スコア", "新規性スコア", "市場性スコア", "実現性スコア"]:
        df_master[col] = 0.0

    # ---- 以降は通常処理
    for idx, row in df_master.iterrows():
        if row["depth"] == "1":
            mask = (df_topics["topic_depth_1"] == row["Nomic Topic: Broad"])
        elif row["depth"] == "2":
            mask = (df_topics["topic_depth_2"] == row["Nomic Topic: Medium"])
        else:
            continue

        rows = df_topics.loc[mask, "row_number"]
        df_sub = df_data[df_data["row_number"].isin(rows)]
        if df_sub.empty:
            continue

        best = df_sub.sort_values(by="total_score", ascending=False).iloc[0]

        # 見つかった列だけ使う（無ければ空文字）
        df_master.at[idx, "アイデア名"] = str(best[title_col]) if title_col else ""
        df_master.at[idx, "Summary"]   = str(best[summary_col]) if summary_col else ""
        df_master.at[idx, "カテゴリー"] = str(best[category_col]) if category_col else ""

        df_master.at[idx, "合計スコア"]   = float(best.get("total_score", 0.0))
        df_master.at[idx, "新規性スコア"] = float(pd.to_numeric(best.get(n, 0), errors="coerce") or 0.0)
        df_master.at[idx, "市場性スコア"] = float(pd.to_numeric(best.get(m, 0), errors="coerce") or 0.0)
        df_master.at[idx, "実現性スコア"] = float(pd.to_numeric(best.get(f, 0), errors="coerce") or 0.0)
    return df_master



# ==============================
# 🔹 メイン統合処理
# ==============================

def prepare_master_dataframe(df_meta, df_topics, df_data,n,f,m):
    """一連の処理をまとめて実行"""
    df_master = create_master_dataframe(df_meta)
    df_master = add_item_count(df_master, df_topics)
    df_master = add_average_scores(df_master, df_topics, df_data,n,f,m)
    df_master = add_excellent_ideas(df_master, df_topics, df_data,n,f,m)
    df_master = add_detailed_scores(df_master, df_topics, df_data, n, f, m)
    df_master = add_best_ideas(df_master, df_topics, df_data,n,f,m)
    return df_master
