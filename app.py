import streamlit as st
import google.generativeai as genai
import time
import json

# --- 页面基础配置 ---
st.set_page_config(
    page_title="Java设计模式AI教学工具",
    page_icon="🧩",
    layout="wide"
)

# --- AI模型配置 ---
# 从Streamlit Secrets获取API密钥
try:
    # 检查密钥是否存在
    if "API_KEY" not in st.secrets or not st.secrets["API_KEY"]:
        st.error("AI服务未配置！请在Streamlit的'Settings -> Secrets'中设置'API_KEY'。")
        st.stop()
        
    api_key = st.secrets["API_KEY"]
    genai.configure(api_key=api_key)
    
    # --- 【重要修改】 ---
    # 将模型从 'gemini-1.5-flash' 更换为更稳定、广泛可用的 'gemini-pro'
    model = genai.GenerativeModel('gemini-pro')
    # --- 【修改结束】 ---

except Exception as e:
    st.error(f"AI服务初始化失败！请检查API密钥是否有效。错误: {e}")
    st.stop()


# --- AI调用函数 ---
def generate_content(prompt):
    """通用AI内容生成函数"""
    with st.spinner('🤖 AI正在思考中，请稍候...'):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"AI生成失败，请稍后重试。可能是API调用频率限制或内容安全策略导致。错误信息: {e}")
            return None

# --- UI界面 ---
st.title("🧩 Java设计模式AI教学工具 (创建型模式)")
st.caption("一个帮助你理解工厂方法、单例、原型模式的智能助手")

# --- 模块切换 ---
tab1, tab2, tab3 = st.tabs(["**模块1：场景生成器**", "**模块2：代码对比器**", "**模块3：模式闯关**"])

# --- 模块1：场景生成器 ---
with tab1:
    st.header("场景生成器")
    st.info("选择一个设计模式和难度，AI将为你生成一个真实的业务场景及有问题的代码。")

    col1, col2 = st.columns(2)
    with col1:
        pattern_choice = st.selectbox(
            "选择设计模式:",
            ("工厂方法模式", "单例模式", "原型模式"),
            key="tab1_pattern"
        )
    with col2:
        difficulty_choice = st.selectbox(
            "选择难度:",
            ("入门", "进阶"),
            key="tab1_difficulty"
        )
    
    scene_choice = st.selectbox(
        "选择业务场景:",
        ("电商", "日志", "支付"),
        key="tab1_scene"
    )

    if st.button("🚀 生成场景与代码", key="tab1_generate"):
        prompt = f"""
        作为一名Java教学专家，请为我生成一个关于“{pattern_choice}”的教学案例，要求如下：
        1.  **业务场景**: 设定一个具体的“{scene_choice}”领域的业务场景，难度为“{difficulty_choice}”。场景描述要简洁，不超过150字。
        2.  **有耦合问题的原始Java代码**: 提供一段符合Java 8规范的原始代码。这段代码要能体现出业务逻辑，但存在明显的设计问题（例如，违反开闭原则、对象创建复杂等），从而引出使用“{pattern_choice}”的必要性。代码必须是完整的、可编译的。
        3.  **模式触发点**: 在代码下方，用一两句话明确指出“为什么需要用这个模式？”。要一针见血，点出原始代码的痛点。

        请严格按照以下格式输出，不要有任何多余的解释：
        ### 业务场景
        [这里是业务场景描述]

        ### 原始Java代码
        ```java
        // [这里是完整的Java代码]
        ```

        ### 模式触发点
        [这里是模式触发点的说明]
        """
        response_text = generate_content(prompt)
        if response_text:
            st.markdown(response_text)


# --- 模块2：代码对比器 ---
with tab2:
    st.header("代码对比器")
    st.info("粘贴你的Java代码，选择目标设计模式，AI将为你重构并解读。")

    target_pattern = st.selectbox(
        "选择优化的目标模式:",
        ("工厂方法模式", "单例模式", "原型模式"),
        key="tab2_pattern"
    )

    original_code = st.text_area("在此粘贴原始Java代码:", height=300, placeholder="public class YourClass {\n  // ...\n}")

    if st.button("✨ 生成优化代码与解读", key="tab2_generate"):
        if not original_code.strip():
            st.warning("请输入原始代码。")
        else:
            prompt = f"""
            作为一名Java架构师，请对我提供的Java代码进行重构。要求如下：
            1.  **目标**: 使用“{target_pattern}”来优化这段代码。
            2.  **生成优化代码**: 提供完整的、优化后的Java代码。在关键的修改处，必须添加简短的中文注释，解释这行代码的作用。代码必须符合Java 8规范。
            3.  **生成三句话优化解读**:
                - 第一句：明确指出解决了原始代码的什么痛点（例如，硬编码、高耦合等）。
                - 第二句：说明“{target_pattern}”的核心价值和作用是什么。
                - 第三句：提出一个启发性问题，引导学生思考模式带来的好处。例如：“如果后续新增XX，原始代码需要改哪里？优化代码为什么不用改？”

            这是我的原始代码：
            ```java
            {original_code}
            ```

            请严格按照以下格式输出：
            ### 优化后的Java代码
            ```java
            // [这里是带有关键注释的优化代码]
            ```

            ### 优化解读
            - **解决痛点**: [第一句话]
            - **模式价值**: [第二句话]
            - **启发思考**: [第三句话]
            """
            response_text = generate_content(prompt)
            if response_text:
                try:
                    parts = response_text.split("### 优化解读")
                    if len(parts) == 2:
                        optimized_part = parts[0]
                        explanation_part = "### 优化解读" + parts[1]

                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("原始代码")
                            st.code(original_code, language='java')
                        with col2:
                            st.subheader("优化后的代码")
                            st.markdown(optimized_part)
                        
                        st.divider()
                        st.markdown(explanation_part)
                    else:
                        st.error("AI返回格式有误，无法解析。")
                        st.text(response_text)

                except Exception as e:
                    st.error(f"解析AI返回内容时出错: {e}")
                    st.text(response_text)


