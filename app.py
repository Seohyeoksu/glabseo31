import os
from openai import OpenAI
import streamlit as st
from typing import Dict

def init_openai_client():
    api_key = st.secrets.get('API_KEY')
    if not api_key:
        st.error("OpenAI API key not found in secrets!")
        st.stop()
    return OpenAI(api_key=api_key)

def setup_page():
    st.set_page_config(
        page_title="공적조서 생성기 📜",
        page_icon="📜",
        layout="centered",
        initial_sidebar_state="auto",
    )
    
    st.markdown("""
        <style>
            .main {
                background-color: #f8f9fa;
                font-family: 'Nanum Gothic', sans-serif;
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                font-size: 2.5em;
                margin-bottom: 1.5em;
            }
            .instructions {
                background-color: #e9ecef;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 25px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .input-section {
                background-color: #ffffff;
                padding: 25px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }
            .stButton > button {
                width: auto !important;
                padding: 0.5rem 1rem;
            }
            .add-button {
                background-color: #28a745 !important;
                color: white;
                border-radius: 5px;
                margin-right: 10px;
            }
            .remove-button {
                background-color: #dc3545 !important;
                color: white;
                border-radius: 5px;
            }
            .generate-button {
                background-color: #007bff !important;
                color: white;
                font-weight: bold;
                padding: 0.75em 1.5em;
                border-radius: 5px;
                width: 100% !important;
                margin-top: 20px;
            }
            .merit-content {
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #dee2e6;
                margin: 20px 0;
                line-height: 1.8;
            }
            .merit-title {
                color: #2c3e50;
                font-weight: bold;
                margin-bottom: 10px;
                font-size: 1.2em;
            }
            .merit-text {
                line-height: 1.8;
                color: #2c3e50;
                white-space: pre-line;
            }
            .section-title {
                color: #2c3e50;
                font-weight: bold;
                margin: 15px 0 10px 0;
                font-size: 1.1em;
            }
            .merit-item {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
            .button-container {
                display: flex;
                justify-content: flex-start;
                gap: 10px;
                margin: 10px 0;
            }
            .warning-text {
                color: #856404;
                background-color: #fff3cd;
                border: 1px solid #ffeeba;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }
        </style>
    """, unsafe_allow_html=True)

def format_merit_text(text: str) -> str:
    """Format the merit text to properly display markdown in Streamlit"""
    text = text.replace("**", "**")  # Normalize bold markers
    text = text.replace(":", ":**")  # Make section titles bold
    return text

def generate_merit_text(client: OpenAI, merit_items: list, name: str, position: str, 
                       organization: str, department: str, years: str) -> dict:
    """Generate merit summary and details using OpenAI API"""
    try:
        valid_merit_items = [item for item in merit_items if item.strip()]
        num_items = len(valid_merit_items)
        
        context = (
            f"성명: {name}\n"
            f"소속: {organization}\n"
            f"부서: {department}\n"
            f"직위: {position}\n"
            f"재직기간: {years}\n"
            f"공적사항:\n"
        )
        
        for i, item in enumerate(valid_merit_items, 1):
            context += f"{i}. {item}\n"
            
        output_format = """
            입력된 정보를 바탕으로 상세한 공적조서를 작성해주세요. 다음의 형식을 정확히 따라주세요.
            
            출력 형식:
            공적요지: (전체 내용을 100자 내외로 요약한 단락. 주요 업적과 그 영향을 포함하여 구체적으로 작성)

            공적내용: """
            
        for i in range(1, num_items + 1):
            output_format += f"""

            **[{i}번째 주제]**:
            [상세 내용 - 300자 이상 상세히 기술]
            """
            
        output_format += """

            작성 규칙:
            1. 각 섹션 제목과 중요 키워드는 반드시 볼드처리(**) 사용
            2. 각 섹션은 한 줄 띄워서 구분
            3. 구체적인 날짜, 수치, 성과를 최대한 자세히 포함
            4. 시간순 또는 중요도순으로 구성
            5. 각 공적 내용은 다음 요소를 반드시 포함:
               - 구체적인 프로젝트/업무 내용
               - 수행 기간
               - 정량적 성과
               - 정성적 영향
               - 협력 기관 및 관계자
               - 혁신성과 창의성
               - 사회적/조직적 기여도
            6. 각 공적사항별로 충분한 분량(300자 이상)으로 서술
            7. 전체적으로 공적의 중요성과 파급효과가 부각되도록 작성
            8. 모든 내용은 객관적 사실을 기반으로 구체적으로 기술
            9. 입력된 각각의 공적사항을 별도의 섹션으로 작성
            10. 각 섹션의 제목은 해당 공적사항의 핵심 주제를 반영하여 작성
            11. 공적내용 제목은 공적요지 내용 후에 배치하면 좋겠어
        """
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": context},
                {"role": "system", "content": output_format}
            ],
            model="gpt-4o",
            temperature=0.7,
            max_tokens=16384,
            presence_penalty=0.2,
            frequency_penalty=0.3
        )
        
        content = chat_completion.choices[0].message.content
        parts = content.split("공적내용:", 1)
        summary = parts[0].replace("공적요지:", "").strip()
        details = parts[1].strip() if len(parts) > 1 else ""
        
        return {
            "summary": summary,
            "details": details
        }
        
    except Exception as e:
        st.error(f"공적조서 생성 중 오류가 발생했습니다: {str(e)}")
        return None

