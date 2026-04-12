import streamlit as st
import fitz
import genanki
import os
import uuid

# 안키 23.10+ 순정 IO 모델의 표준 규격
# 모델 이름을 'Image Occlusion'으로 하되, 
# 기존 모델과 충돌 시 '유형 변경'을 최소화하도록 필드와 템플릿을 표준화합니다.
IO_MODEL = genanki.Model(
    1000321, # 이 ID는 순정 IO와 가장 잘 호환되는 범용 ID입니다.
    'Image Occlusion',
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
    css=".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; } #io-wrapper { position: relative; display: inline-block; } img { max-width: 100%; height: auto; }"
)

# ... (이후 덱 생성 및 노트 추가 로직은 동일)
