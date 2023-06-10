from io import BytesIO
from datetime import datetime

import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns

import preprocessor
import helper
import nltk

nltk.download("vader_lexicon")
plt.rcParams['font.size'] = 18
st.set_page_config(layout="centered")

c1, c2 = st.columns((5, 2))
c1.title("Sentiment Analyzer for Whatsapp")
c2.image("./Images/whatsapp.png")

wc_loaded = False


time_format = st.sidebar.radio('Provide your time format', ['24 hour clock', '12 hour clock'])
uploaded_file = st.sidebar.file_uploader("Choose a file from your device")

# st.text(time_format)
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df, df_deleted, df_emoji = preprocessor.preprocess(data, time_format)

    # st.title("Uploaded Dataset")
    # st.dataframe(df)

    # Fetch unique users
    user_list = list(df['user'].unique())
    # user_list.remove("Notification")
    user_list.sort()
    user_list.insert(0, "General")

    selected_user = st.sidebar.selectbox("User Specific Analysis", user_list)

    if st.sidebar.button("Analyze"):
        total_messages, words, total_media, total_links, tags_len, df_text, con_len = helper.fetch_stats(selected_user,
                                                                                                         df)
        df_deleted = helper.change_user(selected_user, df_deleted)
        df_emoji = helper.change_user(selected_user, df_emoji)

        st.title("Key Metrics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.subheader("Total Messages")
            st.title(total_messages)

        with col2:
            st.subheader("Overall Words")
            st.title(words)

        with col3:
            st.subheader("Multimedia Shared")
            st.title(total_media)

        with col4:
            st.subheader("URL Links Shared")
            st.title(total_links)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown('<h3 style="color: blue;">Deleted Messages</h3>', unsafe_allow_html=True)
            st.title(df_deleted.shape[0])

        with col2:
            st.markdown('<h3 style="color: blue;">Overall Emojis</h3>', unsafe_allow_html=True)
            st.title(df_emoji.shape[0])

        with col3:
            st.markdown('<h3 style="color: blue;">Total Times Tagged</h3>', unsafe_allow_html=True)
            st.title(tags_len)

        with col4:
            st.markdown('<h3 style="color: blue;">Contacts Shared</h3>', unsafe_allow_html=True)
            st.title(con_len)

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
        st.title("Activity Analytics")

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

        # Finding the most active users in the group
        st.title("Frequency Analytics")

        if selected_user == "General":
            user_freq, activity_pct = helper.message_frequency(df)
            fig6, ax6 = plt.subplots(figsize=(12, 12))

            if len(user_list) > 5:
                sns.barplot(x=user_freq.index, y=user_freq.values, ax=ax6)
                ax6.set_xticklabels(ax6.get_xticklabels(), rotation=45, horizontalalignment='right')
                ax6.set_ylabel("No. of Messages", fontsize=32, fontweight='bold')
                sns.despine()
                plt.title("Most Active Members")
                st.pyplot(fig6)

                st.subheader("Contribution in Conversation")
                fig7, ax7 = plt.subplots(figsize=(12, 9))
                ax7.pie(activity_pct, radius=4, pctdistance=0.8, autopct="%1.2f%%", startangle=30)
                ax7.legend(activity_pct.index, fontsize=32, loc="center left", bbox_to_anchor=(2.15, 0, 0.5, 3.25))
                st.pyplot(fig7, dip=600, bbox_inches="tight")

            elif len(user_list) < 6:
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Most Active Members")
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

        st.title("Content Analytics")
        # Word Cloud
        st.header("Word Cloud")
        word_cloud, df_text, df_tags, wc_loaded = helper.create_word_cloud(selected_user, df_text)
        fig8, ax8 = plt.subplots()
        ax8.imshow(word_cloud, interpolation='bilinear')
        plt.axis("off")
        st.pyplot(fig8, dpi=600)
        if wc_loaded:
            image_binary = BytesIO()
            word_cloud.to_image().save(image_binary, format='PNG')
            contents = image_binary.getvalue()
            st.sidebar.download_button(
                label="Download WC",
                data=contents,
                file_name=f"WordCloud-{datetime.now()}({selected_user}).png",
                mime="image/png"
            )

        # Most common words
        st.header("Words of Choice")
        df_freq = helper.most_common_words(selected_user, df_text)
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
        emoji_set = helper.emoji_helper(selected_user, df_emoji)

        # Defining the font family for emoji display
        emoji_font = {"fontname": "Segoe UI Emoji"}

        st.header("Top 10 Emojis😂😂")
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

        st.title("Sentiment Analysis")

        if selected_user == "General":
            if len(user_list) > 5:
                df_sa = helper.sentiment_analysis(selected_user, df_text)
                fig11, ax11 = plt.subplots(figsize=(12, 9))
                sns.countplot(data=df_sa, x="user", hue="sentiments", palette=["tab:red", "tab:green"], ax=ax11)
                plt.xticks(rotation="vertical", fontsize=16)
                ax11.set_xticklabels(ax11.get_xticklabels(), rotation=50, horizontalalignment='right')
                ax11.set_xlabel("")
                ax11.set_ylabel("Sentiment Score", fontsize=32, fontweight='bold')
                st.pyplot(fig11)

            elif len(user_list) < 6:
                df_sa = helper.sentiment_analysis(selected_user, df_text)
                fig11, ax11 = plt.subplots(figsize=(12, 9))
                sns.countplot(data=df_sa, x="user", hue="sentiments", palette=["tab:red", "tab:green"], ax=ax11)
                ax11.set_xlabel("Members", fontsize=22)
                ax11.set_ylabel("No. of Messages", fontsize=22)
                st.pyplot(fig11)

        else:
            df_sa = helper.sentiment_analysis(selected_user, df_text)
            fig11, ax11 = plt.subplots(figsize=(12, 9))
            sns.countplot(data=df_sa, x="sentiments", palette=["tab:red", "tab:green"], ax=ax11)
            ax11.set_xlabel(f"Sentiments of {selected_user}", fontsize=22)
            ax11.set_ylabel("No. of Messages", fontsize=22)
            st.pyplot(fig11)