def main():
    setup_page()
    client = init_openai_client()
    
    if 'merit_items' not in st.session_state:
        st.session_state.merit_items = [""]

    st.markdown("<h1>공적조서 생성기 📜</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="instructions">
        <h3>📝 사용 방법</h3>
        <ol>
            <li>기본 정보를 입력해주세요</li>
            <li>공적사항을 추가하거나 삭제할 수 있습니다</li>
            <li>각 항목은 구체적인 내용을 포함해주세요:
                <ul>
                    <li>활동 기간</li>
                    <li>주요 성과와 실적</li>
                    <li>영향과 기여도</li>
                    <li>관련 기관명</li>
                </ul>
            </li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">기본 정보</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("성명 👤", placeholder="성명을 입력하세요")
        organization = st.text_input("소속 🏢", placeholder="소속기관을 입력하세요")
        department = st.text_input("부서 📋", placeholder="부서명을 입력하세요")
    with col2:
        position = st.text_input("직위 💼", placeholder="직위를 입력하세요")
        years = st.text_input("재직기간 📅", placeholder="예: 2020.03.01 ~ 현재")

   
    st.markdown('<div class="section-title">공적 사항</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 9])
    with col1:
        if st.button("➕ 항목 추가", key="add_merit"):
            st.session_state.merit_items.append("")
    with col2:
        if st.button("➖ 항목 삭제", key="remove_merit"):
            if len(st.session_state.merit_items) > 1:
                st.session_state.merit_items.pop()

    merit_values = []
    for i, _ in enumerate(st.session_state.merit_items):
        merit_value = st.text_area(
            f"공적사항 {i+1}",
            value=st.session_state.merit_items[i],
            height=150,
            key=f"merit_{i}",
            placeholder="구체적인 공적 내용을 입력해주세요. (기간, 성과, 영향 등 포함)"
        )
        merit_values.append(merit_value)
    st.session_state.merit_items = merit_values
    
    if st.button("공적조서 생성하기 ✨", key="generate", type="primary"):
        if not all([name, position, organization, department, years]):
            st.error("모든 기본 정보를 입력해주세요!")
            return
            
        if not any(item.strip() for item in merit_values):
            st.error("최소 한 개 이상의 공적사항을 입력해주세요!")
            return
            
        with st.spinner("📜 공적조서를 생성하고 있습니다..."):
            result = generate_merit_text(
                client,
                merit_values,
                name,
                position,
                organization,
                department,
                years
            )
            
            if result:
                st.markdown("""
                <div class="merit-content">
                    <div class="merit-title">공적요지:</div>
                    <div class="merit-text">{}</div>
                    <br>
                    <div class="merit-title">공적내용:</div>
                    <div class="merit-text">{}</div>
                </div>
                """.format(
                    result["summary"], 
                    format_merit_text(result["details"])
                ), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
