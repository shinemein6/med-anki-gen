import streamlit as st
import fitz  # PyMuPDF
import genanki
import os
import uuid
import time

# 1. 안전한 독립 모델 설정 (기존 데이터와 충돌 방지)
# 사용자님의 5개 필드 구성을 반영하되, ID는 독립적으로 가져갑니다.
MODEL_ID = 20260413105 
MODEL_NAME = "Med_Anki_Manual_Sync"

IO_MODEL = genanki.Model(
    MODEL_ID,
    MODEL_NAME,
    fields=[
        {'name': 'Occlusion'},    # 1. 상자 정보
        {'name': 'Image'},        # 2. 이미지
        {'name': 'Header'},       # 3. 제목 (출처 삭제를 위해 비워둘 예정)
        {'name': 'Back Extra'},   # 4. 뒷면 추가 설명
        {'name': 'Comments'},     # 5. 메모 (여기에 출처 정보를 숨김)
    ],
    templates=[
        {
            'name': 'Image Occlusion Card',
            # 전면에 출처(Header)를 표시하지 않도록 Image만 배치
            'qfmt': '<div id="io-wrapper">{{Image}}</div>',
            'afmt': '{{FrontSide}}<hr>{{Back Extra}}<br><div style="color:gray; font-size:0.8em;">{{Comments}}</div>',
        },
    ],
    css=".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; } img { max-width: 100%; height: auto; }"
)

st.set_page_config(page_title="CMC 하이패스 생성기 (출처 제거판)")
st.title("🩺 수동 동기화용 안키 생성기")
st.markdown("""
### 🚀 워크플로우 (10초 루틴)
1. **변환:** PDF를 올려 `.apkg` 파일을 만듭니다.
2. **가져오기:** 안키에서 파일을 가져옵니다.
3. **유형 변경:** 탐색 창에서 전체 선택(`Ctrl+A`) 후, **기존의 [Image Occlusion]**으로 유형을 변경하세요.
""")

uploaded_file = st.file_uploader("강의록 PDF 선택", type="pdf")

if uploaded_file:
    with st.spinner('출처 정보를 정리하며 카드를 조립 중입니다...'):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        base_name = os.path.splitext(uploaded_file.name)[0]
        
        # 덱 ID 생성
        deck_id = int(time.time()) % 10**10
        my_deck = genanki.Deck(deck_id, base_name)
        media_files = []
        
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            
            img_filename = f"med_{uuid.uuid4().hex[:8]}.png"
            pix.save(img_filename)
            media_files.append(img_filename)
            
            # 필드 주입 전략
            # - Header: 비워둠 (출처 표시 제거)
            # - Comments: 파일명과 페이지 정보를 여기에 저장
            note = genanki.Note(
                model=IO_MODEL,
                fields=[
                    str(uuid.uuid4()),            # 1. Occlusion
                    f'<img src="{img_filename}">', # 2. Image
                    "",                            # 3. Header (비움)
                    "",                            # 4. Back Extra
                    f"출처: {base_name} - P.{i+1}"   # 5. Comments
                ]
            )
            my_deck.add_note(note)
            
        package = genanki.Package(my_deck)
        package.media_files = media_files
        output_filename = "anki_ready.apkg"
        package.write_to_file(output_filename)
        
        with open(output_filename, "rb") as f:
            st.download_button("📥 안키 덱 다운로드", f, file_name=f"{base_name}_Manual.apkg")
            
        for f in media_files:
            if os.path.exists(f): os.remove(f)
uploaded_file = st.file_uploader("강의록 PDF 선택", type="pdf")

if uploaded_file:
    with st.spinner('안전한 독립 통로로 카드를 제작 중입니다...'):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        base_name = os.path.splitext(uploaded_file.name)[0]
        
        # 덱 ID 생성
        my_deck = genanki.Deck(abs(hash(base_name)) % (10 ** 10), base_name)
        media_files = []
        
        for i in range(len(doc)):
            page = doc.load_page(i)
            # 고해상도 처리 (Matrix 2, 2로 선명도 유지)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            
            img_filename = f"med_auto_{uuid.uuid4().hex[:10]}.png"
            pix.save(img_filename)
            media_files.append(img_filename)
            
            # 5개 필드에 데이터 주입
            note = genanki.Note(
                model=IO_MODEL,
                # Occlusion 필드에 임시 cloze 태그를 넣어 에러를 방지하고 편집기를 유도합니다.
                fields=[
                    "{{c1::}}",                   # 1. Occlusion (빈칸 태그 미리 주입)
                    f'<img src="{img_filename}">', # 2. Image
                    f"{base_name} - P.{i+1}",      # 3. Header
                    "",                            # 4. Back Extra
                    ""                             # 5. Comments
                ]
            )
            my_deck.add_note(note)
            
        package = genanki.Package(my_deck)
        package.media_files = media_files
        output_filename = "anki_oneshot_ready.apkg"
        package.write_to_file(output_filename)
        
        with st.container():
            st.success("시스템 동기화 완료! 이제 안심하고 사용하세요.")
            with open(output_filename, "rb") as f:
                st.download_button("📥 하이패스 안키 덱 다운로드", f, file_name=f"{base_name}_OneShot.apkg")
            
        # 서버 임시 파일 청소
        for f in media_files:
            if os.path.exists(f): os.remove(f)
        if os.path.exists(output_filename): os.remove(output_filename)

st.divider()
st.caption("CMC 본과 생활의 든든한 파트너가 되길 바랍니다.")
