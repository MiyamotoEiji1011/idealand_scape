import pandas as pd

def create_master_dataframe():
    """Google Sheets初期化用の空DataFrame"""
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
    return pd.DataFrame(columns=columns)
