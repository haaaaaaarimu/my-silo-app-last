import streamlit as st
import pandas as pd
import io

# --- [디자인 및 스타일 로직] ---
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
            rects_html += f'<div class="rect-item"><div class="text-box" data-c="{code}" data-n="{name}" data-q="{qty}"><span class="p-name" style="color:{p_c}">{name}</span><span class="p-qty" style="color:{q_c}">{qty}</span><span class="p-code">{code}</span></div></div>'
    
    circles_html = '<div class="circle-overlay">'
    for r_idx, y_pos in enumerate([0, 160, 320]):
        for c_idx in range(6):
            x_pos = (c_idx + 1) * 90
            code = f"{prefix}{circ_start + c_idx + (r_idx*6)}"
            name, raw_qty = find_val(code)
            p_c, q_c, qty = get_style(name, raw_qty)
            circles_html += f'<div class="circle-item" style="top: {y_pos}px; left: {x_pos}px;"><div class="text-box" data-c="{code}" data-n="{name}" data-q="{qty}"><span class="p-name" style="color:{p_c}">{name}</span><span class="p-qty" style="color:{q_c}">{qty}</span><span class="p-code">{code}</span></div></div>'
    
    return rects_html + circles_html + '</div>'

# --- [웹 화면 구성] ---
st.set_page_config(layout="wide", page_title="싸이로 재고 현황")

st.markdown("<h1 style='text-align: center;'>🌾 실시간 싸이로 재고 현황판</h1>", unsafe_allow_html=True)

raw_data = st.text_area("📋 엑셀 데이터 붙여넣기", height=150)

if raw_data.strip():
    try:
        df = pd.read_csv(io.StringIO(raw_data), sep='\t', names=['장치장', '곡종', '재고량'], header=None)
        if df['장치장'].iloc[0] == '장치장': df = df[1:]
        
        A_L = make_block("A", 201, 101, df)
        A_R = make_block("A", 207, 107, df)
        B_L = make_block("B", 201, 101, df)
        B_R = make_block("B", 207, 107, df)

        st.components.v1.html(f"""
        <style>
            /* 폰트 및 배경 */
            body {{ font-family: 'Malgun Gothic', sans-serif; background-color: #ffffff; }}
            
            /* 전체를 감싸는 바구니: 높이를 충분히 확보 */
            .main-content {{ display: block; width: 1600px; margin: 0 auto; }}
            
            /* 싸이로 그룹 (A와 B를 수직으로 분리) */
            .silo-group {{ display: block; margin-bottom: 80px; clear: both; }}
            .silo-title {{ font-size: 28px; font-weight: bold; text-align: center; margin-bottom: 20px; }}
            
            /* 좌우 배치를 위한 컨테이너 */
            .flex-row {{ display: flex; justify-content: center; gap: 40px; }}
            
            /* 개별 싸이로 박스 */
            .silo-container {{ 
                position: relative; width: 780px; height: 500px; 
                border: 3px solid #000; background: #fff; 
                flex-shrink: 0; 
            }}
            
            .rect-grid {{ display: grid; grid-template-columns: repeat(7, 90px); grid-template-rows: repeat(2, 160px); position: relative; }}
            .rect-item {{ border: 1px solid #444; width: 90px; height: 160px; position: relative; }}
            .circle-overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 10; }}
            .circle-item {{ position: absolute; width: 100px; height: 100px; border-radius: 50%; border: 2.5px solid #000; background: #fff; display: flex; align-items: center; justify-content: center; transform: translate(-50%, -50%); pointer-events: auto; }}
            
            .text-box {{ display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; height: 100%; position: absolute; cursor: pointer; }}
            
            /* 툴팁 디자인 */
            .text-box:hover::after {{
                content: "📍 위치: " attr(data-c) "\\A🌾 곡종: " attr(data-n) "\\A📦 재고: " attr(data-q) "t";
                white-space: pre; position: absolute; bottom: 105%; left: 50%; transform: translateX(-50%);
                background: rgba(0,0,0,0.85); color: white; padding: 10px; border-radius: 5px; font-size: 13px;
                z-index: 999; width: 120px; text-align: left; line-height: 1.5;
            }}

            .p-name {{ font-size: 15px; font-weight: bold; }}
            .p-qty {{ font-size: 14px; font-weight: bold; }}
            .p-code {{ font-size: 11px; color: #74c934; }}
        </style>

        <div class="main-content">
            <div class="silo-group">
                <div class="silo-title">싸이로 A</div>
                <div class="flex-row">
                    <div class="silo-container">{A_L}</div>
                    <div class="silo-container">{A_R}</div>
                </div>
            </div>

            <div class="silo-group">
                <div class="silo-title">싸이로 B</div>
                <div class="flex-row">
                    <div class="silo-container">{B_L}</div>
                    <div class="silo-container">{B_R}</div>
                </div>
            </div>
        </div>
        """, height=1600)  # 높이를 1600으로 대폭 늘렸습니다!
    except Exception as e:
        st.error(f"오류 발생: {e}")
