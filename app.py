import streamlit as st
import requests
import base64
import time
import json
import uuid
from PIL import Image, ImageOps
from io import BytesIO
import html

st.set_page_config(
    page_title="CEO Talk Plus",
    page_icon="🌿",
    layout="centered"
)
def upload_file_to_github(file_bytes, path, message):
    repo = st.secrets["GITHUB_REPO"]
    token = st.secrets["GITHUB_TOKEN"]

    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    content = base64.b64encode(file_bytes).decode("utf-8")

    data = {
        "message": message,
        "content": content
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.put(url, json=data, headers=headers)

    if response.status_code not in [200, 201]:
        st.error(
            f"GitHub 업로드 실패\n"
            f"상태코드 : {response.status_code}\n"
            f"내용 : {response.text[:500]}"
        )

    return response.status_code in [200, 201]


def get_photo_items_from_github():
    repo = st.secrets["GITHUB_REPO"]
    token = st.secrets["GITHUB_TOKEN"]

    url = f"https://api.github.com/repos/{repo}/contents/photos"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return []

    files = response.json()
    file_map = {f["name"]: f for f in files}

    photo_items = []

    for file in files:
        name = file["name"]

        if name.lower().endswith((".jpg", ".jpeg", ".png")):
            base_name = name.rsplit(".", 1)[0]
            meta_name = f"{base_name}.json"

            uploader = "작성자 미입력"
            comment = "소감 미입력"

            if meta_name in file_map:
                meta_response = requests.get(file_map[meta_name]["download_url"])
                if meta_response.status_code == 200:
                    meta = meta_response.json()
                    uploader = meta.get("uploader", uploader)
                    comment = meta.get("comment", comment)

            photo_items.append({
                "filename": name,
                "image_url": file["download_url"],
                "uploader": uploader,
                "comment": comment
            })

    return photo_items


def compress_image(uploaded_file, max_width=1000, quality=60):
    try:
        image = Image.open(uploaded_file)
        image = ImageOps.exif_transpose(image)

        if image.mode != "RGB":
            image = image.convert("RGB")

        width, height = image.size

        if width > max_width:
            new_height = int(height * max_width / width)
            image = image.resize((max_width, new_height))

        buffer = BytesIO()
        image.save(
            buffer,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=True
        )

        return buffer.getvalue()

    except Exception as e:
        st.error(f"사진 변환 중 오류가 발생했습니다: {e}")
        return None
# =========================
# CSS
# =========================
st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 760px;
}

.hero-container {
    position: relative;
    margin-bottom: 20px;
    border-radius: 24px;
    overflow: hidden;
}

.hero-container img {
    width: 100%;
    height: 260px;
    object-fit: cover;
    display: block;
}

.hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        rgba(0,0,0,0.10),
        rgba(0,0,0,0.60)
    );
}

.hero-text {
    position: absolute;
    left: 28px;
    bottom: 30px;
    color: white;
}

.hero-title {
    font-size: 40px;
    font-weight: 800;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
}

.hero-sub {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 6px;
}

.hero-date {
    font-size: 16px;
    font-weight: 700;
}

.card {
    background: white;
    border: 1px solid #E7E7E7;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);

    color: #1F2937 !important;
}

.info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 0;
    border-bottom: 1px solid #EEEEEE;
}

.info-row-last {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 0;
}

.info-label {
    font-weight: 700;
    font-size: 16px;
}

.info-value {
    font-weight: 800;
    font-size: 18px;
    color: #1F2937;
    text-align: right;
}

.info-value-normal {
    font-weight: 700;
    font-size: 18px;
    text-align: right;
}

.small {
    color: #666;
    font-size: 14px;
    line-height: 1.6;
}

.tag {
    display: inline-block;
    background: #F3F3F3;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 13px;
    margin: 3px;
}

.timeline {
    border-left: 3px solid #A50020;
    padding-left: 16px;
    margin-left: 6px;
}

.timeline-item {
    margin-bottom: 18px;
}

.timeline-time {
    font-weight: 800;
    color: #A50020;
    font-size: 15px;
}

.timeline-title {
    font-weight: 800;
    font-size: 18px;
    margin-top: 3px;
}

.timeline-desc {
    color: #666;
    font-size: 14px;
    margin-top: 3px;
}

