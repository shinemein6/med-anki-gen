import streamlit as st
import fitz  # PyMuPDF
import genanki
import os
import uuid

# 1. 사용자님 안키 고유 정보 (Model ID & Fields)
# 확인하신 ID와 5개 필드 구성을 엄격히 준수합니다.
IO_MODEL_ID = 1740279848975 
IO_MODEL = genanki.Model(
    IO_MODEL_ID,
    'Image Occlusion', # 안키 내 모델 이름
    fields=[
        {'name': 'Occlusion'},    # 1번: 상자 정보(JSON) 및 고유 식별자
        {'name': 'Image'},        # 2번: 강의록 이미지
        {'name': 'Header'},       # 3번: 제목 및 페이지
        {'name': 'Back Extra'},   # 4번: 뒷면 추가 설명
        {'name': 'Comments'},     # 5번: 기타 메모
    ],
    templates=[
        {
            'name': 'Image Occlusion',
            'qfmt': '<div id="io-header">{{Header}}</div><div id="io-wrapper">{{Image}}</div>',
            'afmt': '<div id="io-header">{{Header}}</div><div id="io-wrapper">{{Image}}</div><hr>{{Back Extra}}<br>{{Comments}}',
        },
    ],
    css=".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; } img { max-width: 100%; height: auto; }"
)

st.set_page_config(page_title="CMC 본과생 전용 IO 생성기", layout="centered")
st.title("🩺 하이패스: 100% 동기화 생성기")
st.success(f"현재 설정된 모델 ID: {IO_MODEL_ID}")

uploaded_file = st.file_uploader("강의록 PDF 선택", type="pdf")

if uploaded_file:
    with st.spinner('사용자님의 안키 양식에 맞춰 카드를 제작 중입니다...'):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        base_name = os.path.splitext(uploaded_file.name)[0]
        
        # 덱 생성 (충돌 방지를 위해 파일명 기반 ID 생성)
        my_deck = genanki.Deck(abs(hash(base_name)) % (10 ** 10), base_name)
        media_files = []
        
        for i in range(len(doc)):
            page = doc.load_page(i)
            # 고해상도 처리 (이미지 가리기 시 디테일 확보)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            
            img_filename = f"med_io_{uuid.uuid4().hex[:10]}.png"
            pix.save(img_filename)
            media_files.append(img_filename)
            
            # 사용자님의 5개 필드 순서에 맞춰 데이터 주입
            # 1. Occlusion: 고유 ID 부여 (중복 방지용)
            # 2. Image: <img> 태그
            # 3. Header: 강의록 이름과 페이지
            # 4. Back Extra: 빈칸
            # 5. Comments: 빈칸
            note = genanki.Note(
                model=IO_MODEL,
                fields=[
                    str(uuid.uuid4()),            # 1. Occlusion
                    f'<img src="{img_filename}">', # 2. Image
                    f"{base_name} - P.{i+1}",      # 3. Header
                    "",                            # 4. Back Extra
                    ""                             # 5. Comments
                ]
            )
            my_deck.add_note(note)
            
        # 패키징 및 파일 생성
        package = genanki.Package(my_deck)
        package.media_files = media_files
        output_filename = "anki_sync_ready.apkg"
        package.write_to_file(output_filename)
        
        with open(output_filename, "rb") as f:
            st.download_button("📥 즉시 편집 가능 덱 다운로드", f, file_name=f"{base_name}_Ready.apkg")
            
        # 임시 파일 삭제
        for f in media_files:
            if os.path.exists(f): os.remove(f)
        if os.path.exists(output_filename): os.remove(output_filename)
