import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="图形化编程作品分析", layout="wide")
st.title("📊 图形化编程作品使用时长分析")

# 🗂 设置本地 Excel 文件路径（相对路径）
file_path = os.path.join("data", "usage_data.xlsx")

# 加载数据
try:
    df = pd.read_excel(file_path)

    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    df = df.dropna(subset=['作品使用时长（分钟）'])

    df['作品名称提取'] = df['图形化编程作品名称'].apply(
        lambda name: str(name).split('_', 1)[1] if '_' in str(name) else name
    )

    work_time_summary = df.groupby('作品名称提取')['作品使用时长（分钟）'].sum().sort_values(ascending=False)
    works = work_time_summary.index.tolist()

    selected = st.selectbox("选择作品：", options=works)

    if selected:
        filtered = df[df['作品名称提取'] == selected]
        total = filtered['作品使用时长（分钟）'].sum()

        # 总时长图
        total_fig = go.Figure()
        total_fig.add_bar(
            x=[selected],
            y=[total],
            text=[f"{total:.0f} 分钟"],
            textposition='outside'
        )
        total_fig.update_layout(title=f"📊 `{selected}` 总使用时长", yaxis_title="分钟")

        # 门店分布图
        store_summary = filtered.groupby('所属门店')['作品使用时长（分钟）'].sum().sort_values(ascending=False)
        store_fig = go.Figure()
        store_fig.add_bar(
            x=store_summary.index,
            y=store_summary.values,
            text=[f"{v:.0f}" for v in store_summary.values],
            textposition='outside'
        )
        store_fig.update_layout(title=f"🏫 `{selected}` 各门店使用时长分布", yaxis_title="分钟")

        st.plotly_chart(total_fig, use_container_width=True)
        st.plotly_chart(store_fig, use_container_width=True)

except FileNotFoundError:
    st.error("❌ 没有找到 Excel 文件。请确保文件存在于 `data/usage_data.xlsx`。")
except Exception as e:
    st.error(f"❌ 数据加载失败：{e}")
