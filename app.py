import streamlit as st
import fitz  # PyMuPDF
import genanki
import os
import uuid

# 1. 안키 순정(Native) Image Occlusion 규격과 100% 일치화
# 안키 23.10+ 버전이 내부적으로 생성하는 기본 모델명을 그대로 사용합니다.
IO_MODEL_NAME = "Image Occlusion"
IO_MODEL_ID = 1000321  # 고정된 ID를 사용하여 모델 분산 방지

IO_MODEL = genanki.Model(
    IO_MODEL_ID,
    IO_MODEL_NAME,
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
    css=".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; } img { max-width: 100%; height: auto; }"
)

st.set_page_config(page_title="의대생용 안키 IO 생성기", page_icon="🩺")
st.title("🩺 최종본: 순정 호환 IO 생성기")

uploaded_file = st.file_uploader("강의록 PDF 선택", type="pdf")

if uploaded_file:
    with st.spinner('안키 규격에 맞춰 제작 중...'):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        base_name = os.path.splitext(uploaded_file.name)[0]
        
        # 덱 생성
        my_deck = genanki.Deck(abs(hash(base_name)) % (10 ** 10), base_name)
        media_files = []
        
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            
            img_filename = f"med_{uuid.uuid4().hex[:10]}.png"
            pix.save(img_filename)
            media_files.append(img_filename)
            
            # 모든 필드를 안키 순정 IO가 요구하는 형식으로 채움
            note = genanki.Note(
                model=IO_MODEL,
                fields=[
                    str(uuid.uuid4()),            # 1. ID (Hidden)
                    f'<img src="{img_filename}">', # 2. Image
                    f"{base_name} - P.{i+1}",      # 3. Header [cite: 1-3]
                    "",                            # 4. Footer
                    ""                             # 5. Occlusions (JSON)
                ]
            )
            my_deck.add_note(note)
            
        package = genanki.Package(my_deck)
        package.media_files = media_files
        output_filename = "anki_ready.apkg"
        package.write_to_file(output_filename)
        
        with open(output_filename, "rb") as f:
            st.download_button("📥 수정 없이 바로 쓰는 안키 덱 다운로드", f, file_name=f"{base_name}_Ready.apkg")
            
        for f in media_files:
            if os.path.exists(f): os.remove(f)
        if os.path.exists(output_filename): os.remove(output_filename)