# --- 模块3：模式闯关 ---
with tab3:
    st.header("模式闯关")
    st.info("AI会给出一个业务场景，请你判断最适合使用哪种设计模式。")

    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = None

    if st.button("闯关开始 / 下一题", key="tab3_generate"):
        st.session_state.quiz_data = None # 重置题目
        prompt = """
        作为一名Java面试官，请为我出一道关于创建型设计模式（工厂方法、单例、原型）的选择题。
        要求：
        1.  场景描述: 描述一个常见的软件开发场景，其中隐含了某个设计问题。
        2.  问题: 提出问题：“在这种情况下，最适合使用哪种设计模式来解决问题？”
        3.  选项: 提供三个选项，一个是正确答案，另外两个是具有迷惑性的干扰项。
        4.  答案与解析: 给出正确答案的键（例如A, B, C），并提供详细解析。解析需要解释为什么正确答案是合适的，以及为什么另外两个干扰项不合适。解析要通俗易懂。

        请严格按照以下JSON格式输出，不要有任何多余的文字或代码块标记：
        {
          "scene": "这里是场景描述...",
          "question": "在这种情况下，最适合使用哪种设计模式来解决问题？",
          "options": {
            "A": "工厂方法模式",
            "B": "单例模式",
            "C": "原型模式"
          },
          "answer": "A",
          "explanation": {
            "correct": "这里解释为什么A是正确的...",
            "incorrect_B": "这里解释为什么B是错误的...",
            "incorrect_C": "这里解释为什么C是错误的..."
          }
        }
        """
        response_text = generate_content(prompt)
        if response_text:
            try:
                # 清理可能的Markdown标记
                clean_text = response_text.strip().replace("```json", "").replace("```", "")
                st.session_state.quiz_data = json.loads(clean_text)
            except json.JSONDecodeError as e:
                st.error(f"题目生成失败，AI返回的JSON格式错误，请重试。错误: {e}")
                st.text("收到的原始文本:\n" + response_text)
                st.session_state.quiz_data = None

    if st.session_state.quiz_data:
        q = st.session_state.quiz_data
        
        # 确保数据结构完整
        if all(k in q for k in ['scene', 'question', 'options', 'answer', 'explanation']):
            st.markdown(f"**场景：** {q['scene']}")
            st.markdown(f"**问题：** {q['question']}")
            
            # 使用唯一key来重置选项
            radio_key = f"quiz_{q['scene']}" 
            
            options_list = [f"{key}: {value}" for key, value in q['options'].items()]
            user_choice = st.radio("请选择你的答案:", options_list, key=radio_key, index=None)

            if user_choice:
                user_answer_key = user_choice.split(":")[0]

                if user_answer_key == q['answer']:
                    st.success(f"回答正确！🎉 正确答案是 **{q['answer']}**。")
                else:
                    st.error(f"回答错误！😥 正确答案是 **{q['answer']}**。")

                with st.expander("**查看详细解析**"):
                    st.markdown(f"✔️ **为什么选 {q['answer']} ({q['options'][q['answer']]})？**")
                    st.write(q['explanation']['correct'])
                    
                    for key, value in q['options'].items():
                        if key != q['answer']:
                            explanation_key = f"incorrect_{key.upper()}"
                            # 兼容大小写
                            if explanation_key not in q['explanation']:
                                explanation_key = f"incorrect_{key.lower()}"
                            
                            if explanation_key in q['explanation']:
                                st.markdown(f"---")
                                st.markdown(f"❌ **为什么不选 {key} ({value})？**")
                                st.write(q['explanation'][explanation_key])

        else:
            st.error("AI返回的题目数据结构不完整，请尝试重新生成。")
