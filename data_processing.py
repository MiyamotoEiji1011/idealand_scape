import pandas as pd

def prepare_master_dataframe(map_data):
    """Nomicデータを整形してマスターデータを作成"""
    df_metadata = map_data.topics.metadata
    df_topics = map_data.topics.df
    df_data = map_data.data.df

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
    
    # --- 優秀アイデア数と比率カウント ---
    df_master["平均スコア"] = 0.0
    for idx, row in df_master.iterrows():
        depth = row["depth"]

        if depth == "1":
            topic_name = row["Nomic Topic: Broad"]
            rows = df_topics[df_topics["topic_depth_1"] == topic_name]["row_number"]
        elif depth == "2":
            topic_name = row["Nomic Topic: Medium"]
            rows = df_topics[df_topics["topic_depth_2"] == topic_name]["row_number"]
        else:
            rows = pd.Series(dtype=int)

        if not rows.empty:
            df_sub = df_data[df_data["row_number"].isin(rows)]

            total_score = (
                df_sub["novelty_score"] +
                df_sub["feasibility_score"] +
                df_sub["marketability_score"]
            )
            avg_score = total_score.mean()

            df_master.at[idx, "平均スコア"] = round(avg_score, 2)
        else:
            df_master.at[idx, "平均スコア"] = 0
    
    #--- 各スコアの平均値計算 ---
    df_master["新規性平均スコア"] = 0.0
    for idx, row in df_master.iterrows():
        depth = row["depth"]

        if depth == "1":
            topic_name = row["Nomic Topic: Broad"]
            rows = df_topics[df_topics["topic_depth_1"] == topic_name]["row_number"]
        elif depth == "2":
            topic_name = row["Nomic Topic: Medium"]
            rows = df_topics[df_topics["topic_depth_2"] == topic_name]["row_number"]
        else:
            rows = pd.Series(dtype=int)

        if not rows.empty:
            df_sub = df_data[df_data["row_number"].isin(rows)]
            avg_score = df_sub["novelty_score"].mean()
            df_master.at[idx, "新規性平均スコア"] = round(avg_score, 2)
        else:
            df_master.at[idx, "新規性平均スコア"] = 0.0

    df_master["市場性平均スコア"] = 0.0
    for idx, row in df_master.iterrows():
        depth = row["depth"]

        if depth == "1":
            topic_name = row["Nomic Topic: Broad"]
            rows = df_topics[df_topics["topic_depth_1"] == topic_name]["row_number"]
        elif depth == "2":
            topic_name = row["Nomic Topic: Medium"]
            rows = df_topics[df_topics["topic_depth_2"] == topic_name]["row_number"]
        else:
            rows = pd.Series(dtype=int)

        if not rows.empty:
            df_sub = df_data[df_data["row_number"].isin(rows)]
            avg_score = df_sub["marketability_score"].mean()
            df_master.at[idx, "市場性平均スコア"] = round(avg_score, 2)
        else:
            df_master.at[idx, "市場性平均スコア"] = 0.0

    df_master["実現性平均スコア"] = 0.0
    for idx, row in df_master.iterrows():
        depth = row["depth"]

        if depth == "1":
            topic_name = row["Nomic Topic: Broad"]
            rows = df_topics[df_topics["topic_depth_1"] == topic_name]["row_number"]
        elif depth == "2":
            topic_name = row["Nomic Topic: Medium"]
            rows = df_topics[df_topics["topic_depth_2"] == topic_name]["row_number"]
        else:
            rows = pd.Series(dtype=int)

        if not rows.empty:
            df_sub = df_data[df_data["row_number"].isin(rows)]
            avg_score = df_sub["feasibility_score"].mean()
            df_master.at[idx, "実現性平均スコア"] = round(avg_score, 2)
        else:
            df_master.at[idx, "実現性平均スコア"] = 0.0

    #--- 優秀アイデア数(12点以上)カウント ---
    df_master["優秀アイデア数(12点以上)"] = 0
    for idx, row in df_master.iterrows():
        depth = row["depth"]

        if depth == "1":
            topic_name = row["Nomic Topic: Broad"]
            rows = df_topics[df_topics["topic_depth_1"] == topic_name]["row_number"]
        elif depth == "2":
            topic_name = row["Nomic Topic: Medium"]
            rows = df_topics[df_topics["topic_depth_2"] == topic_name]["row_number"]
        else:
            rows = pd.Series(dtype=int)

        if not rows.empty:
            df_sub = df_data[df_data["row_number"].isin(rows)]
            total_score = (
                df_sub["novelty_score"] +
                df_sub["feasibility_score"] +
                df_sub["marketability_score"]
            )
            count_over12 = (total_score >= 12).sum()
            df_master.at[idx, "優秀アイデア数(12点以上)"] = count_over12
        else:
            df_master.at[idx, "優秀アイデア数(12点以上)"] = 0

    #--- 優秀アイデア比率計算 ---
    df_master["優秀アイデアの比率(12点以上)"] = 0.0
    for idx, row in df_master.iterrows():
        idea_count = row["アイデア数"]
        excellent_count = row["優秀アイデア数(12点以上)"]

        if idea_count > 0:
            ratio = (excellent_count / idea_count) * 100
        else:
            ratio = 0.0

        df_master.at[idx, "優秀アイデアの比率(12点以上)"] = f"{round(ratio, 1)}%"


    #--- 新規性、実現可能性、市場性の各スコア詳細計算 ---
    df_master["novelty_score(新規性)平均スコア"] = 0.0
    df_master["novelty_score(新規性)優秀アイデア数(4点以上)"] = 0
    df_master["novelty_score(新規性)優秀アイデア比率(4点以上)"] = "0%"

    for idx, row in df_master.iterrows():
        depth = row["depth"]

        # 1: Broad, 2: Medium
        if depth == "1":
            mask = df_topics["topic_depth_1"] == row["Nomic Topic: Broad"]
        elif depth == "2":
            mask = df_topics["topic_depth_2"] == row["Nomic Topic: Medium"]
        else:
            mask = pd.Series([False]*len(df_topics))

        row_numbers = df_topics.loc[mask, "row_number"]

        df_sub = df_data[df_data["row_number"].isin(row_numbers)]

        if not df_sub.empty:
            mean_score = df_sub["novelty_score"].mean()
            df_master.at[idx, "novelty_score(新規性)平均スコア"] = round(mean_score, 2)

            excellent_count = (df_sub["novelty_score"] >= 4).sum()
            df_master.at[idx, "novelty_score(新規性)優秀アイデア数(4点以上)"] = int(excellent_count)

            total_count = len(df_sub)
            ratio = (excellent_count / total_count) * 100 if total_count > 0 else 0
            df_master.at[idx, "novelty_score(新規性)優秀アイデア比率(4点以上)"] = f"{round(ratio, 1)}%"


    df_master["marketability_score(市場性)平均スコア"] = 0.0
    df_master["marketability_score(市場性)優秀アイデア数(4点以上)"] = 0
    df_master["marketability_score(市場性)優秀アイデア比率(4点以上)"] = "0%"

    for idx, row in df_master.iterrows():
        depth = row["depth"]

        if depth == "1":
            mask = df_topics["topic_depth_1"] == row["Nomic Topic: Broad"]
        elif depth == "2":
            mask = df_topics["topic_depth_2"] == row["Nomic Topic: Medium"]
        else:
            mask = pd.Series([False]*len(df_topics))

        row_numbers = df_topics.loc[mask, "row_number"]
        df_sub = df_data[df_data["row_number"].isin(row_numbers)]

        if not df_sub.empty:
            mean_score = df_sub["marketability_score"].mean()
            df_master.at[idx, "marketability_score(市場性)平均スコア"] = round(mean_score, 2)

            excellent_count = (df_sub["marketability_score"] >= 4).sum()
            df_master.at[idx, "marketability_score(市場性)優秀アイデア数(4点以上)"] = int(excellent_count)

            total_count = len(df_sub)
            ratio = (excellent_count / total_count) * 100 if total_count > 0 else 0
            df_master.at[idx, "marketability_score(市場性)優秀アイデア比率(4点以上)"] = f"{round(ratio, 1)}%"


    df_master["feasibility_score(実現可能性)平均スコア"] = 0.0
    df_master["feasibility_score(実現可能性)優秀アイデア数(4点以上)"] = 0
    df_master["feasibility_score(実現可能性)優秀アイデア比率(4点以上)"] = "0%"

    for idx, row in df_master.iterrows():
        depth = row["depth"]

        if depth == "1":
            mask = df_topics["topic_depth_1"] == row["Nomic Topic: Broad"]
        elif depth == "2":
            mask = df_topics["topic_depth_2"] == row["Nomic Topic: Medium"]
        else:
            mask = pd.Series([False]*len(df_topics))

        row_numbers = df_topics.loc[mask, "row_number"]
        df_sub = df_data[df_data["row_number"].isin(row_numbers)]

        if not df_sub.empty:
            mean_score = df_sub["feasibility_score"].mean()
            df_master.at[idx, "feasibility_score(実現可能性)平均スコア"] = round(mean_score, 2)

            excellent_count = (df_sub["feasibility_score"] >= 4).sum()
            df_master.at[idx, "feasibility_score(実現可能性)優秀アイデア数(4点以上)"] = int(excellent_count)

            total_count = len(df_sub)
            ratio = (excellent_count / total_count) * 100 if total_count > 0 else 0
            df_master.at[idx, "feasibility_score(実現可能性)優秀アイデア比率(4点以上)"] = f"{round(ratio, 1)}%"


    # --- 合計スコア計算列追加 ---
    df_data["total_score"] = df_data["novelty_score"] + df_data["feasibility_score"] + df_data["marketability_score"]

    # --- 最優秀アイデア抽出 ---
    for col in ["アイデア名","Summary","カテゴリー","合計スコア","新規性スコア","市場性スコア","実現性スコア"]:
        df_master[col] = "" if col in ["アイデア名","Summary","カテゴリー"] else 0

    for idx, row in df_master.iterrows():
        depth = row["depth"]

        if depth == "1":
            mask = df_topics["topic_depth_1"] == row["Nomic Topic: Broad"]
        elif depth == "2":
            mask = df_topics["topic_depth_2"] == row["Nomic Topic: Medium"]
        else:
            mask = pd.Series([False]*len(df_topics))

        row_numbers = df_topics.loc[mask, "row_number"]
        df_sub = df_data[df_data["row_number"].isin(row_numbers)]

        if not df_sub.empty:
            best = df_sub.sort_values(by="total_score", ascending=False).iloc[0]

            df_master.at[idx, "アイデア名"] = best.get("title", "")
            df_master.at[idx, "Summary"] = best.get("summary", "")
            df_master.at[idx, "カテゴリー"] = best.get("category", "")
            df_master.at[idx, "合計スコア"] = best.get("total_score", 0)
            df_master.at[idx, "新規性スコア"] = best.get("novelty_score", 0)
            df_master.at[idx, "市場性スコア"] = best.get("marketability_score", 0)
            df_master.at[idx, "実現性スコア"] = best.get("feasibility_score", 0)

    return df_master