.group-title {
    font-weight: 800;
    font-size: 18px;
    color: #A50020;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# Hero
# =========================
st.markdown("""
<div class="hero-container">
<img src="https://raw.githubusercontent.com/chulhan11jang/CEO_Talk_Plus/main/gumi.jpeg">
<div class="hero-overlay"></div>
<div class="hero-text">
    <div class="hero-title">CEO Talk Plus</div>
    <div class="hero-sub">with 패키지솔루션</div>
    <div class="hero-date">2026.07.08 · 금오산 둘레길</div>
</div>
</div>
""", unsafe_allow_html=True)


# =========================
# Program Intro
# =========================
st.markdown("""
<div class="card">
    <h2 style="font-size:26px;">프로그램 소개</h2>
    <p><b>CEO와 함께하는 Talk Plus, 소통에 의미를 더하다</b></p>
    <p>
    CEO와 리더 간 직접적인 소통을 통해<br>
    조직의 방향성과 생각을 공유하는 자리입니다.
    </p>
</div>
""", unsafe_allow_html=True)


# =========================
# Main Tabs
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "집결 정보", "일정", "조 편성", "죽녹원", "석식"
])


# =========================
# Tab 1: 집결 정보
# =========================
with tab1:

    st.markdown("""
<div class="card">
<div class="info-row">
<div class="info-label">🚍 배차 정보</div>
<div class="info-value">광주77사 1911</div>
</div>
<div class="info-row">
<div class="info-label">📍 탑승 위치</div>
<div class="info-value-normal">정문 앞(ID카드 태깅 필요)</div>
</div>
<div class="info-row-last">
<div class="info-label">⏰ 집결 시간</div>
<div class="info-value"><span style="color:#DC2626; font-weight:700;">15:25</span>까지 탑승 완료</div>
</div>

<div style="
margin-top:12px;
padding-top:12px;
border-top:1px solid #EEEEEE;
font-size:14px;
color:#D97706;
font-weight:600;
">
☂️ 우천에 대비하여 우산을 지참해 주시기 바랍니다.
</div>
""", unsafe_allow_html=True)

# =========================
# Tab 2: 일정
# =========================
with tab2:
    st.markdown("""
<div class="card">
<div class="timeline">

<div class="timeline-item">
<div class="timeline-time">15:30</div>
<div class="timeline-title">광주 공장 출발</div>
<div class="timeline-desc">차량 탑승 및 인원 확인</div>
</div>

<div class="timeline-item">
<div class="timeline-time">16:00</div>
<div class="timeline-title">담양 종합체육관 주차장 도착</div>
<div class="timeline-desc">집결지 이동 및 조별 정렬</div>
</div>

<div class="timeline-item">
<div class="timeline-time">16:10</div>
<div class="timeline-title">프로그램 안내</div>
<div class="timeline-desc">세부내용 설명 및 단체사진 촬영</div>
</div>

<div class="timeline-item">
<div class="timeline-time">16:30</div>
<div class="timeline-title">조별 산책 출발</div>
<div class="timeline-desc">1조 출발 후 3~5분 간격으로 2·3조 출발</div>
</div>

<div class="timeline-item">
<div class="timeline-time">17:00</div>
<div class="timeline-title">Post Activity</div>
<div class="timeline-desc">목표달성 'Goal-In' 활동 진행</div>
</div>

<div class="timeline-item">
<div class="timeline-time">17:10</div>
<div class="timeline-title">조별 산책 출발</div>
<div class="timeline-desc">Activity 종료 후 1조부터 순차적 출발</div>
</div>

<div class="timeline-item">
<div class="timeline-time">18:00 ~ 20:00</div>
<div class="timeline-title">석식 및 소통</div>
<div class="timeline-desc">식사 및 행사 진행</div>
</div>

</div>
</div>
""", unsafe_allow_html=True)

# =========================
# Tab 3: 조 편성
# =========================
with tab3:
    groups = {
        "1조": ["유병국", "남형기", "김민규", "김형근", "김웅", "박창혁", "신기수", "장성덕", "조정민", "최낙주"],
        "2조": ["김진호", "강용호", "장용재", "권영철", "김성수", "문종인", "박갑동", "박석", "오영춘", "이재광", "정재희", "최영민"],
        "3조": ["이동훈", "유인수", "장승우", "백남산", "김성훈", "박무룡", "유기주", "유선수", "전희진", "조성재"],
    }

    for group, members in groups.items():

        first_line = " · ".join(members[:6])
        second_line = " · ".join(members[6:])

        st.markdown(
            f"""
<div class="card">
<b style="font-size:20px; color:#000000;">{group}</b><br><br>
{first_line}<br><br>{second_line}
</div>
""",
            unsafe_allow_html=True
        )

# =========================
# Tab 4: 죽녹원
# =========================
with tab4:
    sub1, sub2, sub3 = st.tabs([
        "산책 동선", "포토미션", "Activity"
    ])

