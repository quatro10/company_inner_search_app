"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# 1. ライブラリの読み込み
############################################################
from dotenv import load_dotenv
import logging
import streamlit as st
import utils
from initialize import initialize
import components as cn
import constants as ct

############################################################
# 2. 設定関連
############################################################
# ブラウザタブと画面レイアウトの設定（wideに変更）
st.set_page_config(
    page_title=ct.APP_NAME,
    layout="wide"
)

# ロガー設定
logger = logging.getLogger(ct.LOGGER_NAME)

############################################################
# 3. 初期化処理
############################################################
try:
    initialize()
except Exception as e:
    logger.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n{e}")
    st.error(utils.build_error_message(ct.INITIALIZE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    st.stop()

if "initialized" not in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.APP_BOOT_MESSAGE)

############################################################
# 4. サイドバー（利用目的の選択 + 入力例の表示）
############################################################
with st.sidebar:
    st.header("利用目的")
    st.radio(
        label="",
        options=[ct.ANSWER_MODE_1, ct.ANSWER_MODE_2],
        key="mode"
    )

    st.markdown("#### 「社内文書検索」を選択した場合")
    st.info("入力内容と関連性が高い社内文書のありかを検索できます。")
    st.markdown("##### 【入力例】\n社員の育成方針に関するMTGの議事録")

    st.markdown("#### 「社内問い合わせ」を選択した場合")
    st.info("質問・要望に対して、社内文書の情報をもとに回答を得られます。")
    st.markdown("##### 【入力例】\n人事部に所属している従業員情報を一覧化して")

############################################################
# 5. メイン画面：初期タイトルとガイダンス
############################################################
st.title(ct.APP_NAME)

with st.container():
    st.chat_message("assistant").markdown(
        f"{ct.LINK_SOURCE_ICON} こんにちは。私は社内文書の情報をもとに回答する生成AIチャットボットです。"
        f"サイドバーで利用目的を選択し、画面下部のチャット欄からメッセージを送信してください。"
    )
    st.warning("⚠️ 具体的に入力したほうが期待通りの回答を得やすいです。")

############################################################
# 6. 会話ログの表示
############################################################
try:
    cn.display_conversation_log()
except Exception as e:
    logger.error(f"{ct.CONVERSATION_LOG_ERROR_MESSAGE}\n{e}")
    st.error(utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    st.stop()

############################################################
# 7. チャット入力の受け付け
############################################################
chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)

############################################################
# 8. チャット送信時の処理
############################################################
if chat_message:
    # ユーザー発言の表示とログ
    logger.info({"message": chat_message, "application_mode": st.session_state.mode})
    with st.chat_message("user"):
        st.markdown(chat_message)

    # LLM応答の取得
    res_box = st.empty()
    with st.spinner(ct.SPINNER_TEXT):
        try:
            llm_response = utils.get_llm_response(chat_message)
        except Exception as e:
            logger.error(f"{ct.GET_LLM_RESPONSE_ERROR_MESSAGE}\n{e}")
            st.error(utils.build_error_message(ct.GET_LLM_RESPONSE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            st.stop()

    # アシスタントメッセージの表示
    with st.chat_message("assistant"):
        try:
            if st.session_state.mode == ct.ANSWER_MODE_1:
                content = cn.display_search_llm_response(llm_response)
            elif st.session_state.mode == ct.ANSWER_MODE_2:
                content = cn.display_contact_llm_response(llm_response)
            logger.info({"message": content, "application_mode": st.session_state.mode})
        except Exception as e:
            logger.error(f"{ct.DISP_ANSWER_ERROR_MESSAGE}\n{e}")
            st.error(utils.build_error_message(ct.DISP_ANSWER_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            st.stop()

    # 会話ログへの追加
    st.session_state.messages.append({"role": "user", "content": chat_message})
    st.session_state.messages.append({"role": "assistant", "content": content})
