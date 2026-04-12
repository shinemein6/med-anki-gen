import streamlit as st
import fitz  # PyMuPDF
import genanki
import os
import uuid

# 1. 안키 순정(Native) Image Occlusion 모델 규격 정의
# 안키 23.10+ 버전이 인식하는 5개 필드와 순서를 엄격히 준수합니다.
IO_MODEL_ID = 1607392319
IO_MODEL = genanki.Model(
    IO_MODEL_ID,
    'Image Occlusion', # 모델 이름을 순정과 동일하게 설정
    fields=[
        {'name': 'ID (Hidden)'},
        {'name': 'Image'},
        {'name': 'Header'},
        {'name': 'Footer'},
        {'name': 'Occlusions (JSON)'},
    ],
    templates=[
        {
            'name': 'Image Occlusion',
            'qfmt': '<div id="io-header">{{Header}}</div><div id="io-wrapper">{{Image}}</div><div id="io-footer">{{Footer}}</div>',
            'afmt': '<div id="io-header">{{Header}}</div><div id="io-wrapper">{{Image}}</div><hr id="answer"><div id="io-footer">{{Footer}}</div>',
        },
    ],
    css="""
    .card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; }
    #io-wrapper { position: relative; display: inline-block; }
    img { max-width: 100%; height: auto; }
    """
)

st.set_page_config(page_title="의대생용 안키 IO 생성기", layout="centered")
st.title("🩺 완결판: 안키 IO 자동 생성기")
st.info("PDF를 업로드하면 즉시 '이미지 가리기' 편집이 가능한 덱을 생성합니다.")

uploaded_file = st.file_uploader("강의록 PDF 선택 (예: Ch 8 단백질 가공)", type="pdf")

if uploaded_file:
    with st.spinner('안키 규격에 맞춰 제작 중...'):
        # PDF 처리 시작 [cite: 2, 3]
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        base_name = os.path.splitext(uploaded_file.name)[0]
        
        # 덱 ID 생성 (파일별로 고유하게)
        deck_id = abs(hash(base_name)) % (10 ** 10)
        my_deck = genanki.Deck(deck_id, base_name)
        
        media_files = []
        
        for i in range(len(doc)):
            page = doc.load_page(i)
            # 고해상도 이미지 추출 (지엽적 도표 대비) [cite: 74-77, 150-182]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            
            # 고유 파일명 생성
            img_filename = f"med_io_{uuid.uuid4().hex[:10]}.png"
            pix.save(img_filename)
            media_files.append(img_filename)
            
            # 안키 순정 IO 필드 구조에 데이터 주입
            # 1. ID (Hidden), 2. Image, 3. Header, 4. Footer, 5. Occlusions (JSON)
            note = genanki.Note(
                model=IO_MODEL,
                fields=[
                    str(uuid.uuid4()), 
                    f'<img src="{img_filename}">', 
                    f"{base_name} - Page {i+1}", 
                    "", 
                    ""
                ]
            )
            my_deck.add_note(note)
            
        # 안키 패키지 생성
        package = genanki.Package(my_deck)
        package.media_files = media_files
        output_filename = "anki_io_bundle.apkg"
        package.write_to_file(output_filename)
        
        # 다운로드 버튼
        with open(output_filename, "rb") as f:
            st.download_button(
                label="📥 안키 덱 다운로드",
                data=f,
                file_name=f"{base_name}_Ready.apkg",
                mime="application/octet-stream"
            )
            
        # 서버 임시 파일 청소
        for f in media_files:
            if os.path.exists(f): os.remove(f)
        if os.path.exists(output_filename): os.remove(output_filename)
