import streamlit as st
import random

# 1. 網頁基礎設定 (手機看也很美)
st.set_page_config(page_title="ETE 模擬訓練系統", layout="centered")

# 2. 標題與你的作者資訊
st.title("🚀 ETE 模擬訓練系統 v7.5 (Web)")
st.caption("專為快速交接與優先權訓練設計")
st.sidebar.markdown(f"### 👤 開發者：[Henrylin]\n**版本：Mobile Ready**")

# --- 替換原本的數據初始化積木 ---
if 'machines' not in st.session_state or st.sidebar.button("🎲 刷新隨機題目"):
    st.session_state.submitted = False
    data = []
    # 定義你的新分類
    status_pool = {
        "正常": ["UP", "LOST"],
        "測機": ["PMON", "DMON"],
        "待機": ["WPE", "WEQ"],
        "爆點": ["WALP", "LOT_Q"]
    }
    
    # 為了控制爆點數量，我們先生成一個隨機清單
    # 前 10 台有機會是爆點，後面 24 台強制避開爆點狀態
    for i in range(1, 35):
        if i <= 10:
            # 前 10 台隨機選取所有狀態
            cat = random.choice(list(status_pool.keys()))
        else:
            # 後面台數排除「爆點」分類
            cat = random.choice(["正常", "測機", "待機"])
            
        st_type = random.choice(status_pool[cat])
        
        # 邏輯優化：如果是爆點分類，秒數設為 5~6 小時；其餘設為 4 小時以下
        if cat == "爆點":
            sec = random.randint(18001, 21600)
        else:
            sec = random.randint(3600, 17999)
            
        data.append({"id": f"EQP-{i:02d}", "status": st_type, "sec": sec})
    
    random.shuffle(data) # 打亂順序，讓爆點不一定在前面
    st.session_state.machines = data
    st.rerun()
# --- 關鍵修正：先準備好存答案的盒子 ---
user_answers = {}     
for m in st.session_state.machines:
    # 判斷是否為爆點 (5小時)
    is_danger = m['sec'] >= 18000
    
    # 使用摺疊選單，手機才不會滑到手痠
    label = f"🛠️ {m['id']} | {'⚠️ 爆點' if is_danger else '✅ 正常'}"
    with st.expander(label):
        col1, col2 = st.columns([1, 1])
        col1.write(f"狀態: **{m['status']}**")
        # --- 修改這裡：讓爆點時間變紅色 ---
        display_time = f"{m['sec']//3600}H {m['sec']%3600//60}M"
        if m['sec'] >= 18000:
            col1.markdown(f"運行: <span style='color: #ff4b4b; font-weight: bold;'>{display_time} ⚠️</span>", unsafe_allow_html=True)
        else:
            col1.write(f"運行: {display_time}")
        # -------------------------------
        
        # 選擇優先級 (單選按鈕)
        user_answers[m['id']] = col2.radio(
            "優先級", [1, 2, 3, 4], 
            key=f"r_{m['id']}", 
            horizontal=True,
            index=3 # 預設在 4
        )
        # --- 複習模式：提交後顯示正確答案 ---
        is_danger = m['sec'] >= 18000
        real_answer = 1 if is_danger else 4 
        
        if 'submitted' in st.session_state and st.session_state.submitted:
            if user_answers[m['id']] == real_answer:
                st.success("✅ 判斷正確")
            else:
                st.error(f"❌ 應選: Priority {real_answer}")
# 5. 結算與 AI 診斷
st.write("---")
if st.button("提交診斷"):
    # 1. 設置提交狀態為 True
    st.session_state.submitted = True
    
    correct = 0
    total = len(st.session_state.machines)
    wrong_types = [] # 紀錄出錯的狀態分類

    for m in st.session_state.machines:
        is_danger = m['sec'] >= 18000
        ans = 1 if is_danger else 4
        # 這裡從 radio 抓取答案
        if user_answers[m['id']] == ans:
            correct += 1
        else:
            wrong_types.append(m['status'])

    # 2. 計算分數並存入 session_state (這點很重要)
    st.session_state.final_score = int(correct/total*100)
    st.session_state.correct_count = correct

    score = int(correct/total*100) # 這是區域變數，重整後會消失
    
    # 將結果存入 session_state 保險箱
    st.session_state.final_score = score
    st.session_state.final_correct = correct
    st.session_state.final_total = total
    st.session_state.final_wrong_types = wrong_types
    st.session_state.submitted = True
    
    # 3. 觸發氣球
    st.balloons()
    
    # 4. 強制刷新！這會讓程式從第 1 行重新跑，
    # 屆時上方的 if 'submitted' in st.session_state 就會成真，立刻秀出結果
    st.rerun()
    
# --- AI 答題報告報告 ---
if 'submitted' in st.session_state and st.session_state.submitted:
    st.write("---")
    st.subheader("🤖 AI 診斷報告")
    
    # 從保險箱讀取數據，如果還沒存過就預設為 0 或空清單
    score = st.session_state.get('final_score', 0)
    correct = st.session_state.get('final_correct', 0)
    total = st.session_state.get('final_total', 0)
    wrong_types = st.session_state.get('final_wrong_types', [])
    
    col_a, col_b = st.columns(2)
    col_a.metric("最終得分", f"{score}%")
    col_b.metric("正確題數", f"{correct}/{total}")

    if score == 100:
        st.success("Perfect! 你對 ETE 的敏感度已經達到資深工程師水準。")
    else:
        # 分析哪種狀態最弱
        if wrong_types:
            most_wrong = max(set(wrong_types), key=wrong_types.count)
            st.warning(f"分析結果：你對 **{most_wrong}** 狀態的判斷較猶豫。")
        st.info("建議：Priority 1 代表需要立即處理(超過5H)，請優先掃描紅色標註機台。")
        
# 在 App 最後面加上成就勳章
st.write("---")
with st.expander("🏆 開發者成就獎章"):
    st.write("""
    - ✅ **Debug 高手**：解決了縮進與 UI 衝突問題
    - ✅ **雲端架構師**：完成 GitHub 與 Streamlit 部署
    - ✅ **問題解決者**：成功開發 ETE 模擬訓練系統
    - *“進步是為了更好的交接！”*
    """)
