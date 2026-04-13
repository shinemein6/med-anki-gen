import streamlit as st
import fitz  # PyMuPDF
import genanki
import os
import uuid
import time

# [설정] 페이지 설정은 반드시 가장 처음에 와야 합니다.
st.set_page_config(page_title="CMC 안키 생성기", layout="centered")

# 1. 독립 모델 설정 (ID: 20260413105)
# 사용자님의 5개 필드 구성을 반영하되, 기존 데이터 보호를 위해 독립 ID 사용
IO_MODEL = genanki.Model(
    20260413105,
    'Med_Anki_Manual_Sync',
    fields=[
        {'name': 'Occlusion'},    # 1. 상자 정보
        {'name': 'Image'},        # 2. 이미지
        {'name': 'Header'},       # 3. 제목 (출처 제거를 위해 공백 유지)
        {'name': 'Back Extra'},   # 4. 뒷면 추가 설명
        {'name': 'Comments'},     # 5. 메모 (출처 정보를 여기에 숨김)
    ],
    templates=[
        {
            'name': 'Image Occlusion Card',
            'qfmt': '<div id="io-wrapper">{{Image}}</div>',
            'afmt': '{{FrontSide}}<hr>{{Back Extra}}<br><div style="color:gray; font-size:0.8em;">{{Comments}}</div>',
        },
    ],
    css=".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; } img { max-width: 100%; height: auto; }"
)

st.title("🩺 CMC 하이패스 안키 생성기")
st.markdown("---")
st.info("PDF를 업로드하면 출처가 제거된 깔끔한 안키 덱을 생성합니다.")

uploaded_file = st.file_uploader("강의록 PDF 파일 선택", type="pdf")

if uploaded_file:
    try:
        with st.spinner('카드를 조립하고 있습니다...'):
            # PDF 읽기
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            base_name = os.path.splitext(uploaded_file.name)[0]
            
            # 덱 생성 (시간 기반 ID로 충돌 방지)
            deck_id = int(time.time()) % 10**10
            my_deck = genanki.Deck(deck_id, base_name)
            media_files = []
            
            for i in range(len(doc)):
                page = doc.load_page(i)
                # 고해상도 이미지 추출 (이미지 가리기용)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                
                # 파일명 생성
                img_filename = f"img_{uuid.uuid4().hex[:8]}.png"
                pix.save(img_filename)
                media_files.append(img_filename)
                
                # 노트 생성 (Header는 비워서 출처 노출 방지)
                note = genanki.Note(
                    model=IO_MODEL,
                    fields=[
                        str(uuid.uuid4()), 
                        f'<img src="{img_filename}">', 
                        "", 
                        "", 
                        f"출처: {base_name} - P.{i+1}"
                    ]
                )
                my_deck.add_note(note)
                
            # 패키지 생성
            output_filename = "anki_bundle.apkg"
            package = genanki.Package(my_deck)
            package.media_files = media_files
            package.write_to_file(output_filename)
            
            # 다운로드 버튼 생성
            with open(output_filename, "rb") as f:
                st.download_button(
                    label="📥 안키 덱 다운로드",
                    data=f,
                    file_name=f"{base_name}_Ready.apkg",
                    mime="application/octet-stream"
                )
            
            # 임시 파일 정리
            for f in media_files:
                if os.path.exists(f): os.remove(f)
            if os.path.exists(output_filename): os.remove(output_filename)
            
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
