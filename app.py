# app.py
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ========== 📁 数据读取与预处理 ==========
file_path = '/Users/elite/Downloads/各校区每日图形化编程作品使用时长_全部数据_20250521184525.xlsx'
df = pd.read_excel(file_path)
df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
df = df.dropna(subset=['作品使用时长（分钟）'])

# 提取干净的作品名称
def extract_work_name(name):
    name = str(name)
    parts = name.split('_', 1)
    return parts[1] if len(parts) == 2 else name

df['作品名称提取'] = df['图形化编程作品名称'].apply(extract_work_name)

# ========== 🎛 Streamlit 页面结构 ==========
st.title("🎯 图形化编程作品使用分析")
st.markdown("按作品名称查看总使用时长及各门店分布")

# ========== 🔢 生成作品下拉选项 ==========
work_time_summary = (
    df.groupby('作品名称提取')['作品使用时长（分钟）']
    .sum()
    .sort_values(ascending=False)
)
works = work_time_summary.index.tolist()

selected = st.selectbox("选择作品:", options=[''] + works)

if selected:
    filtered = df[df['作品名称提取'] == selected]
    total = filtered['作品使用时长（分钟）'].sum()

    # 总时长图
    total_fig = go.Figure()
    total_fig.add_bar(
        x=[selected],
        y=[total],
        text=[f'{total:.0f} 分钟'],
        textposition='outside'
    )
    total_fig.update_layout(
        title=f'📊 `{selected}` 总使用时长',
        xaxis_title='作品名称',
        yaxis_title='总使用时长（分钟）',
        yaxis_range=[0, total * 1.2],
        template='plotly_white'
    )
    st.plotly_chart(total_fig, use_container_width=True)

    # 各门店图
    store_summary = (
        filtered.groupby('所属门店')['作品使用时长（分钟）']
        .sum()
        .sort_values(ascending=False)
    )

    store_fig = go.Figure()
    store_fig.add_bar(
        x=store_summary.index.tolist(),
        y=store_summary.values.tolist(),
        text=[f'{v:.0f}' for v in store_summary.values],
        textposition='outside'
    )
    store_fig.update_layout(
        title=f'🏫 `{selected}` 各门店使用时长分布',
        xaxis_title='所属门店',
        yaxis_title='使用时长（分钟）',
        yaxis_range=[0, store_summary.max() * 1.2],
        template='plotly_white'
    )
    st.plotly_chart(store_fig, use_container_width=True)
