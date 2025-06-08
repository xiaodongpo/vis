# app.py
import pandas as pd
import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 加载清洗后的数据
df = pd.read_csv("cleaned_sms_dataset.csv", parse_dates=["recitime", "conntime"])

st.title("北京市伪基站垃圾短信分析系统")

# 1. 选择某一天的短信数据
unique_dates = df['recitime'].dt.date.unique()
selected_date = st.selectbox("选择分析日期", unique_dates)

# 筛选出选择日期的数据
df_day = df[df['recitime'].dt.date == selected_date]

# 2. 日期选择后的短信数量变化
st.subheader(f"该日短信数量变化")
hourly_counts = df_day['recitime'].dt.hour.value_counts().sort_index()
fig = px.line(x=hourly_counts.index, y=hourly_counts.values, labels={'x': '小时', 'y': '短信数量'})
st.plotly_chart(fig)

# 3. 伪基站短信分布地图
st.subheader(f"伪基站短信分布地图（{selected_date}）")
time_range = st.slider("选择时间段", 0, 23, (0, 23), step=1)
df_filtered = df_day[df_day['recitime'].dt.hour.between(time_range[0], time_range[1])]

fig_map = px.scatter_mapbox(
    df_filtered.sample(n=min(5000, len(df_filtered))),  # 采样加速绘图
    lat="lat", lon="lng",
    hover_data=["content", "phone", "recitime"],
    zoom=10,
    height=500
)
fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map)

# 4. 高频伪装号码（仅该天的数据）
st.subheader(f"高频伪装号码（{selected_date}）")
top_phones = df_day['phone'].value_counts().head(10)
st.bar_chart(top_phones)

# 5. 短信内容词云（仅该天的数据）
st.subheader(f"短信内容词云（{selected_date}）")
text = " ".join(df_day['content'].dropna().astype(str).values)
wordcloud = WordCloud(font_path='simhei.ttf', background_color="white", width=800, height=400).generate(text)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
st.pyplot(plt)

# 6. 短信内容关键词搜索
st.subheader(f"短信内容关键词搜索")
search_query = st.text_input("输入关键词", "")
if search_query:
    df_search = df_day[df_day['content'].str.contains(search_query, case=False, na=False)]
    st.write(f"找到 {len(df_search)} 条包含关键词 '{search_query}' 的短信记录")
    # 显示搜索结果
    st.write(df_search[['phone', 'content', 'recitime']].head(10))
else:
    st.write("请输入关键词以进行内容过滤")
