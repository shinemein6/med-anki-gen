import streamlit as st
import fitz  # PyMuPDF
import genanki
import os
import uuid

# 1. 안전한 독립 고유 ID (기존 시스템 보호를 위해 새로운 번호 부여)
# 이 번호는 기존 ID와 다르므로 절대 기존 데이터를 건드리지 않습니다.
FINAL_AUTO_MODEL_ID = 2026041399 

# 2. '원샷' 가리기 편집 활성화 모델 정의
IO_MODEL = genanki.Model(
    FINAL_AUTO_MODEL_ID,
    'Image_Occlusion_OneShot',  # 독립된 유형 이름
    fields=[
        {'name': 'Occlusion'},    # 1. 상자 정보 필드 ({{cloze:Occlusion}} 역할)
        {'name': 'Image'},        # 2. 강의록 이미지
        {'name': 'Header'},       # 3. 제목
        {'name': 'Back Extra'},   # 4. 뒷면 설명
        {'name': 'Comments'},     # 5. 메모
    ],
    templates=[
        {
            'name': 'Image Occlusion Card',
            # qfmt에 cloze:Occlusion을 넣어야 안키가 IO 편집기를 활성화합니다.
            'qfmt': '<div id="io-header">{{Header}}</div><div id="io-wrapper">{{cloze:Occlusion}}{{Image}}</div>',
            'afmt': '<div id="io-header">{{Header}}</div><div id="io-wrapper">{{cloze:Occlusion}}{{Image}}</div><hr>{{Back Extra}}<br>{{Comments}}',
        },
    ],
    css=".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; } #io-wrapper { position: relative; display: inline-block; } img { max-width: 100%; height: auto; }",
    model_type=genanki.Model.CLOZE  # ★핵심: 빈칸 넣기 유형으로 지정하여 편집 버튼 활성화
)

st.set_page_config(page_title="CMC 하이패스 안키 생성기", layout="centered")
st.title("🩺 원샷: 이미지 가리기 자동 생성기")
st.info("이 도구는 유형 변경 없이 가져오기 즉시 편집이 가능하도록 설계되었습니다.")

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
