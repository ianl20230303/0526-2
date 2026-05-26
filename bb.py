import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(layout="wide", page_title="團隊雲端行事曆看板", page_icon="📅")

# 注入自訂：完美緊湊、無大空白 CSS
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
    
    /* 移除 min-height 的大空格，改用輕量級的底色與圓角 */
    .calendar-column-box {
        background-color: #eaecef;
        padding: 8px !important;
        border-radius: 8px;
        /* 拔除 min-height: 350px，不再強行留白！ */
    }
    
    /* 極致緊湊型卡片 */
    .cal-card {
        background-color: #ffffff;
        padding: 6px 10px;
        border-radius: 6px;
        border-left: 6px solid #4dadf7; 
        margin-bottom: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .cal-todo { border-left-color: #ff4d4d; }
    .cal-progress { border-left-color: #ff922b; }
    .cal-done { border-left-color: #40c057; }
    
    .cal-title {
        font-size: 1.2rem !important; /* 保持一眼看清的大字 */
        font-weight: 800 !important;   /* 極致加粗 */
        color: #1a1a1a;
        line-height: 1.2;
    }
    
    .cal-owner {
        color: #495057;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 2px;
    }
    
    /* 星期標頭大字 */
    .day-header {
        font-size: 1.15rem;
        font-weight: 800;
        text-align: center;
        padding: 5px;
        background-color: #dee2e6;
        border-radius: 6px;
        margin-bottom: 8px;
        color: #212529;
    }
    
    .completed-text {
        text-decoration: line-through;
        color: #adb5bd;
    }
</style>
""", unsafe_allow_html=True)

st.write("## 📅 團隊大字版週行事曆看板")
st.caption("授權標註：edit by 闕河正 | 緊湊無留白版")

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="Tasks", ttl="0")

if "day" not in df.columns:
    df["day"] = "Monday"

# ==========================================
#  區塊一：快速指派表單
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
#  區塊二：行事曆風五軌看板（已修正大空白）
# ==========================================
st.write("### 🗓️ 本週工作排程一覽")

days_of_week = [
    {"eng": "Monday", "chi": "週一 Mon"},
    {"eng": "Tuesday", "chi": "週二 Tue"},
    {"eng": "Wednesday", "chi": "週實 Wed"},
    {"eng": "Thursday", "chi": "週四 Thu"},
    {"eng": "Friday", "chi": "週五 Fri"}
]

cal_cols = st.columns(5)
status_classes = {"To Do": "cal-todo", "In Progress": "cal-progress", "Done": "cal-done"}

for idx, day_config in enumerate(days_of_week):
    day_eng = day_config["eng"]
    
    with cal_cols[idx]:
        st.markdown(f"<div class='day-header'>{day_config['chi']}</div>", unsafe_allow_html=True)
        
        # 篩選今天任務
        day_tasks = df[df["day"] == day_eng]
        
        # 外層包裹一個會隨內容自動縮放的緊湊灰色底色塊
        st.markdown("<div class='calendar-column-box'>", unsafe_allow_html=True)
        
        if not day_tasks.empty:
            for t_idx, row in day_tasks.iterrows():
                status_class = status_classes.get(row['status'], "")
                
                if row['status'] == "Done":
                    card_html = f"""
                    <div class='cal-card {status_class}'>
                        <div class='cal-title completed-text'>{row['title']}</div>
                        <div class='cal-owner'>👤 {row['owner']}</div>
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
                
                # 微型控制按鈕
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
            # 當沒有任務時，顯示極為緊湊的小提示，不佔空間
            st.markdown("<p style='color: #868e96; font-size: 0.85rem; text-align:center; margin: 5px 0;'>💡 暫無排程</p>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<p style='color: #adb5bd; font-size: 0.85rem; text-align:center; font-style:italic;'>💡 空白</p>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True) # 關閉 calendar-col 容器
