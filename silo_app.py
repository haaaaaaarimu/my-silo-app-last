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

# --- [웹 화면 구성] ---
st.set_page_config(layout="wide", page_title="싸이로 재고 현황")

st.markdown("<h1 style='text-align: center;'>🌾 실시간 싸이로 재고 현황판</h1>", unsafe_allow_html=True)

raw_data = st.text_area("📋 엑셀 데이터 붙여넣기", height=100)

if raw_data.strip():
    try:
        df = pd.read_csv(io.StringIO(raw_data), sep='\t', names=['장치장', '곡종', '재고량'], header=None)
        
        A_L = make_block("A", 201, 101, df)
        A_R = make_block("A", 207, 107, df)
        B_L = make_block("B", 201, 101, df)
        B_R = make_block("B", 207, 107, df)

        st.components.v1.html(f"""
        <style>
            /* 전체 배경 및 정렬 */
            body {{ margin: 0; background-color: #f4f7f6; }}
            .main-wrapper {{ 
                display: flex; flex-direction: column; align-items: center; 
                width: 100%; padding: 20px; box-sizing: border-box;
            }}
            
            /* 싸이로 그룹 (A/B) */
            .silo-group {{ 
                margin-bottom: 60px; text-align: center; 
                display: flex; flex-direction: column; align-items: center;
            }}
            .group-title {{ 
                font-size: 32px; font-weight: bold; margin-bottom: 20px; color: #2c3e50;
                border-bottom: 4px solid #74c934; padding-bottom: 5px; width: fit-content;
            }}

            /* 좌우 배치 컨테이너 */
            .side-by-side {{ 
                display: flex; gap: 30px; justify-content: center; align-items: flex-start;
            }}

            /* 개별 싸이로 박스 */
            .silo-container {{ 
                position: relative; width: 750px; height: 480px; 
                border: 3px solid #333; background: #fff; 
                border-radius: 10px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
                overflow: hidden; flex-shrink: 0;
            }}

            /* 내부 그리드 및 아이템 스타일 */
            .rect-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); width: 100%; height: 320px; }}
            .rect-item {{ border: 0.5px solid #eee; position: relative; }}
            .circle-overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }}
            .circle-item {{ 
                position: absolute; width: 95px; height: 95px; border-radius: 50%; 
                border: 2px solid #000; background: #fff; display: flex; 
                align-items: center; justify-content: center; transform: translate(-50%, -50%); 
                pointer-events: auto; transition: 0.2s; z-index: 5;
            }}
            .circle-item:hover {{ transform: translate(-50%, -50%) scale(1.1); z-index: 50; box-shadow: 0 0 15px rgba(0,0,0,0.3); }}
            
            /* 텍스트 및 툴팁 */
            .text-box {{ display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; height: 100%; cursor: pointer; }}
            .text-box::after {{
                content: "📍 " attr(data-code) "\\A🌾 " attr(data-name) "\\A📦 " attr(data-qty) "t";
                white-space: pre; position: absolute; bottom: 120%; left: 50%; transform: translateX(-50%);
                background: rgba(44, 62, 80, 0.95); color: white; padding: 10px; border-radius: 6px; font-size: 13px;
                opacity: 0; visibility: hidden; transition: 0.2s; z-index: 100; width: 100px; line-height: 1.4;
            }}
            .text-box:hover::after {{ opacity: 1; visibility: visible; }}
            
            .p-name {{ font-size: 14px; font-weight: bold; }}
            .p-qty {{ font-size: 13px; font-weight: bold; }}
            .p-code {{ font-size: 10px; color: #7f8c8d; }}
        </style>

        <div class="main-wrapper">
            <div class="silo-group">
                <div class="group-title">SILO A</div>
                <div class="side-by-side">
                    <div class="silo-container">{A_L}</div>
                    <div class="silo-container">{A_R}</div>
                </div>
            </div>

            <div class="silo-group">
                <div class="group-title">SILO B</div>
                <div class="side-by-side">
                    <div class="silo-container">{B_L}</div>
                    <div class="silo-container">{B_R}</div>
                </div>
            </div>
        </div>
        """, height=1250)
    except Exception as e:
        st.error(f"데이터 에러: {e}")
