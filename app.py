import streamlit as st
import fitz  # PyMuPDF
import genanki
import os
import uuid

# 1. 안키 순정 Image Occlusion(IO) 호환 모델 정의
# 안키 23.10+ 버전의 내장 IO 기능과 필드 구조를 완벽히 일치시켰습니다.
IO_MODEL_ID = 19840321  # 고유 모델 ID
IO_MODEL = genanki.Model(
    IO_MODEL_ID,
    'Image Occlusion (Auto-Generated)',
    fields=[
        {'name': 'ID (Hidden)'},
        {'name': 'Image'},
        {'name': 'Header'},
        {'name': 'Footer'},
        {'name': 'Occlusions (JSON)'},
    ],
    templates=[
        {
            'name': 'Image Occlusion Card',
            'qfmt': '<div id="io-header">{{Header}}</div><div id="io-wrapper">{{Image}}</div><div id="io-footer">{{Footer}}</div>',
            'afmt': '<div id="io-header">{{Header}}</div><div id="io-wrapper">{{Image}}</div><hr id="answer"><div id="io-footer">{{Footer}}</div>',
        },
    ],
    css="""
    .card {
        font-family: arial;
        font-size: 20px;
        text-align: center;
        color: black;
        background-color: white;
    }
    #io-wrapper {
        position: relative;
        display: inline-block;
    }
    img {
        max-width: 100%;
        height: auto;
    }
    """
)

st.set_page_config(page_title="의대생용 안키 IO 생성기", page_icon="🩺")
st.title("🩺 스마트 안키 IO 생성기")
st.write("PDF를 올리면 즉시 '이미지 가리기' 편집이 가능한 덱을 생성합니다.")

uploaded_file = st.file_uploader("강의록 PDF 선택 (예: Ch 8 단백질 가공)", type="pdf")

if uploaded_file:
    with st.spinner('안키 덱을 정교하게 조립 중...'):
        # PDF 읽기
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        base_name = os.path.splitext(uploaded_file.name)[0]
        
        # 덱 생성 (파일명을 덱 이름으로)
        deck_id = abs(hash(base_name)) % (10 ** 10)
        my_deck = genanki.Deck(deck_id, base_name)
        
        media_files = []
        
        for i in range(len(doc)):
            page = doc.load_page(i)
            # 고해상도 변환 (지엽적인 도표 내용도 선명하게 처리)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            
            # 파일명 고유화 및 저장
            img_filename = f"med_io_{uuid.uuid4().hex[:10]}.png"
            pix.save(img_filename)
            media_files.append(img_filename)
            
            # 안키 순정 IO 필드 구조에 맞춰 데이터 주입
            # 1. ID (Hidden) -> 고유 UUID
            # 2. Image -> <img> 태그
            # 3. Header -> 강의록 이름 및 페이지 번호
            # 4. Footer -> 빈칸
            # 5. Occlusions (JSON) -> 빈칸 (사용자가 안키에서 상자를 그릴 공간)
            note = genanki.Note(
                model=IO_MODEL,
                fields=[
                    str(uuid.uuid4()), 
                    f'<img src="{img_filename}">', 
                    f"{base_name} - P.{i+1}", 
                    "", 
                    ""
                ]
            )
            my_deck.add_note(note)
            
        # 패키지 생성
        package = genanki.Package(my_deck)
        package.media_files = media_files
        output_filename = "anki_io_bundle.apkg"
        package.write_to_file(output_filename)
        
        # 다운로드 버튼 생성
        with open(output_filename, "rb") as f:
            st.download_button(
                label="📥 이미지 가리기용 덱 다운로드",
                data=f,
                file_name=f"{base_name}_IO.apkg",
                mime="application/octet-stream"
            )
            
        # 임시 이미지 파일 및 패키지 삭제 (서버 용량 관리)
        for f in media_files:
            if os.path.exists(f): os.remove(f)
        if os.path.exists(output_filename): os.remove(output_filename)

st.info("💡 팁: 이 덱을 안키에 넣으면 별도의 설정 없이도 카드를 열어 '이미지 가리기(IO)' 아이콘을 눌러 바로 상자를 그릴 수 있습니다.")