with sub1:
    st.markdown("""
<div class="card">
<b>🌿 함께 걸으며</b><br><br>

CEO 및 리더들과 함께 걸으며<br>
<span style="color:#DC2626; font-weight:700;">자유롭게 생각을 나누는 시간</span>입니다.<br><br>

사업의 방향,<br>
조직 운영에 대한 고민,<br>
리더로서의 경험과 생각 등<br>
평상 시 <span style="color:#DC2626; font-weight:700;">함께 나누고 싶은 주제</span> 중심으로<br>
자유롭게 소통해 주시기 바랍니다.

</div>
""", unsafe_allow_html=True)

    st.image(
        "https://raw.githubusercontent.com/chulhan11jang/CEO_Talk_Plus/main/route.png",
        use_container_width=True
    )

    st.markdown("""
<div class="card">
<b>하차지점</b> : 담양 종합체육관 주차장<br>
<b>집결지</b> : 주차장 인근<br>
<b>단체사진 촬영</b> : 죽녹원 입구 인근<br>
<b>출발지</b> : 죽녹원 입구<br>
<b>Post</b> : 산책 중간 Activity 진행 지점
</div>
""", unsafe_allow_html=True)

with sub2:

    st.markdown("""
<div class="card">
<b>📸 오늘 함께한 순간을 기록해 주세요.</b><br><br>

함께 걷는 모습, 소통의 모습 등<br>
<span style="color:#DC2626; font-weight:700;">오늘의 현장감</span>과
<span style="color:#DC2626; font-weight:700;">즐거운 분위기</span>가 담긴 사진을<br>
자유롭게 업로드해 주시기 바랍니다.<br><br>

사진을 업로드해 주신 분들 중<br>
추첨을 통해 커피 쿠폰을 드립니다.
</div>
""", unsafe_allow_html=True)

    uploader_name = st.text_input("이름")
    photo_comment = st.text_input("한 줄 소감")

    uploaded_photo = st.file_uploader(
        "사진 업로드",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_photo is not None:
        if st.button("사진 업로드하기"):

            if not uploader_name.strip():
                st.warning("이름을 입력해 주세요.")

            elif not photo_comment.strip():
                st.warning("소감을 입력해 주세요.")

            else:
                photo_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
                photo_filename = f"{photo_id}.jpg"
                meta_filename = f"{photo_id}.json"

                compressed_photo = compress_image(uploaded_photo)

                photo_success = upload_file_to_github(
                    compressed_photo,
                    f"photos/{photo_filename}",
                    f"Upload photo {photo_filename}"
                )

                metadata = {
                    "uploader": uploader_name.strip(),
                    "comment": photo_comment.strip()
                }

                meta_success = upload_file_to_github(
                    json.dumps(metadata, ensure_ascii=False).encode("utf-8"),
                    f"photos/{meta_filename}",
                    f"Upload metadata {meta_filename}"
                )

                if photo_success and meta_success:
                    st.success("사진이 업로드되었습니다.")
                    st.rerun()
                else:
                    st.error("업로드에 실패했습니다. 관리자에게 문의해 주세요.")

    st.markdown("### 📷 업로드된 사진")

    photo_items = get_photo_items_from_github()

    if photo_items:
        gallery_html = """
<style>
.photo-modal {
display: none;
position: fixed;
z-index: 9999;
left: 0;
top: 0;
width: 100%;
height: 100%;
background: rgba(0,0,0,0.72);
padding: 42px 16px;
box-sizing: border-box;
overflow-y: auto;
}

.photo-modal:target {
display: block;
}

.photo-modal-card {
background: white;
border-radius: 20px;
padding: 14px;
max-width: 520px;
margin: 0 auto;
box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}

.photo-modal-card img {
width: 100%;
border-radius: 14px;
margin-bottom: 14px;
}

.photo-close {
float: right;
width: 34px;
height: 34px;
border-radius: 50%;
background: #E5E7EB;
color: #6B7280;
font-size: 24px;
font-weight: 800;
text-decoration: none;
line-height: 34px;
text-align: center;
}

.photo-name {
font-size: 22px;
font-weight: 800;
color: #1F2937;
margin-top: 10px;
}

.photo-comment {
font-size: 17px;
line-height: 1.5;
color: #1F2937;
margin-top: 8px;
}
</style>

<div id="gallery"></div>

<div style="
display:grid;
grid-template-columns:repeat(3, minmax(0, 1fr));
gap:8px;
width:100%;
">
"""

        for idx, item in enumerate(reversed(photo_items)):
            modal_id = f"photo_{idx}"
            image_url = item["image_url"]
            uploader_raw = item.get("uploader", "")
            comment_raw = item.get("comment", "")

            uploader = html.escape(uploader_raw) if uploader_raw not in ["작성자 미입력", ""] else ""
            comment = html.escape(comment_raw) if comment_raw not in ["소감 미입력", ""] else ""

            info_html = ""

            if uploader:
                info_html += f'<div class="photo-name">👤 {uploader}</div>'

            if comment:
                info_html += f'<div class="photo-comment">{comment}</div>'

            gallery_html += f"""
<div style="
width:100%;
aspect-ratio:1/1;
overflow:hidden;
border-radius:12px;
">
<a href="#{modal_id}" style="
display:block;
width:100%;
height:100%;
">
<img src="{image_url}" style="
width:100%;
height:100%;
object-fit:cover;
display:block;
">
</a>
</div>

<div id="{modal_id}" class="photo-modal">
<div class="photo-modal-card">
<a href="#gallery" class="photo-close">×</a>
<img src="{image_url}">
{info_html}
</div>
</div>
"""

        gallery_html += """
</div>

<div style="font-size:13px; color:#777; margin-top:8px;">
사진을 누르면 크게 볼 수 있습니다.
</div>
"""

        st.markdown(gallery_html, unsafe_allow_html=True)

    else:
        st.info("아직 업로드된 사진이 없습니다.")
        
with sub3:

    st.markdown("""
<div class="card">
<b>⚽ 목표 달성 'Goal-In'</b><br>

<ul>
<li>조별로 진행되는 가벼운 <span style="color:#DC2626; font-weight:700;">축구 게임</span>입니다.</li>
<li>조원 모두가 <span style="color:#DC2626; font-weight:700;">한 번의 기회</span>를 가지며<br>
    <span style="color:#DC2626; font-weight:700;">'골인' 성공 개수</span>로 점수를 획득합니다.</li>
<li>우리 조가 많은 '골인'을 할 수 있도록<br>
    열렬히 응원하며 목표에 도전합니다.</li>
</ul>

<b>🎯 Game Tip</b><br>

<ul>
<li><span style="color:#DC2626; font-weight:700;">발 안쪽의 넓은 부위</span>로 차면 보다 정확하게<br>
    찰 수 있습니다.</li>
<li>너무 강하게 차기보다 <span style="color:#DC2626; font-weight:700;">적당한 힘</span>으로<br>
    정확하게 차는 것이 중요합니다.</li>
<li><span style="color:#DC2626; font-weight:700;">공을 끝까지 바라보며</span> 차보세요.</li>
</ul>

<b>😊 참고해 주세요</b><br>

<li>본 활동은 <span style="color:#DC2626; font-weight:700;">정확도</span>와 <span style="color:#DC2626; font-weight:700;">집중력</span>이 필요합니다.</li>
<li><span style="color:#DC2626; font-weight:700;">누구나 한 번에 성공하기는 어렵습니다.</span></li>
<li>성공 여부와 관계없이 조원들과 함께 도전하고<br>
    응원하는 시간을 즐겨주시기 바랍니다.</li>

</div>
""", unsafe_allow_html=True)

# =========================
# Tab 5: 석식
# =========================
with tab5:

    st.markdown("""
<div class="card">

<div class="info-row">
    <div class="info-label">🍽 식당</div>
    <div style="text-align:right;">
    <div style="font-weight:700; color:#1F2937;">
        한상근대통밥집
    </div>
    <div class="small">
        (담양군 월산면 담장로 113)
    </div>
</div>
</div>

<div class="info-row">
    <div class="info-label">🍴 메뉴</div>
    <div style="
    text-align:right;
    font-weight:700;
    color:#1F2937;
">
    죽계찜 · 떡갈비 · 돼지갈비 · 홍어무침
</div>
</div>

<div class="info-row-last">
    <div class="info-label">🪑 자리배치도</div>
</div>
<img src="https://raw.githubusercontent.com/chulhan11jang/CEO_Talk_Plus/main/dinner3.png"
     style="width:100%;
            margin-top:0px;
            border-radius:12px;
            border:1px solid #E7E7E7;">

</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<div style="font-size:0.85rem; color:#888888;">
CEO Talk Plus · Mobility Solution<br>
문의 : 장철한 선임 
<a href="tel:01034766176"
   style="color:#0EA5A4; text-decoration:none; font-weight:600;">
010-3476-6176
</a>
</div>
""", unsafe_allow_html=True)
