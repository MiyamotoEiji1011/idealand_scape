import pandas as pd

def prepare_master_dataframe(map_data):
    """Nomicデータを整形してマスターデータを作成"""
    df_metadata = map_data.topics.metadata
    df_topics = map_data.topics.df

    columns = [
        "depth", "topic_id", "Nomic Topic: Broad", "Nomic Topic: Medium", "キーワード",
        "アイデア数", "平均スコア", "新規性平均スコア", "市場性平均スコア", "実現性平均スコア",
        "優秀アイデア数(12点以上)", "優秀アイデアの比率(12点以上)",
        "novelty_score(新規性)平均スコア", "novelty_score(新規性)優秀アイデア数(4点以上)",
        "novelty_score(新規性)優秀アイデア比率(4点以上)",
        "feasibility_score(実現可能性)平均スコア", "feasibility_score(実現可能性)優秀アイデア数(4点以上)",
        "feasibility_score(実現可能性)優秀アイデア比率(4点以上)",
        "marketability_score(市場性)平均スコア", "marketability_score(市場性)優秀アイデア数(4点以上)",
        "marketability_score(市場性)優秀アイデア比率(4点以上)",
        "アイデア名", "Summary", "カテゴリー", "合計スコア", "新規性スコア", "市場性スコア", "実現性スコア"
    ]

    df_master = pd.DataFrame(columns=columns)
    df_master["depth"] = df_metadata["depth"].astype(str)
    df_master["topic_id"] = df_metadata["topic_id"].astype(str)
    df_master["Nomic Topic: Broad"] = df_metadata["topic_depth_1"].astype(str)
    df_master["Nomic Topic: Medium"] = df_metadata["topic_depth_2"].astype(str)
    df_master["キーワード"] = df_metadata["topic_description"].astype(str)

    # --- アイデア数カウント ---
    df_master["アイデア数"] = 0
    for idx, row in df_master.iterrows():
        depth = row["depth"]
        topic_depth_1 = row["Nomic Topic: Broad"]
        topic_depth_2 = row["Nomic Topic: Medium"]

        if depth == "1":
            count = (df_topics["topic_depth_1"] == topic_depth_1).sum()
        elif depth == "2":
            count = (df_topics["topic_depth_2"] == topic_depth_2).sum()
        else:
            count = 0

        df_master.at[idx, "アイデア数"] = count

    return df_master
