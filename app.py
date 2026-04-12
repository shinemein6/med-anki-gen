import streamlit as st
import fitz  # PyMuPDF
import genanki
import os
import uuid

# 1. 안전한 독립 모델 설정 (기존 데이터와 충돌 방지)
# 기존 ID(1740...) 대신 새로운 고유 ID를 부여하여 시스템을 격리합니다.
NEW_SAFE_MODEL_ID = 20260413002 
NEW_MODEL_NAME = "Med_Anki_IO_Independent"

IO_MODEL = genanki.Model(
    NEW_SAFE_MODEL_ID,
    NEW_MODEL_NAME,
    fields=[
        {'name': 'Occlusion'},    # 1. 상자 좌표 및 고유 식별자
        {'name': 'Image'},        # 2. 강의록 이미지
        {'name': 'Header'},       # 3. 제목 (파일명 + 페이지)
        {'name': 'Back Extra'},   # 4. 뒷면 추가 정보
        {'name': 'Comments'},     # 5. 기타 메모
    ],
    templates=[
        {
            'name': 'Image Occlusion Card',
            'qfmt': '<div id="io-header">{{Header}}</div><div id="io-wrapper">{{Image}}</div>',
            'afmt': '<div id="io-header">{{Header}}</div><div id="io-wrapper">{{Image}}</div><hr>{{Back Extra}}<br>{{Comments}}',
        },
    ],
    css=".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; } #io-wrapper { position: relative; display: inline-block; } img { max-width: 100%; height: auto; }"
)

st.set_page_config(page_title="CMC 본과생용 안전 IO 생성기", layout="centered")
st.title("🩺 안전 독립형: 안키 IO 생성기")
st.markdown("""
### ⚠️ 사용 전 확인사항
1. **데이터 복구:** 기존 카드의 편집 버튼이 사라졌다면, PC 안키의 **[파일] -> [사용자 프로필 전환] -> [백업 열기]**에서 오늘 이전 시점으로 복구하세요.
2. **독립 운영:** 이 코드는 기존 양식을 덮어씌우지 않고 별도의 `{NEW_MODEL_NAME}` 유형을 생성하므로 안전합니다.
""")

uploaded_file = st.file_uploader("강의록 PDF 선택", type="pdf")

if uploaded_file:
    with st.spinner('새로운 안전 통로로 카드를 조립 중입니다...'):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        base_name = os.path.splitext(uploaded_file.name)[0]
        
        # 덱 생성 (파일명 기반 고유 ID)
        my_deck = genanki.Deck(abs(hash(base_name)) % (10 ** 10), base_name)
        media_files = []
        
        for i in range(len(doc)):
            page = doc.load_page(i)
            # 고해상도 처리 (이미지 가리기 시 텍스트 가독성 확보)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            
            # 고유 이미지 파일명 생성
            img_filename = f"med_safe_{uuid.uuid4().hex[:10]}.png"
            pix.save(img_filename)
            media_files.append(img_filename)
            
            # 사용자님의 5개 필드 순서에 데이터 주입
            note = genanki.Note(
                model=IO_MODEL,
                fields=[
                    str(uuid.uuid4()),            # 1. Occlusion (임시 ID 부여)
                    f'<img src="{img_filename}">', # 2. Image
                    f"{base_name} - P.{i+1}",      # 3. Header
                    "",                            # 4. Back Extra
                    ""                             # 5. Comments
                ]
            )
            my_deck.add_note(note)
            
        # 안키 패키지(.apkg) 생성
        package = genanki.Package(my_deck)
        package.media_files = media_files
        output_filename = "anki_safe_bundle.apkg"
        package.write_to_file(output_filename)
        
        with st.container():
            st.success(f"총 {len(doc)}장의 카드가 생성되었습니다!")
            with open(output_filename, "rb") as f:
                st.download_button(
                    label="📥 안전 덱 다운로드",
                    data=f,
                    file_name=f"{base_name}_Independent.apkg",
                    mime="application/octet-stream"
                )
            
        # 임시 이미지 및 패키지 삭제
        for f in media_files:
            if os.path.exists(f): os.remove(f)
        if os.path.exists(output_filename): os.remove(output_filename)

st.divider()
st.caption("본 도구는 CMC 의대생의 효율적인 암기 학습(Anki IO)을 돕기 위해 설계되었습니다.")
