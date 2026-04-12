# 1. 안키 순정 Image Occlusion 양식과 동일하게 필드 구성
model_id = 1607392319
my_model = genanki.Model(
    model_id,
    'Image Occlusion', # 이름을 안키 기본형과 일치시킴
    fields=[
        {'name': 'ID (Hidden)'}, # 안키 내부 식별용
        {'name': 'Image'},       # 실제 강의록 이미지 [cite: 17]
        {'name': 'Header'},      # 제목 (예: Ch 8) 
        {'name': 'Footer'},
        {'name': 'Occlusions (JSON)'}, # 상자 정보가 저장될 곳
    ],
    templates=[{
        'name': 'Image Occlusion',
        'qfmt': '{{Image}}',
        'afmt': '{{Image}}<hr>{{Header}}',
    }]
)

# ... 중략 ...

# 카드 생성 시 빈 필드값 채워주기
my_note = genanki.Note(
    model=my_model, 
    fields=[str(uuid.uuid4()), f'<img src="{img_name}">', deck_name, '', '']
)
