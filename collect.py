import requests
from datetime import datetime, timedelta
import pandas as pd
import bar_chart_race as bcr
import matplotlib.pyplot as plt
import matplotlib as mpl

# matplotlibのフォント設定を更新
mpl.rcParams['font.family'] = 'IPAexGothic'

# GitHubの個人アクセストークンを設定
github_token = 'your access token'

# リポジトリとチーム名のマッピング
repositories = {
    "リポジトリのURL":"横軸の名前"
}

# リポジトリが複数あってそれを統合させる場合
repositories_xxx = {
    "リポジトリのURL":"横軸の名前"
}

repositories_yyy = {
    "リポジトリのURL":"横軸の名前"
}

# コミット数を取得する関数
def get_commit_count(repo_url, current_date, github_token):
    owner, repo_name = repo_url.split("/")[-2:]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?since={current_date.isoformat()}&until={(current_date + timedelta(hours=1)).isoformat()}"
    headers = {'Authorization': f'token {github_token}'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        commits = response.json()
        return len(commits)
    except requests.RequestException as e:
        print(f"Error fetching data for {repo_url}: {e}")
        return 0

# データ収集のループ
data = []
end_date = datetime.now()
# データ収集を始める日
current_date = datetime(2024, 3, 16, 0, 0, 0)

while current_date <= end_date:
    row = {"Date": current_date}
    for repo_url, team_name in {**repositories, **repositories_xxx, **repositories_yyy}.items():
        commit_count = get_commit_count(repo_url, current_date, github_token)
        row[team_name] = row.get(team_name, 0) + commit_count

    # xxxとyyyの合計を計算
    row['xxx'] = sum(row.get(team_name, 0) for team_name in repositories_xxx.values())
    row['yyy'] = sum(row.get(team_name, 0) for team_name in repositories_yyy.values())

    data.append(row)
    current_date += timedelta(hours=1)

# データフレームの作成
df = pd.DataFrame(data)
df = df.set_index("Date")

# 各チーム名のリスト
all_teams = list(repositories.values()) + ["xxx", "yyy"]

# 使わないチームの列を削除
df = df[all_teams]

# 累積和の計算
df = df.cumsum()

# 動画を生成
bcr.bar_chart_race(
    df=df,
    filename="cumulative_commit_history.mp4",
    orientation="h",
    sort="desc",
    n_bars=6,  # グラフの本数、集計させるリポジトリの数によって変化させる
    fixed_order=False,
    fixed_max=True,
    steps_per_period=10,
    period_length=500,
    interpolate_period=False,
    period_label={"x": .99, "y": .25, "ha": "right", "va": "center"},
    period_summary_func=lambda v, r: {"x": .99, "y": .18, "s": f"Total: {v.nlargest(6).sum():,.0f}", "ha": "right", "size": 11},
    perpendicular_bar_func="median",
    figsize=(8, 5),  # プロットのサイズを増やす
    cmap="dark12",
    title="Hackit Challenge 2024", # グラフタイトル
    scale="linear"
)
