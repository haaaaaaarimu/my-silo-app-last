import streamlit as st
import pandas as pd
import io

# 1. 스타일 정의 (곡종별 색상 등)
def get_style(name, qty):
    name = str(name).upper()
    if name in ["WCRS", "WAH", "WUR"]: p_color = "#E67E22"
    elif name in ["WASW", "WUSH", "WUSL9.0", "BB", "WASWP"]: p_color = "#0000FF"
    elif name in ["YBG2", "BU", "YU", "YR2", "YE2"]: p_color = "#27AE60"
    else: p_color = "#333"
    
    try:
        val = float(str(qty).replace(',', ''))
        qty_color = "red" if val == 0 else "black"
        display_qty = "{:,.0f}".format(val)
    except:
        qty_color = "black"
        display_qty = qty
    return p_color, qty_color, display_qty

# 2. 개별 싸이로 블록 생성 함수
def make_block(prefix, rect_start, circ_start, df):
    def find_val(code):
        if df is not None:
            res = df[df.iloc[:, 0].astype(str).str.contains(code, na=False)]
            if not res.empty:
                return res.iloc[0, 1], res.iloc[0, 2]
        return "N/A", 0

    rects_html = '<div class="rect-grid">'
    for row in range(2):
        for col in range(7):
            code = f"{prefix}{rect_start + col + (row*7)}"
            name, raw_qty = find_val(code)
            p_c, q_c, qty = get_style(name, raw_qty)
            rects_html += f'<div class="rect-item"><div class="text-box" data-code="{code}" data-name="{name}" data-qty="{qty}"><span class="p-name" style="color:{p_c}">{name}</span><span class="p-qty" style="color:{q_c}">{qty}</span><span class="p-code">{code}</span></div></div>'
    
    circles_html = '<div class="circle-overlay">'
    for r_idx, y_pos in enumerate([0, 160, 320]):
        for c_idx in range(6):
            x_pos = (c_idx + 1) * 90
            code = f"{prefix}{circ_start + c_idx + (r_idx*6)}"
            name, raw_qty = find_val(code)
            p_c, q_c, qty = get_style(name, raw_qty)
            circles_html += f'<div class="circle-item" style="top: {y_pos}px; left: {x_pos}px;"><div class="text-box" data-code="{code}" data-name="{name}" data-qty="{qty}"><span class="p-name" style="color:{p_c}">{name}</span><span class="p-qty" style="color:{q_c}">{qty}</span><span class="p-code">{code}</span></div></div>'
    return rects_html + circles_html + '</div>'

# 3. Streamlit 설정
st.set_page_config(layout="wide", page_title="재고 현황판")
st.markdown("<h2 style='text-align: center;'>🌾 실시간 싸이로 재고 현황</h2>", unsafe_allow_html=True)

raw_data = st.text_area("데이터 붙여넣기", height=100)

if raw_data.strip():
    try:
        df = pd.read_csv(io.StringIO(raw_data), sep='\t', names=['장치장', '곡종', '재고량'], header=None)
        
        # 공통 스타일 정의
        common_style = """
        <style>
            .silo-container { position: relative; width: 700px; height: 480px; border: 2px solid #333; background: #fff; margin: 10px auto; border-radius: 10px; overflow: hidden; }
            .rect-grid { display: grid; grid-template-columns: repeat(7, 100px); height: 320px; }
            .rect-item { border: 0.5px solid #eee; position: relative; width: 100px; height: 160px; }
            .circle-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
            .circle-item { position: absolute; width: 90px; height: 90px; border-radius: 50%; border: 2px solid #000; background: #fff; display: flex; align-items: center; justify-content: center; transform: translate(-50%, -50%); pointer-events: auto; }
            .text-box { display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; height: 100%; position: relative; }
            .text-box::after { content: attr(data-name) " (" attr(data-qty) "t)"; position: absolute; bottom: 100%; background: #000; color: #fff; padding: 5px; border-radius: 5px; font-size: 11px; opacity: 0; visibility: hidden; z-index: 100; }
            .text-box:hover::after { opacity: 1; visibility: visible; }
            .p-name { font-size: 14px; font-weight: bold; }
            .p-qty { font-size: 13px; }
            .p-code { font-size: 10px; color: gray; }
        </style>
        """

        # --- 싸이로 A 구역 ---
        st.markdown("### 📍 SILO A")
        col1, col2 = st.columns(2)
        with col1:
            st.components.v1.html(common_style + f'<div class="silo-container">{make_block("A", 201, 101, df)}</div>', height=500)
        with col2:
            st.components.v1.html(common_style + f'<div class="silo-container">{make_block("A", 207, 107, df)}</div>', height=500)

        # --- 싸이로 B 구역 ---
        st.markdown("### 📍 SILO B")
        col3, col4 = st.columns(2)
        with col3:
            st.components.v1.html(common_style + f'<div class="silo-container">{make_block("B", 201, 101, df)}</div>', height=500)
        with col4:
            st.components.v1.html(common_style + f'<div class="silo-container">{make_block("B", 207, 107, df)}</div>', height=500)

    except Exception as e:
        st.error(f"데이터 형식을 확인해주세요: {e}")
