import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 頁面基礎設定
st.set_page_config(layout="wide", page_title="團隊雲端行事曆看板", page_icon="📅")

# 2. 注入自訂：行事曆專屬高密度 CSS
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f6f8fa;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    [data-testid="stForm"] {
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #e1e4e6 !important;
        padding: 1rem !important;
    }
    
    /* 行事曆欄位（一到五）專用背景：更緊湊、帶有縱向邊框感 */
    .calendar-col {
        background-color: #ffffff;
        padding: 8px !important;
        border-radius: 8px;
        border: 1px solid #e1e4e6;
        min-height: 350px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    
    /* 緊湊型行事曆卡片 */
    .cal-card {
        background-color: #f8f9fa;
        padding: 6px 10px;
        border-radius: 4px;
        border-left: 4px solid #4dadf7; /* 預設水藍色行事曆風格 */
        margin-bottom: 6px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    
    /* 根據狀態改變行事曆卡片顏色，一眼看穿進度 */
    .cal-todo { border-left-color: #ff4d4d; }
    .cal-progress { border-left-color: #ff922b; background-color: #fff9db; }
    .cal-done { border-left-color: #40c057; opacity: 0.6; }
    
    /* 字體醒目大字 */
    .cal-title {
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        color: #1a1a1a;
        line-height: 1.2;
    }
    
    .cal-owner {
        color: #495057;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 2px;
    }
    
    /* 星期標頭 */
    .day-header {
        font-size: 1.1rem;
        font-weight: 800;
        text-align: center;
        padding: 4px;
        background-color: #e9ecef;
        border-radius: 4px;
        margin-bottom: 8px;
        color: #343a40;
    }
    
    .completed-text {
        text-decoration: line-through;
        color: #adb5bd;
    }
</style>
""", unsafe_allow_html=True)

st.write("## 📅 團隊大字版週行事曆看板")
st.caption("授權標註：edit by 闕河正 | 行事曆風格視覺排版")

# 初始化 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="Tasks", ttl="0")

# 確保資料表有 day 欄位（防呆機制）
if "day" not in df.columns:
    df["day"] = "Monday"

# ==========================================
#  區塊一：快速指派表單（新增「星期」下拉選單）
# ==========================================
with st.form("task_input_form", clear_on_submit=True):
    c_title, c_day, c_status, c_owner, c_btn = st.columns([3, 1.5, 1.5, 1.5, 1.5])
    
    with c_title:
        new_title = st.text_input("任務名稱", placeholder="⚡ 新增排程任務...", label_visibility="collapsed")
    with c_day:
        new_day = st.selectbox("安排在星期幾", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], label_visibility="collapsed")
    with c_status:
        new_status = st.selectbox("狀態", ["To Do", "In Progress", "Done"], label_visibility="collapsed")
    with c_owner:
        new_owner = st.text_input("負責人", placeholder="👤 負責人...", label_visibility="collapsed")
    with c_btn:
        submit_btn = st.form_submit_button("📅 排入行事曆", use_container_width=True)

if submit_btn and new_title and new_owner:
    new_data = {"title": new_title, "status": new_status, "owner": new_owner, "day": new_day}
    new_row = pd.DataFrame([new_data])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    conn.update(worksheet="Tasks", data=updated_df)
    st.toast("🎉 行事曆排程已同步！", icon="📅")
    st.rerun()

st.write(" ")

# ==========================================
#  區塊二：行事曆風五軌看板 (Mon ~ Fri)
# ==========================================
st.write("### 🗓️ 本週工作排程一覽")

days_of_week = [
    {"eng": "Monday", "chi": "週一 Mon"},
    {"eng": "Tuesday", "chi": "週二 Tue"},
    {"eng": "Wednesday", "chi": "週三 Wed"},
    {"eng": "Thursday", "chi": "週四 Thu"},
    {"eng": "Friday", "chi": "週五 Fri"}
]

# 建立 5 個縱欄代表星期一到星期五
cal_cols = st.columns(5)

# 對應狀態的 CSS class 字典
status_classes = {
    "To Do": "cal-todo",
    "In Progress": "cal-progress",
    "Done": "cal-done"
}

for idx, day_config in enumerate(days_of_week):
    day_eng = day_config["eng"]
    
    with cal_cols[idx]:
        # 渲染星期標頭
        st.markdown(f"<div class='day-header'>{day_config['chi']}</div>", unsafe_allow_html=True)
        
        # 外層包裹一個自訂的欄位容器
        st.markdown("<div class='calendar-col'>", unsafe_allow_html=True)
        
        # 篩選出屬於今天的所有任務
        day_tasks = df[df["day"] == day_eng]
        
        if not day_tasks.empty:
            for t_idx, row in day_tasks.iterrows():
                status_class = status_classes.get(row['status'], "")
                
                # 行事曆卡片 HTML 渲染
                if row['status'] == "Done":
                    card_html = f"""
                    <div class='cal-card {status_class}'>
                        <div class='cal-title completed-text'>{row['title']}</div>
                        <div class='cal-owner'>👤 {row['owner']} (已完成)</div>
                    </div>
                    """
                else:
                    card_html = f"""
                    <div class='cal-card {status_class}'>
                        <div class='cal-title'>{row['title']}</div>
                        <div class='cal-owner'>👤 {row['owner']}</div>
                    </div>
                    """
                st.markdown(card_html, unsafe_allow_html=True)
                
                # 卡片內微型操作（變更狀態或刪除，極致緊湊版）
                c_opt, c_del = st.columns([3, 1])
                with c_opt:
                    current_options = ["To Do", "In Progress", "Done"]
                    def_idx = current_options.index(row['status'])
                    changed_status = st.selectbox(
                        "修改狀態", current_options, index=def_idx, key=f"cal_status_{t_idx}", label_visibility="collapsed"
                    )
                    if changed_status != row['status']:
                        df.at[t_idx, "status"] = changed_status
                        conn.update(worksheet="Tasks", data=df)
                        st.rerun()
                with c_del:
                    if st.button("🗑️", key=f"cal_del_{t_idx}", use_container_width=True):
                        df = df.drop(t_idx).reset_index(drop=True)
                        conn.update(worksheet="Tasks", data=df)
                        st.rerun()
        else:
            st.markdown("<p style='color: #adb5bd; font-size: 0.85rem; text-align:center; font-style:italic;'>💡 空白</p>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True) # 關閉 calendar-col 容器
