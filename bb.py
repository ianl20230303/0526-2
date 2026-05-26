import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 頁面基礎設定
st.set_page_config(layout="wide", page_title="雲端 Trello 看板", page_icon="📋")

# 2. 注入自訂：高密度、大字體 CSS
st.markdown("""
<style>
    /* 全局背景與微調 */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f6f8fa;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* 表單區塊緊湊化 */
    [data-testid="stForm"] {
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #e1e4e6 !important;
        padding: 1rem !important;
    }
    
    /* 看板欄位背景與圓角（縮小外距讓空間更大） */
    [data-testid="stColumn"] {
        background-color: #eaecef;
        padding: 10px !important;
        border-radius: 10px;
        min-height: 600px;
    }
    
    /* 緊湊型卡片（縮小 Padding、強化左邊條） */
    .trello-card {
        background-color: #ffffff;
        padding: 8px 12px; /* 縮小內距，讓格子變小 */
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-left: 6px solid #6c757d; 
        margin-bottom: 8px; /* 卡片間距縮小 */
        transition: transform 0.1s ease;
    }
    .trello-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 3px 8px rgba(0,0,0,0.08);
    }
    
    /* 狀態邊條顏色 */
    .card-todo { border-left-color: #ff4d4d; }
    .card-progress { border-left-color: #ff922b; }
    .card-done { border-left-color: #40c057; }
    
    /* 任務名稱：字體加大、特粗、一眼看清 */
    .task-title {
        font-size: 1.25rem !important; /* 字體放大 */
        font-weight: 800 !important;   /* 極致加粗 */
        color: #1a1a1a;
        line-height: 1.3;
        margin-bottom: 4px;
    }
    
    /* 負責人小字稍微調深，增加對比度 */
    .task-owner {
        color: #495057;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* 欄位頂部標題放大 */
    .column-header {
        font-size: 1.2rem;
        font-weight: 800;
        padding: 6px 12px;
        border-radius: 6px;
        margin-bottom: 10px;
        display: inline-block;
    }
    .header-todo { background-color: #ffe3e3; color: #c92a2a; }
    .header-progress { background-color: #fff3bf; color: #d9480f; }
    .header-done { background-color: #d3f9d8; color: #2b8a3e; }
    
    .completed-text {
        text-decoration: line-through;
        color: #adb5bd;
    }
    
    /* 調整 Streamlit 元件在卡片內的緊湊度 */
    .stSelectbox div[data-baseweb="select"] {
        min-height: 28px !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. 主標題
st.write("## 🗂️ 團隊專案雲端看板")
st.caption("授權標註：edit by 闕河正 | 高密度、醒目大字版")

# 初始化 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="Tasks", ttl="0")

# ==========================================
#  區塊一：快速指派表單
# ==========================================
with st.form("task_input_form", clear_on_submit=True):
    c_title, c_status, c_owner, c_btn = st.columns([3.5, 1.5, 1.5, 1.5])
    
    with c_title:
        new_title = st.text_input("任務名稱", placeholder="⚡ 快速新增任務...", label_visibility="collapsed")
    with c_status:
        new_status = st.selectbox("狀態", ["To Do", "In Progress", "Done"], label_visibility="collapsed")
    with c_owner:
        new_owner = st.text_input("負責人", placeholder="👤 負責人...", label_visibility="collapsed")
    with c_btn:
        submit_btn = st.form_submit_button("➕ 指派同步", use_container_width=True)

if submit_btn and new_title and new_owner:
    new_data = {"title": new_title, "status": new_status, "owner": new_owner}
    new_row = pd.DataFrame([new_data])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    conn.update(worksheet="Tasks", data=updated_df)
    st.toast("🎉 任務已成功同步！", icon="🚀")
    st.rerun()

st.write(" ") 

# ==========================================
#  區塊二：緊湊型 Trello 看板渲染
# ==========================================
columns_config = [
    {"status": "To Do", "title": "📌 待辦事項", "class": "card-todo", "header_class": "header-todo"},
    {"status": "In Progress", "title": "⚡ 執行中", "class": "card-progress", "header_class": "header-progress"},
    {"status": "Done", "title": "✅ 已完成", "class": "card-done", "header_class": "header-done"}
]

trello_cols = st.columns(3)

for col_idx, config in enumerate(columns_config):
    status_name = config["status"]
    
    with trello_cols[col_idx]:
        st.markdown(f"<div class='column-header {config['header_class']}'>{config['title']}</div>", unsafe_allow_html=True)
        
        filtered_list = df[df["status"] == status_name]
        
        if not filtered_list.empty:
            for idx, row in filtered_list.iterrows():
                
                # 卡片 HTML（字體大、特粗、格子小）
                if status_name == "Done":
                    card_content = f"""
                    <div class='trello-card {config['class']}'>
                        <div class='task-title completed-text'>{row['title']}</div>
                        <div class='task-owner'>👤 {row['owner']}</div>
                    </div>
                    """
                else:
                    card_content = f"""
                    <div class='trello-card {config['class']}'>
                        <div class='task-title'>{row['title']}</div>
                        <div class='task-owner'>👤 {row['owner']}</div>
                    </div>
                    """
                st.markdown(card_content, unsafe_allow_html=True)
                
                # --- 卡片底部控制微調（緊湊型佈局） ---
                c_change, c_del = st.columns([3.2, 0.8])
                
                with c_change:
                    current_options = ["To Do", "In Progress", "Done"]
                    default_idx = current_options.index(status_name)
                    
                    changed_status = st.selectbox(
                        "移動", 
                        current_options, 
                        index=default_idx, 
                        key=f"move_{idx}",
                        label_visibility="collapsed"
                    )
                    if changed_status != status_name:
                        df.at[idx, "status"] = changed_status
                        conn.update(worksheet="Tasks", data=df)
                        st.rerun()
                        
                with c_del:
                    if st.button("🗑️", key=f"del_{idx}", use_container_width=True):
                        df = df.drop(idx).reset_index(drop=True)
                        conn.update(worksheet="Tasks", data=df)
                        st.rerun()
                
                # 限制卡片底部的留白，讓整體更緊湊
                st.write("<div style='margin-bottom: 2px;'></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color: #868e96; font-size: 0.9rem; font-style: italic; padding: 5px;'>暫無任務</p>", unsafe_allow_html=True)
