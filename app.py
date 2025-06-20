import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import re

st.set_page_config(page_title="图形化编程作品分析", layout="wide")
st.title("📊 图形化编程作品使用时长分析（分类中位数正确计算示范）")

file_path = os.path.join("data", "usage_data.xlsx")

hardware_projects = [
    "射箭比赛", "布袋球", "百米短跑", "划艇比赛", "滑板比赛", "掰手腕",
    "投篮大师", "谁是大力士", "新乒乓球大战", "跳绳抛射", "耐力跳跃", "乒乓球大战",
    "打水漂", "飞盘射击", "toio 保龄球", "太鼓小火车", "魔法烟花秀", "魔杖泡泡龙",
    "合成大西瓜", "投篮挑战"
]

def extract_main_project_name(name):
    if not isinstance(name, str):
        return name
    name = re.sub(r"\(.*?\)|（.*?）", "", name)
    name = name.replace('_', ' ').replace('·', ' ').replace('-', ' ')
    name = re.sub(
        r"(入门版|普通版|挑战版|入门级|普通级|挑战级|困难级|地狱级|"
        r"一年级上|一年级下|二年级上|二年级下|三年级上|三年级下|"
        r"四年级上|四年级下|五年级上|五年级下|六年级上|六年级下)",
        "",
        name
    )
    matches = re.findall(r"[\u4e00-\u9fa5]{2,}", name)
    if matches:
        name = "".join(matches)
    else:
        name = name.strip()
    return name.strip()

try:
    df = pd.read_excel(file_path)
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    df = df.dropna(subset=['作品使用时长（分钟）', '日期'])
    df['作品名称提取'] = df['图形化编程作品名称'].apply(extract_main_project_name)

    max_date = df['日期'].max()

    group = df.groupby('作品名称提取')
    project_stats = pd.DataFrame({
        '总使用时长（分钟）': group['作品使用时长（分钟）'].sum(),
        '首次使用日期': group['日期'].min(),
    })

    project_stats['项目类型'] = project_stats.index.to_series().apply(
        lambda x: "硬件类" if x in hardware_projects else "纯软件"
    )

    project_stats['上线天数'] = (max_date - project_stats['首次使用日期']).dt.days + 1

    # 先选择项目类型
    type_filter = st.selectbox("选择要分析的项目类型：", ["全部", "硬件类", "纯软件"])

    # 根据选择筛选
    if type_filter != "全部":
        filtered_stats = project_stats[project_stats['项目类型'] == type_filter]
    else:
        filtered_stats = project_stats

    # 计算筛选后中位数
    median_total = filtered_stats['总使用时长（分钟）'].median()

    # 按筛选后数据划分
    above = filtered_stats[filtered_stats['总使用时长（分钟）'] > median_total]
    below_or_equal = filtered_stats[filtered_stats['总使用时长（分钟）'] <= median_total]

    st.markdown(f"### 🧮 【{type_filter}】项目总使用时长的中位数为：**{median_total:.0f} 分钟**")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🟢 总使用时长高于中位数的项目：")
        for name, row in above.sort_values('总使用时长（分钟）', ascending=False).iterrows():
            st.write(f"✅ {name} - {row['总使用时长（分钟）']:.0f} 分钟")

    with col2:
        st.markdown("#### 🔵 总使用时长低于或等于中位数的项目：")
        for name, row in below_or_equal.sort_values('总使用时长（分钟）', ascending=False).iterrows():
            st.write(f"ℹ️ {name} - {row['总使用时长（分钟）']:.0f} 分钟")

    # 项目选择
    sorted_projects = filtered_stats.sort_values('总使用时长（分钟）', ascending=False).index.tolist()
    selected_project = st.selectbox("选择项目查看总使用时长：", options=sorted_projects)

    if selected_project:
        total_time = filtered_stats.loc[selected_project, '总使用时长（分钟）']
        fig = go.Figure()
        fig.add_bar(
            x=[selected_project],
            y=[total_time],
            text=[f"{total_time:.0f} 分钟"],
            textposition='outside'
        )
        fig.update_layout(
            title=f"📊 `{selected_project}` 总使用时长",
            yaxis_title="使用时长（分钟）"
        )
        st.plotly_chart(fig, use_container_width=True)

except FileNotFoundError:
    st.error("❌ 没有找到 Excel 文件。请确保文件存在于 `data/usage_data.xlsx`。")
except Exception as e:
    st.error(f"❌ 数据加载失败：{e}")
