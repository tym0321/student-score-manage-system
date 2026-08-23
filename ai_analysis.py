import pandas as pd


def score_analysis(score_list):
    df = pd.DataFrame(score_list)
    result = {}

    if df.empty:
        return {"提示": "还没有录入任何成绩数据"}

    result["及格率(%)"] = round((df["score"] >= 60).mean() * 100, 2)
    result["挂科学生"] = df[df["score"] < 60].to_dict("records")
    result["平均分"] = round(df["score"].mean(), 2)

    df["排名"] = df["score"].rank(ascending=False, method="min")
    result["成绩排名"] = df.to_dict("records")

    return result