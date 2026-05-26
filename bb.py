import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 頁面基礎設定
st.set_page_config(layout="wide", page_title="雲端 Trello 看板", page_icon="📋")

# 2. 注入自訂高級感 CSS
st.markdown("""
<style>
    /* 全局字體與背景微調 */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 調整表單區塊與看板區塊的間距 */
    [data-testid="stForm"] {
        border-radius: 12px;
        background-color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef !important;
        padding: 1.5rem !important;
    }
    
    /* 看板欄位背景與圓角 */
    [data-testid="stColumn"] {
        background-color: #f1f3f5;
        padding: 15px !important;
        border-radius: 12px;
        min-height: 500px;
    }
    
    /* 自訂精緻卡片樣式 */
    .trello-card {
        background-color: #ffffff;
        padding: 14px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        border-left: 5px solid #6c757d; /* 預設灰邊 */
        margin-bottom: 12px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .trello-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    /* 各狀態卡片的左側邊框顏色 */
    .card-todo { border-left-color: #ff6b6b; }
    .card-progress { border-left-color: #fcc419; }
    .card-done { border-left-color: #51cf66; }
    
    /* 欄位頂部精緻標題 */
    .column-header {
        font-size: 1.1rem;
        font-weight: 700;
        padding: 6px 12px;
        border-radius: 6px;
        margin-bottom: 15px;
        display: inline-block;
    }
    .header-todo { background-color: #fff5f5; color: #c92a2a; }
    .header-progress { background-color: #fff9db; color: #e67700; }
    .header-done { background-color: #ebfbee; color: #2b8a3e; }
    
    /* 刪除線樣式優化 */
    .completed-text {
        text-decoration: line-through;
        color: #adb5bd;
    }
</style>
""", unsafe_allow_html=True)

# 3. 標題與版權
st.write("## 🗂️ 團隊專案雲端看板")
st.caption("授權標註：edit by 闕河正 | UI/UX 高級視覺優化版")

# 初始化 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="Tasks", ttl="0")

# ==========================================
#  區塊一：指派任務表單（視覺微調）
# ==========================================
with st.form("task_input_form", clear_on_submit=True):
    st.markdown("<p style='font-weight:600; color:#495057; margin-bottom:-5px;'>⚡ 快速指派新任務</p>", unsafe_allow_html=True)
    c_title, c_status, c_owner, c_btn = st.columns([3, 1.5, 1.5, 1.5])
    
    with c_title:
        new_title = st.text_input("任務名稱", placeholder="要做些什麼...", label_visibility="collapsed")
    with c_status:
        new_status = st.selectbox("狀態", ["To Do", "In Progress", "Done"], label_visibility="collapsed")
    with c_owner:
        new_owner = st.text_input("負責人", placeholder="負責人...", label_visibility="collapsed")
    with c_btn:
        # 讓按鈕填滿高度，與輸入框對齊
        submit_btn = st.form_submit_button("➕ 新增任務", use_container_width=True)

if submit_btn and new_title and new_owner:
    new_data = {"title": new_title, "status": new_status, "owner": new_owner}
    new_row = pd.DataFrame([new_data])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    conn.update(worksheet="Tasks", data=updated_df)
    st.toast("🎉 任務已成功同步至雲端！", icon="🚀")
    st.rerun()

st.write(" ") # 留白空格

# ==========================================
#  區塊二：Trello 看板畫布渲染
# ==========================================
columns_config = [
    {"status": "To Do", "title": "🔴 待辦事項", "class": "card-todo", "header_class": "header-todo"},
    {"status": "In Progress", "title": "🟡 執行中", "class": "card-progress", "header_class": "header-progress"},
    {"status": "Done", "title": "🟢 已完成", "class": "card-done", "header_class": "header-done"}
]

# 建立 Streamlit 三縱欄
trello_cols = st.columns(3)

for col_idx, config in enumerate(columns_config):
    status_name = config["status"]
    
    with trello_cols[col_idx]:
        # 渲染極簡精緻的欄位標頭
        st.markdown(f"<div class='column-header {config['header_class']}'>{config['title']}</div>", unsafe_allow_html=True)
        
        filtered_list = df[df["status"] == status_name]
        
        if not filtered_list.empty:
            for idx, row in filtered_list.iterrows():
                
                # 使用 HTML 渲染帶有高級陰影、圓角與左側狀態邊框的卡片
                if status_name == "Done":
                    card_content = f"""
                    <div class='trello-card {config['class']}'>
                        <div class='completed-text' style='font-weight: 600; font-size: 1.05rem;'>{row['title']}</div>
                        <div style='color: #adb5bd; font-size: 0.85rem; margin-top: 6px;'>👤 負責人: {row['owner']}</div>
                    </div>
                    """
                else:
                    card_content = f"""
                    <div class='trello-card {config['class']}'>
                        <div style='font-weight: 600; font-size: 1.05rem; color: #212529;'>{row['title']}</div>
                        <div style='color: #495057; font-size: 0.85rem; margin-top: 6px;'>👤 負責人: {row['owner']}</div>
                    </div>
                    """
                st.markdown(card_content, unsafe_allow_html=True)
                
                # --- 卡片底部的操作微調區 ---
                c_change, c_del = st.columns([3, 1])
                
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
                    if st.button("🗑️", key=f"del_{idx}", use_container_width=True, help="刪除此任務"):
                        df = df.drop(idx).reset_index(drop=True)
                        conn.update(worksheet="Tasks", data=df)
                        st.rerun()
                
                # 幫卡片之間留一點好看的呼吸空隙
                st.write("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color: #868e96; font-size: 0.9rem; font-style: italic; padding-left: 5px;'>暫無任務</p>", unsafe_allow_html=True)
