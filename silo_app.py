import streamlit as st
import pandas as pd
import io

# --- [디자인 및 스타일 로직] ---
def get_style(name, qty):
    name = str(name).upper()
    if name in ["WCRS", "WAH", "WUR"]: p_color = "#E67E22"  # 주황
    elif name in ["WASW", "WUSH", "WUSL9.0", "BB", "WASWP"]: p_color = "#0000FF"  # 파랑
    elif name in ["YBG2", "BU", "YU", "YR2", "YE2"]: p_color = "#27AE60"  # 초록
    else: p_color = "#333"
    
    try:
        val = float(str(qty).replace(',', ''))
        qty_color = "red" if val == 0 else "black"
        display_qty = "{:,.0f}".format(val)
    except:
        qty_color = "black"
        display_qty = qty
    return p_color, qty_color, display_qty

def make_block(prefix, rect_start, circ_start, df):
    def find_val(code):
        if df is not None:
            res = df[df.iloc[:, 0].astype(str).str.contains(code, na=False)]
            if not res.empty:
                return res.iloc[0, 1], res.iloc[0, 2] # 곡종, 재고량
        return "N/A", 0

    rects_html = '<div class="rect-grid">'
    for row in range(2):
        for col in range(7):
            code = f"{prefix}{rect_start + col + (row*7)}"
            name, raw_qty = find_val(code)
            p_c, q_c, qty = get_style(name, raw_qty)
            # 툴팁 데이터 삽입: data- 속성 사용
            rects_html += f'<div class="rect-item"><div class="text-box" data-c="{code}" data-n="{name}" data-q="{qty}"><span class="p-name" style="color:{p_c}">{name}</span><span class="p-qty" style="color:{q_c}">{qty}</span><span class="p-code">{code}</span></div></div>'
    
    circles_html = '<div class="circle-overlay">'
    for r_idx, y_pos in enumerate([0, 160, 320]):
        for c_idx in range(6):
            x_pos = (c_idx + 1) * 90
            code = f"{prefix}{circ_start + c_idx + (r_idx*6)}"
            name, raw_qty = find_val(code)
            p_c, q_c, qty = get_style(name, raw_qty)
            # 툴팁 데이터 삽입: data- 속성 사용
            circles_html += f'<div class="circle-item" style="top: {y_pos}px; left: {x_pos}px;"><div class="text-box" data-c="{code}" data-n="{name}" data-q="{qty}"><span class="p-name" style="color:{p_c}">{name}</span><span class="p-qty" style="color:{q_c}">{qty}</span><span class="p-code">{code}</span></div></div>'
    return rects_html + circles_html + '</div>'

# --- [웹 화면 구성] ---
st.set_page_config(layout="wide", page_title="싸이로 재고 현황")

st.markdown("<h1 style='text-align: center;'>🌾 실시간 싸이로 재고 현황판</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>엑셀 데이터를 복사해서 아래 칸에 붙여넣으세요 (Ctrl+C -> Ctrl+V)</p>", unsafe_allow_html=True)

raw_data = st.text_area("📋 엑셀 데이터 붙여넣기", height=150, placeholder="장치장 곡종 재고량 순서로 복사된 데이터를 여기에 붙여넣으세요.")

if raw_data.strip():
    try:
        df = pd.read_csv(io.StringIO(raw_data), sep='\t', names=['장치장', '곡종', '재고량'], header=None)
        if df['장치장'].iloc[0] == '장치장':
            df = df[1:]
        
        A_L = make_block("A", 201, 101, df)
        A_R = make_block("A", 207, 107, df)
        B_L = make_block("B", 201, 101, df)
        B_R = make_block("B", 207, 107, df)

        st.components.v1.html(f"""
        <style>
            .silo-wrapper {{ display: flex; flex-direction: column; align-items: center; gap: 40px; font-family: 'Malgun Gothic'; }}
            .silo-container {{ position: relative; width: 780px; height: 500px; border: 3px solid #000; background: #fff; display: flex; justify-content: center; align-items: center; }}
            .rect-grid {{ display: grid; grid-template-columns: repeat(7, 90px); grid-template-rows: repeat(2, 160px); position: relative; }}
            .rect-item {{ border: 1px solid #444; width: 90px; height: 160px; position: relative; }}
            .circle-overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 10; }}
            .circle-item {{ position: absolute; width: 100px; height: 100px; border-radius: 50%; border: 2.5px solid #000; background: #fff; display: flex; align-items: center; justify-content: center; transform: translate(-50%, -50%); pointer-events: auto; }}
            .text-box {{ display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; height: 100%; position: absolute; cursor: pointer; }}
            
            /* 마우스 대면 뜨는 한글 이모지 툴팁 */
            .text-box::after {{
                content: "📍 위치: " attr(data-c) "\\A🌾 곡종: " attr(data-n) "\\A📦 재고: " attr(data-q) "t";
                white-space: pre; position: absolute; bottom: 105%; left: 50%; transform: translateX(-50%);
                background: rgba(0,0,0,0.8); color: white; padding: 8px; border-radius: 5px; font-size: 12px;
                opacity: 0; visibility: hidden; transition: 0.2s; z-index: 100; width: 110px; text-align: left;
            }}
            .text-box:hover::after {{ opacity: 1; visibility: visible; }}
            .circle-item:hover {{ z-index: 50; border-color: #74c934; }}

            .p-name {{ font-size: 15px; font-weight: bold; }}
            .p-qty {{ font-size: 14px; font-weight: bold; }}
            .p-code {{ font-size: 11px; color: #74c934; }}
        </style>
        <div class="silo-wrapper">
            <div style="font-size:24px; font-weight:bold;">싸이로 A</div>
            <div style="display:flex; gap:40px;"><div class="silo-container">{A_L}</div><div class="silo-container">{A_R}</div></div>
            <div style="font-size:24px; font-weight:bold; margin-top:20px;">싸이로 B</div>
            <div style="display:flex; gap:40px;"><div class="silo-container">{B_L}</div><div class="silo-container">{B_R}</div></div>
        </div>
        """, height=1200)
    except Exception as e:
        st.error(f"데이터 형식이 올바르지 않습니다. 다시 복사해주세요. ({e})")
else:
    st.info("💡 엑셀에서 데이터를 복사하여 위 칸에 붙여넣으면 현황판이 나타납니다.")
