from io import BytesIO
from datetime import datetime

import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns

import preprocessor
import helper

plt.rcParams['font.size'] = 18
# st.set_page_config(layout="centered")
st.markdown(
    """
    <style>
        .sidebar .sidebar-content {
            width: 35vw;
        }
        h1 {
            margin-top: 14vh;
            margin-bottom: 4vh;
        }
        h2 {
            margin-top: 2vh;
            margin-bottom: 4vh;
        }
        
        .metric-text {
            margin-top: 4vh;
            font-size: 1.6rem;
            font-weight: 700;
            font-family: sans-serif;
        }
        .metric-num {
            font-size: 3.2rem;
            font-weight: 800;
            color: #094A83;
        }
        img {
            margin-bottom: 6vh;
            border-radius: 8px;
            width: 45vw;
            transition: transform 0.5s ease;
        }
        img:hover {
            transform: scale(1.05);
        }
    </style>
    """,
    unsafe_allow_html=True
)


st.image(image="./icons/logo.png")

# st.text("Decoding Emotions, Empowering Connections!")
wc_loaded = False


time_format = st.sidebar.radio('Provide your time format', ['24 hour clock', '12 hour clock'])
uploaded_file = st.sidebar.file_uploader("Choose a file from your device")


if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df, df_deleted, df_emoji = preprocessor.preprocess(data, time_format)

    # For wrong input
    if df.shape[0] == 0:
        st.error("Either the uploaded file is not a whatsapp chat export file or the chosen time format is wrong. "
                 "Please upload a whatsapp chat or choose the correct time format.")
    else:
        # Fetch unique users
        user_list = list(df['user'].unique())
        user_list.sort()
        user_list.insert(0, "General")

        tab1, tab2, tab3 = st.sidebar.tabs(["Person", "Components", "Wordcloud"])

        with tab1:
            selected_user = st.selectbox("Provide if you want a general or user specific analysis", user_list)

        with tab2:
            if selected_user == "General":
                analyses = st.multiselect("Mark the Analyses you want to see",
                                          ["Activity", "Frequency", "Content", "Sentiment"])
            else:
                analyses = st.multiselect("Mark the Analyses you want to see",
                                          ["Activity", "Content", "Sentiment"])
        with tab3:
            shape = st.radio("Pick the shape of your wordcloud",
                             ["Square", "Thought Cloud", "Whatsapp Logo", "No WordCloud"])

        sidebar_c1, sidebar_c2 = st.sidebar.columns((2, 4))
        with sidebar_c1:
            clicked = st.button("Analyze")
        if clicked:
            total_messages, words, total_media, total_links, tags_len, df_text, con_len = \
                helper.fetch_stats(selected_user, df)

            df_deleted = helper.change_user(selected_user, df_deleted)
            df_emoji = helper.change_user(selected_user, df_emoji)

            st.title("Key Metrics")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                # st.subheader("Total Messages")
                # st.title(total_messages)
                st.markdown('<h3 class="metric-text">Total Messages</h3>', unsafe_allow_html=True)
                st.markdown(f'<h3 class="metric-num">{total_messages}</h3>', unsafe_allow_html=True)

            with col2:
                # st.subheader("Overall Words")
                # st.title(words)
                st.markdown('<h3 class="metric-text">Overall Words</h3>', unsafe_allow_html=True)
                st.markdown(f'<h3 class="metric-num">{words}</h3>', unsafe_allow_html=True)

            with col3:
                # st.subheader("Multimedia Shared")
                # st.title(total_media)
                st.markdown('<h3 class="metric-text">Multimedia Shared</h3>', unsafe_allow_html=True)
                st.markdown(f'<h3 class="metric-num">{total_media}</h3>', unsafe_allow_html=True)

            with col4:
                # st.subheader("URL Links Shared")
                # st.title(total_links)
                st.markdown('<h3 class="metric-text">URL Links Shared</h3>', unsafe_allow_html=True)
                st.markdown(f'<h3 class="metric-num">{total_links}</h3>', unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown('<h3 class="metric-text">Deleted Messages</h3>', unsafe_allow_html=True)
                st.markdown(f'<h3 class="metric-num">{df_deleted.shape[0]}</h3>', unsafe_allow_html=True)
                # st.title(df_deleted.shape[0])

            with col2:
                st.markdown('<h3 class="metric-text": blue;">Overall Emojis</h3>', unsafe_allow_html=True)
                st.markdown(f'<h3 class="metric-num">{df_emoji.shape[0]}</h3>', unsafe_allow_html=True)
                # st.title(df_emoji.shape[0])

            with col3:
                st.markdown('<h3 class="metric-text">Total Times Tagged</h3>', unsafe_allow_html=True)
                st.markdown(f'<h3 class="metric-num">{tags_len}</h3>', unsafe_allow_html=True)
                # st.title(tags_len)

            with col4:
                st.markdown('<h3 class="metric-text">Contacts Shared</h3>', unsafe_allow_html=True)
                st.markdown(f'<h3 class="metric-num">{con_len}</h3>', unsafe_allow_html=True)
                # st.title(con_len)

            st.title("Activity Calender")
            # TIMELINE
            # 1. Monthly Timeline
            st.header("Monthly Activity")
            df_m_timeline = helper.monthly_timeline(selected_user, df)
            fig1, ax1 = plt.subplots(figsize=(18, 11))
            sns.scatterplot(ax=ax1, data=df_m_timeline, x="time", y="message", c="mediumblue")
            plt.plot("time", "message", data=df_m_timeline, c="brown")
            plt.xlabel("")
            plt.xticks(rotation=90, fontsize=22)
            plt.grid(visible=True, linewidth=1, axis="x")
            plt.ylabel("")
            st.pyplot(fig1)

            # 2. Daily Timeline
            st.header("Daily Activity")
            df_d_timeline = helper.daily_timeline(selected_user, df)
            fig2, ax2 = plt.subplots(figsize=(18, 11))
            sns.scatterplot(ax=ax2, data=df_d_timeline, x="only_date", y="message", c="mediumblue")
            plt.plot("only_date", "message", data=df_d_timeline, c="brown")
            plt.grid(visible=True, linewidth=1)
            plt.xlabel("")
            plt.xticks(fontsize=22)
            plt.yticks(fontsize=20)
            plt.ylabel("")
            st.pyplot(fig2)

            # Traffic
            if "Activity" in analyses:
                st.title("Activity Analysis")
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Each Day")
                    df_d = helper.activity_per_day(selected_user, df)
                    fig3, ax3 = plt.subplots(figsize=(14, 12))
                    ax3.bar(df_d.index, df_d["day_name"], color=["c", "y"])
                    plt.xticks(fontsize=36)
                    plt.yticks(fontsize=32)
                    st.pyplot(fig3)

                with col2:
                    st.subheader("Each Month")
                    df_m = helper.activity_per_month(selected_user, df)
                    fig4, ax4 = plt.subplots(figsize=(14, 12))
                    ax4.bar(df_m.index, df_m["month_name"], color=["tab:blue", "tab:purple", "tab:pink"])
                    # st.dataframe(df_month)
                    plt.xticks(fontsize=26)
                    plt.yticks(fontsize=32)
                    st.pyplot(fig4)

                st.header("Activity Heatmap")
                user_heatmap = helper.activity_heatmap(selected_user, df)
                fig5, ax5 = plt.subplots(figsize=(15, 12))
                sns.heatmap(user_heatmap, ax=ax5)
                plt.xlabel("")
                plt.ylabel("")
                st.pyplot(fig5)

            if "Frequency" in analyses:
                # Finding the most active users in the group
                st.title("Frequency Analysis")

                if selected_user == "General":
                    user_freq, activity_pct = helper.message_frequency(df)
                    fig6, ax6 = plt.subplots(figsize=(12, 12))

                    if len(user_list) > 5:
                        sns.barplot(x=user_freq.index, y=user_freq.values, ax=ax6)
                        ax6.set_xticklabels(ax6.get_xticklabels(), rotation=45, horizontalalignment='right')
                        ax6.set_ylabel("No. of Messages", fontsize=32, fontweight='bold')
                        sns.despine()
                        plt.title("Most Talkative Members")
                        st.pyplot(fig6)

                        st.subheader("Contribution in Conversation")
                        fig7, ax7 = plt.subplots(figsize=(12, 9))
                        ax7.pie(activity_pct, radius=4, pctdistance=0.8, autopct="%1.2f%%", startangle=30)
                        ax7.legend(activity_pct.index, fontsize=32, loc="center left",
                                   bbox_to_anchor=(2.15, 0, 0.5, 3.25))
                        st.pyplot(fig7, dip=600, bbox_inches="tight")

                    elif len(user_list) < 6:
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("Most Talkative Members")
                            sns.barplot(x=user_freq.index, y=user_freq.values, ax=ax6)
                            plt.xticks(rotation="vertical", fontsize=32)
                            ax6.set_ylabel("No. of Messages", fontsize=36)
                            st.pyplot(fig6)

                        with col2:
                            st.subheader("Ratios of Activity")
                            fig7, ax7 = plt.subplots()
                            ax7.pie(activity_pct, radius=2, autopct='%1.2f%%', startangle=30)
                            ax7.legend(activity_pct.index, loc="center left", bbox_to_anchor=(1, 0, 0.5, 2.5))
                            st.pyplot(fig7, dip=200, bbox_inches="tight")

            df_text, df_tags = helper.refine_text(selected_user, df)

            if shape != "No WordCloud":
                # Word Cloud
                st.title("Word Cloud")
                word_cloud, wc_loaded = helper.create_word_cloud(df_text, shape)
                fig8, ax8 = plt.subplots()
                ax8.imshow(word_cloud, interpolation='bilinear')
                plt.axis("off")
                st.pyplot(fig8, dpi=600)
                if wc_loaded:
                    image_binary = BytesIO()
                    word_cloud.to_image().save(image_binary, format='PNG')
                    contents = image_binary.getvalue()
                    with sidebar_c2:
                        st.download_button(
                            label="Download WordCloud",
                            data=contents,
                            file_name=f"WordCloud-{datetime.now()}({selected_user}).png",
                            mime="image/png")

            if "Content" in analyses:

                st.title("Content Analysis")
                # Most common words
                st.header("Words of Choice")
                df_freq = helper.most_common_words(df_text)
                fig9, ax9 = plt.subplots(figsize=(12, 9))
                sns.set_style("white")
                sns.barplot(data=df_freq, y="word", x="frequency", ax=ax9, palette="dark:#1D9_r")
                sns.despine()
                plt.grid(visible=True, linewidth=1, axis="x")
                plt.xticks(fontsize=10)
                plt.yticks(fontsize=14)
                plt.xlabel('Number of times used', fontsize=16)
                plt.ylabel("")
                plt.title('Top 20 Words', fontsize=22)
                st.pyplot(fig9)

                # Emoji Analysis
                emoji_set = helper.emoji_helper(df_emoji)

                # Defining the font family for emoji display
                emoji_font = {"fontname": "Segoe UI Emoji"}

                st.header("Excessive Emojis")
                fig10, ax10 = plt.subplots(figsize=(12, 9))
                sns.barplot(data=emoji_set, y="count", x="emoji", ax=ax10)
                ax10.set_xticklabels(emoji_set["emoji"].tolist(), rotation=0)
                sns.despine()
                plt.grid(visible=True, linewidth=1, axis="y")
                plt.xticks(fontsize=20, **emoji_font)
                plt.yticks(fontsize=14)
                plt.xlabel("")
                plt.ylabel("")
                st.pyplot(fig10)

            if "Sentiment" in analyses:
                st.title("Sentiment Analysis")

                if selected_user == "General":
                    if len(user_list) > 5:
                        df_sa = helper.sentiment_analysis(df_text)
                        fig11, ax11 = plt.subplots(figsize=(12, 9))
                        sns.countplot(data=df_sa, x="user", hue="sentiments", palette=["tab:red", "tab:green"], ax=ax11)
                        plt.xticks(rotation="vertical", fontsize=16)
                        ax11.set_xticklabels(ax11.get_xticklabels(), rotation=50, horizontalalignment='right')
                        ax11.set_xlabel("")
                        ax11.set_ylabel("Sentiment Score", fontsize=32, fontweight='bold')
                        st.pyplot(fig11)

                    elif len(user_list) < 6:
                        df_sa = helper.sentiment_analysis(df_text)
                        fig11, ax11 = plt.subplots(figsize=(12, 9))
                        sns.countplot(data=df_sa, x="user", hue="sentiments", palette=["tab:red", "tab:green"], ax=ax11)
                        ax11.set_xlabel("Members", fontsize=22)
                        ax11.set_ylabel("No. of Messages", fontsize=22)
                        st.pyplot(fig11)

                else:
                    df_sa = helper.sentiment_analysis(df_text)
                    fig11, ax11 = plt.subplots(figsize=(12, 9))
                    sns.countplot(data=df_sa, x="sentiments", palette=["tab:red", "tab:green"], ax=ax11)
                    plt.title(f"Sentiments of {selected_user}", fontsize=32)
                    ax11.set_ylabel("No. of Messages", fontsize=22)
                    st.pyplot(fig11)
