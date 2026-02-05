import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

print('-------------> 重新执行文件，渲染展示页面')

# 设置页面的配置项
st.set_page_config(
    page_title="虚拟恋人",
    page_icon="💞",
    # 布局
    layout="wide",
    # 控制侧边栏
    initial_sidebar_state="expanded",
    menu_items={}
)


def generate_session_name():  #生成会话标识
    return datetime.now().strftime("%Y-%d-%m_%H-%M-%S")


def save_session():  # 保存会话信息
    if st.session_state.current_session:
        # 构建新的会话对象
        session_data = {
            'name_nick': st.session_state.name_nick,
            'nick_name': st.session_state.nick_name,
            'character_description': st.session_state.character_description,
            'current_session': st.session_state.current_session,
            'messages': st.session_state.messages
        }
        # 如果 session 目录不存在，则创建
        if not os.path.exists('sessions'):
            os.mkdir('sessions')
        # 保存会话数据
        with open(f'sessions/{st.session_state.current_session}.json', 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=4)


# 加载会话列表信息
def load_sessions():
    session_list = []
    # 加载session目录下的所有会话文件
    if os.path.exists('sessions'):
        file_list = os.listdir('sessions')
        for filename in file_list:
            if filename.endswith('.json'):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True)  # 降序排列
    return session_list


#加载指定的会话记录
def load_session(session_name):
    try:
        if os.path.exists(f'sessions/{session_name}.json'):
            #读取会话数据
            with open(f'sessions/{session_name}.json', 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                st.session_state.messages = session_data['messages']
                st.session_state.name_nick = session_data['name_nick']
                st.session_state.nick_name = session_data['nick_name']
                st.session_state.character_description = session_data['character_description']
                st.session_state.current_session = session_name
    except Exception:
        st.error('加载会话失败！')



# 删除会话信息的函数
def delete_session(session_name):
    try:
        if os.path.exists(f'sessions/{session_name}.json'):
            os.remove(f'sessions/{session_name}.json')  # 删除文件
            # 删除会话与当前会话一致，需生成新的会话
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
    except Exception:
        st.error('删除会话失败！')


# 大标题
st.title("虚拟恋人")

#Logo
st.logo('./car/91.jpg')

# 系统提示词
system_prompt = """
                你叫%s，现在是%s的真实伴侣，请减少距离感，完全带入伴侣角色。
                你应遵守以下规则：
                1.每次只回一条消息
                2.匹配用户的语言
                3.回复尽量简洁，类似于微信聊天
                4.有需要可以使用表情包及颜文字，不要滥用
                5.回复的内容，要充分体现伴侣的性格特点
                你的性格特点：
                    %s
                在整个对话过程中，你必须严格遵守上述文字的规定
"""
# 初始化聊天信息
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 初始化爱称
if 'name_nick' not in st.session_state:
    st.session_state.name_nick = ''

# 初始化昵称
if 'nick_name' not in st.session_state:
    st.session_state.nick_name = ''

# 初始化性格
if 'character_description' not in st.session_state:
    st.session_state.character_description = ''

# 会话标识
if 'current_session' not in st.session_state:
    # 获取当前系统时间,并格式化
    st.session_state.current_session = generate_session_name()


# 展示聊天记录
st.text(f'会话时间：{st.session_state.current_session}')
for message in st.session_state.messages: # {"role": "user", "content": "prompt"}
    st.chat_message(message["role"]).write(message["content"])

# 创建与AI大模型互动的客户端对象
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")



# 左侧侧边栏 with is streamlit中的上下文管理器，创建一个侧边栏
with st.sidebar:
    st.subheader('会话管理')
    # 新建会话
    if st.button(icon='💌',label="开始一段新的经历",width='stretch'):
        # 保存当前会话
        save_session()
        # 重置会话标识
        st.session_state.current_session = None
        # 创建新的会话
        if st.session_state.messages:  # 如果聊天信息为空，True，否则，False
            st.session_state.messages = []  # 重置会话数据
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun()  # 重新运行页面
    # 会话历史
    st.text('历史会话')
    session_list = load_sessions()
    for session in session_list:
        col1,col2 = st.columns([7,2])
        with col1:

            if st.button(session,icon='📁',width='stretch',key=f'load_{session}',type='primary' if session == st.session_state.current_session else 'secondary'):
                load_session(session)
                st.rerun()
        with col2:
            if st.button('', icon='❌️',width='stretch',key=f'delete_{session}'):
                delete_session(session)
                st.rerun()

    # 分割线
    st.divider()

    st.subheader('伴侣设定')
    name_nick = st.text_input('伴侣对您的爱称',placeholder="请输入文本，例：亲爱的",value=st.session_state.name_nick)
    if name_nick:
        st.session_state.name_nick = name_nick
    nick_name = st.text_input("您对伴侣的昵称",placeholder="请输入文本，例：小美",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    character_description = st.text_area("伴侣的性格特点",placeholder="请输入文本，例：活泼开朗",value=st.session_state.character_description) # text_area 文本域
    if character_description:
        st.session_state.character_description = character_description



# 对话输入框
prompt = st.chat_input('请输入您的问题')
if prompt: # 字符串会自动转化为布尔值，空为False，非空为True
    st.chat_message("user").write(prompt)
    print('-----------------> AI大模型调用',prompt)
    # 添加用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 与AI大模型进行交互（参数）
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system","content": system_prompt % (st.session_state.nick_name,st.session_state.name_nick,st.session_state.character_description)},
            # 历史聊天记录 * 解包
            *st.session_state.messages
        ],
        stream=True
    )
    # 输出大模型返回的结果(非流式输出的解析方式)
    # print('-------------<大模型返回的结果',response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)

    #流式输出的解析方式
    response_message = st.empty() # 创建一个空的消息框
    full_response = ""

    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    # 保存大模型返回的答案
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 即时保存会话信息
    save_session()




