import streamlit as st
import random

# 1. 網頁基礎設定 (手機看也很美)
st.set_page_config(page_title="ETE 模擬訓練系統", layout="centered")

# 2. 標題與你的作者資訊
st.title("🚀 ETE 模擬訓練系統 v7.5 (Web)")
st.caption("專為快速交接與優先權訓練設計")
st.sidebar.markdown(f"### 👤 開發者：[Henrylin]\n**版本：Mobile Ready**")

# 3. 初始化數據 (模擬 34 台機台)
if 'machines' not in st.session_state:
    data = []
    for i in range(1, 35):
        st_type = random.choice(["LOT_Q", "WALP", "WPE", "UP", "PMON"])
        # 隨機產生秒數，故意讓一些超過 18000 (5小時)
        sec = random.randint(14400, 19800) 
        data.append({"id": f"PWDA{i:02d}", "status": st_type, "sec": sec})
    st.session_state.machines = data

# 4. 建立測驗介面
st.write("---")
user_answers = {}

for m in st.session_state.machines:
    # 判斷是否為爆點 (5小時)
    is_danger = m['sec'] >= 18000
    
    # 使用摺疊選單，手機才不會滑到手痠
    label = f"🛠️ {m['id']} | {'⚠️ 爆點' if is_danger else '✅ 正常'}"
    with st.expander(label):
        col1, col2 = st.columns([1, 1])
        col1.write(f"狀態: **{m['status']}**")
        col1.write(f"運行: **{m['sec']//3600}H {m['sec']%3600//60}M**")
        
        # 選擇優先級 (單選按鈕)
        user_answers[m['id']] = col2.radio(
            "優先級", [1, 2, 3, 4], 
            key=f"r_{m['id']}", 
            horizontal=True,
            index=3 # 預設在 4
        )

# 5. 結算與 AI 診斷
st.write("---")
if st.button("📊 提交 AI 績效診斷", use_container_width=True):
    correct = 0
    total = len(st.session_state.machines)
    
    # 檢查邏輯：PD > 5H 必須是 1
    for m in st.session_state.machines:
        ans = 1 if m['sec'] >= 18000 else 4
        if user_answers[m['id']] == ans:
            correct += 1
            
    score = int(correct/total*100)
    st.balloons() # 噴氣球慶祝
    st.metric(label="最終得分", value=f"{score}%")
    
    if score >= 90:
        st.success("🤖 AI 診斷：判斷非常精準！完全具備進入 GG 的交接實力。")
    else:
        st.warning("🤖 AI 診斷：再檢查一下，PD 超過 5 小時的機台是 Priority 1 喔！")
    
    if st.button("🔄 重新產生題目"):
        del st.session_state.machines
        st.rerun()
        
# 在 App 最後面加上成就勳章
st.write("---")
with st.expander("🏆 開發者成就獎章"):
    st.write("""
    - ✅ **Debug 高手**：解決了縮進與 UI 衝突問題
    - ✅ **雲端架構師**：完成 GitHub 與 Streamlit 部署
    - ✅ **問題解決者**：成功開發 ETE 模擬訓練系統
    - *“進步是為了更好的交接！”*
    """)
