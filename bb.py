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
