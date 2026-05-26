import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(layout="wide")
st.title(" 階段五終極威力加強版：GitHub 雲端互動 Trello 看板")
st.caption("授權標註：edit by 闕河正 | 完整功能與動態操作版")

# 初始化 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="Tasks", ttl="0")

# ==========================================
#  區塊一：上方新增任務輸入表單
# ==========================================
st.write("### 📌 指派新任務")
with st.form("task_input_form", clear_on_submit=True):
    c_title, c_status, c_owner = st.columns([2, 1, 1]) # 運用權重比例切分表單
    with c_title:
        new_title = st.text_input(" 任務名稱", placeholder="輸入任務名稱...")
    with c_status:
        new_status = st.selectbox(" 狀態", ["To Do", "In Progress", "Done"])
    with c_owner:
        new_owner = st.text_input(" 負責人", placeholder="誰來負責...")
        
    submit_btn = st.form_submit_button("確認指派並同步雲端")

if submit_btn and new_title and new_owner:
    new_data = {"title": new_title, "status": new_status, "owner": new_owner}
    new_row = pd.DataFrame([new_data])
    
    # 核心安全：使用 pd.concat 進行表格拼接
    updated_df = pd.concat([df, new_row], ignore_index=True)
    conn.update(worksheet="Tasks", data=updated_df)
    st.success(" 資料已跨越限制，成功同步寫入 Google 試算表！")
    st.rerun() 

st.write("---")

# ==========================================
#  區塊二：下方 Trello 三縱欄畫布與動態卡片渲染
# ==========================================
st.write("### 📋 看板動態狀態監控與操作")

# 定義三欄的設定（標題、顏色、對應狀態）
columns_config = [
    {"status": "To Do", "title": "To Do (待辦)", "color": "red"},
    {"status": "In Progress", "title": "In Progress (執行中)", "color": "orange"},
    {"status": "Done", "title": "Done (已完成)", "color": "green"}
]

# 建立 Streamlit 的三縱欄
trello_cols = st.columns(3)

# 用迴圈一次搞定三欄的渲染
for col_idx, config in enumerate(columns_config):
    status_name = config["status"]
    
    with trello_cols[col_idx]:
        # 渲染欄位大標題
        st.markdown(f"### <span style='color:{config['color']}'>{config['title']}</span>", unsafe_allow_html=True)
        
        # 篩選出該狀態的資料
        filtered_list = df[df["status"] == status_name]
        
        if not filtered_list.empty:
            for idx, row in filtered_list.iterrows():
                # 為每張卡片創造精緻外框
                with st.container(border=True):
                    # 如果是 Done，加上傳統完工的體感（這裡也可以保留你原本的刪除線設計）
                    if status_name == "Done":
                        st.write(f"~~**{row['title']}**~~ ✅")
                    else:
                        st.write(f"**{row['title']}**")
                    
                    st.caption(f"👤 負責人: {row['owner']}")
                    
                    # --- 動態互動區：變更狀態與刪除 ---
                    c_change, c_del = st.columns([2, 1])
                    
                    with c_change:
                        # 用 key 確保每個下拉選單都是獨立的
                        current_options = ["To Do", "In Progress", "Done"]
                        # 找出目前狀態在選項中的索引
                        default_idx = current_options.index(status_name)
                        
                        changed_status = st.selectbox(
                            "移動至", 
                            current_options, 
                            index=default_idx, 
                            key=f"move_{idx}",
                            label_visibility="collapsed" # 隱藏小標籤讓畫面更乾淨
                        )
                        
                        # 如果使用者切換了下拉選單
                        if changed_status != status_name:
                            df.at[idx, "status"] = changed_status
                            conn.update(worksheet="Tasks", data=df)
                            st.rerun()
                            
                    with c_del:
                        # 刪除按鈕
                        if st.button("🗑️ 刪除", key=f"del_{idx}", use_container_width=True):
                            df = df.drop(idx).reset_index(drop=True)
                            conn.update(worksheet="Tasks", data=df)
                            st.rerun()
        else:
            st.info(f"暫無{config['title']}")
