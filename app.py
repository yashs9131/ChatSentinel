from streamlit_option_menu import option_menu
from datetime import datetime
from io import BytesIO

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns

import preprocessor
import helper

font_filename = './NotoEmoji-VariableFont_wght.ttf'
custom_font = fm.FontProperties(fname=font_filename)

plt.rcParams['font.size'] = 18

st.set_page_config(
    page_title="Chat Sentinel",
    layout="centered"
)

wc_loaded = False

st.markdown(
    """
    <style>
        .sidebar .sidebar-content {
            width: 35vw;
        }
        .content {
            font-family: Verdana, Arial, Helvetica, sans-serif;
        }
        h1 {
            margin-top: 14vh;
            margin-bottom: 4vh;
        }
        h2 {
            margin-top: 2vh;
            margin-bottom: 4vh;
        }
        h4 {
            font-size: 2rem;
            margin-top: 2vh;
            margin-bottom: 3vh;
        }
        h5 {
            font-size: 1.8rem;
            margin-top: 4vh;
            margin-bottom: 1vh;
        }
        .analysis-item {
            font-size: 1.3rem;
        }
        .item-description {
            font-family: Verdana, Arial, Helvetica, sans-serif;
            font-size: 0.95rem;
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
        a {
            color: #09497d;
            float: right;
        }
    </style>
    """,
    unsafe_allow_html=True
)

h1, h2, h3 = st.columns((1, 4.5, 1))
with h2:
    st.image(image="./icons/logo.png")

selected = option_menu(None, ["Home", "Launch"],
    icons=['house', 'rocket-takeoff'],
    menu_icon="cast", default_index=0, orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "#ff9e3a", "font-size": "1.5rem", "margin-right": "1vw"},
        "nav-link": {"font-size": "1.2rem", "text-align": "center", "margin":"0px"},
        "nav-link-selected": {"background-color": "#174fa7"}
    }
)

if selected == "Home":
    st.markdown("""<h4>Welcome to Chat Sentinel</h4><p class="content">
    Have you ever wondered what lies beneath the surface of your WhatsApp chats? Curious to explore the emotions, 
    trends, and insights hidden within those text exchanges? Look no further! We present our very own Chat Sentinel, a 
    fascinating journey into the realm of WhatsApp chat analysis. </p><p class="content">In this innovative NLP project, we delve deep 
    into your WhatsApp conversations, focusing on sentiment analysis and dynamic word clouds, among other insightful 
    graphs and figures. Discover the emotional tone of your chats, identify recurring themes, and gain a fresh 
    perspective on your interactions with friends, family, or colleagues.</p><p class="content">Getting started is easy! Simply find 
    the "Export Chat" option in your WhatsApp application, and you're ready to unlock the power of Chat Sentinel. 
    Whether you're seeking personal insights, exploring social dynamics, or conducting research, join us on this 
    captivating journey of discovery through your very own WhatsApp chats. Your messages have stories to tell, and Chat 
    Sentinel is here to help you unravel them.</p>""", unsafe_allow_html=True)

    st.markdown("""<h5>How it works</h5>
    <p class="content">Through four key components, it provides valuable insights into your chats: </p>
    <ul>
    <li><b class="analysis-item">Activity Analysis:</b><span class="item-description"> Understand the engagement levels of chat participants.</span>
    <p class="content">Activity analysis examines the engagement levels of all members in the group or both 
    participants in a one-on-one conversation.</p></li>
    <li><b class="analysis-item">Frequency Analysis:</b><span class="item-description"> Discover who communicates the most within the chat.</span>
    <p class="content">Frequency analysis assesses and illustrates the volume of text messages sent by each member 
    of the chat.</p></li>
    <li><b class="analysis-item">Content Analysis:</b><span class="item-description"> Gain insights into prevalent conversation themes and keywords.</span>
    <p class="content">Content analysis delves into the actual content of the text messages exchanged within the 
    chat.</p></li>
    <li><b class="analysis-item">Sentiment Analysis:</b><span class="item-description"> Gauge the emotional tone of your chats.</span>
    <p class="content">Sentiment analysis focuses on the emotions and sentiments expressed in the messages.</p></li>
    </ul>
    <p class="content">These components collectively empower you to explore the dynamics, patterns, and sentiments within your WhatsApp 
    exchanges, offering a deeper understanding of your conversations. </p>
    <p class="content"> We uphold <b>strict data privacy standards</b>. Your client data is <b>never stored</b>; any uploaded files are promptly deleted when you leave our website. </p>
    <p class="content"> Feel free to try this out yourself and hit the <b>Launch</b> tab on the top of our homepage </p>
    """, unsafe_allow_html=True)

else:
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
                df_text, df_tags = helper.refine_text(selected_user, df_text)

                st.title("Key Metrics")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown('<h3 class="metric-text">Total Messages</h3>', unsafe_allow_html=True)
                    st.markdown(f'<h3 class="metric-num">{total_messages}</h3>', unsafe_allow_html=True)

                with col2:
                    st.markdown('<h3 class="metric-text">Overall Words</h3>', unsafe_allow_html=True)
                    st.markdown(f'<h3 class="metric-num">{words}</h3>', unsafe_allow_html=True)

                with col3:
                    st.markdown('<h3 class="metric-text">Multimedia Shared</h3>', unsafe_allow_html=True)
                    st.markdown(f'<h3 class="metric-num">{total_media}</h3>', unsafe_allow_html=True)

                with col4:
                    st.markdown('<h3 class="metric-text">URL Links Shared</h3>', unsafe_allow_html=True)
                    st.markdown(f'<h3 class="metric-num">{total_links}</h3>', unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown('<h3 class="metric-text">Deleted Messages</h3>', unsafe_allow_html=True)
                    st.markdown(f'<h3 class="metric-num">{df_deleted.shape[0]}</h3>', unsafe_allow_html=True)

                with col2:
                    st.markdown('<h3 class="metric-text">Overall Emojis</h3>', unsafe_allow_html=True)
                    st.markdown(f'<h3 class="metric-num">{df_emoji.shape[0]}</h3>', unsafe_allow_html=True)

                with col3:
                    st.markdown('<h3 class="metric-text">Total Times Tagged</h3>', unsafe_allow_html=True)
                    st.markdown(f'<h3 class="metric-num">{tags_len}</h3>', unsafe_allow_html=True)

                with col4:
                    st.markdown('<h3 class="metric-text">Contacts Shared</h3>', unsafe_allow_html=True)
                    st.markdown(f'<h3 class="metric-num">{con_len}</h3>', unsafe_allow_html=True)

                with st.expander("What is this?"):
                    st.markdown("""<p class="content">We've counted everything: total messages, word acrobatics, media sharing, URL links, 
                    deleted messages (the vanishing act), emojis (those mood-makers), total times tagged and contacts 
                    shared. Your chat history is now a delightful mix of insights and laughter! </p>""",
                    unsafe_allow_html=True)

                st.title("Activity Calendar")
                # TIMELINE
                # 1. Monthly Timeline
                st.header("Monthly Activity")
                df_m_timeline = helper.monthly_timeline(selected_user, df)
                fig1, ax1 = plt.subplots(figsize=(18, 11))
                sns.scatterplot(ax=ax1, data=df_m_timeline, x="time", y="message", color="mediumblue")
                plt.plot("time", "message", data=df_m_timeline, color="brown")
                plt.xlabel("")
                plt.xticks(rotation=90, fontsize=22)
                plt.grid(visible=True, linewidth=1, axis="x")
                plt.ylabel("")
                st.pyplot(fig1)
                with st.expander("What is this?"):
                    st.markdown("""<p class="content">Take a peek at our "Monthly Activity" graph to track how message 
                    traffic evolves month by month in your chat. It's like having a chat calendar that shows you when 
                    conversations heat up or cool down over time.</p>""", unsafe_allow_html=True)

                # 2. Daily Timeline
                st.header("Daily Activity")
                df_d_timeline = helper.daily_timeline(selected_user, df)
                fig2, ax2 = plt.subplots(figsize=(18, 11))
                sns.scatterplot(ax=ax2, data=df_d_timeline, x="only_date", y="message", color="mediumblue")
                plt.plot("only_date", "message", data=df_d_timeline, color="brown")
                plt.grid(visible=True, linewidth=1)
                plt.xlabel("")
                plt.xticks(fontsize=22)
                plt.yticks(fontsize=20)
                plt.ylabel("")
                st.pyplot(fig2)
                with st.expander("What is this?"):
                    st.markdown("""<p class="content">With our "Daily Activity" graph, you can zoom in on daily message traffic patterns. 
                    Discover which days are bustling with chatter and which ones are more relaxed. It's your daily 
                    chat diary, making it easier to understand your communication dynamics.</p>""", unsafe_allow_html=True)

                # Traffic
                if "Activity" in analyses:
                    st.title("Activity Analysis")
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Each Day")
                        df_d = helper.activity_per_day(selected_user, df)
                        fig3, ax3 = plt.subplots(figsize=(14, 12))
                        ax3.bar(df_d.index, df_d["day_freq"], color=["c", "y"])
                        plt.xticks(fontsize=36)
                        plt.yticks(fontsize=32)
                        st.pyplot(fig3)
                        with st.expander("What is this?"):
                            st.markdown("""<p class="content">Dive into our "Each Day" analysis to see when messages are sent during the 
                            week. It's like a chat calendar showing which days are the liveliest.</p>""", unsafe_allow_html=True)

                    with col2:
                        st.subheader("Each Month")
                        df_m = helper.activity_per_month(selected_user, df)
                        fig4, ax4 = plt.subplots(figsize=(14, 12))
                        ax4.bar(df_m.index, df_m["month_name"], color=["tab:blue", "tab:purple", "tab:pink"])
                        plt.xticks(fontsize=26)
                        plt.yticks(fontsize=32)
                        st.pyplot(fig4)
                        with st.expander("What is this?"):
                            st.markdown("""<p class="content">Explore "Each Month" to discover trends in message sending over the year. 
                            Spot any monthly patterns or changes in user activity, like a weather report for your 
                            chat engagement!</p>""", unsafe_allow_html=True)

                    st.header("Activity Heatmap")
                    user_heatmap = helper.activity_heatmap(selected_user, df)
                    fig5, ax5 = plt.subplots(figsize=(15, 12))
                    sns.heatmap(user_heatmap, ax=ax5)
                    plt.xlabel("")
                    plt.ylabel("")
                    st.pyplot(fig5)
                    with st.expander("What is this?"):
                        st.markdown("""<p class="content">Imagine a colorful map that shows when people chat the most during the week, 
                        hour by hour. Our Activity Heatmap helps you spot busy times and any regular patterns in your 
                        chat activity. It's like a weather map for your chat engagement!</p>""", unsafe_allow_html=True)

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
                            with st.expander("What is this?"):
                                st.markdown("""<p class="content">The "Most Active Members" plot lists users who send the most messages, 
                                from top to bottom. It's like a leaderboard of the chattiest folks!</p>""", unsafe_allow_html=True)

                            st.subheader("Contribution in Conversation")
                            fig7, ax7 = plt.subplots(figsize=(12, 9))
                            ax7.pie(activity_pct, radius=4, pctdistance=0.8, autopct="%1.2f%%", startangle=30)
                            ax7.legend(activity_pct.index, fontsize=32, loc="center left",
                                       bbox_to_anchor=(2.15, 0, 0.5, 3.25))
                            st.pyplot(fig7, dpi=600, bbox_inches="tight")
                            with st.expander("What is this?"):
                                st.markdown("""<p class="content">The "Contribution in Conversation" plot uses a pie chart to show how 
                                different members participate in the chat. You'll get a visual breakdown of who's 
                                doing the talking. It's like a chat conversation in a pie slice!</p>""", unsafe_allow_html=True)

                        elif len(user_list) < 6:
                            col1, col2 = st.columns(2)

                            with col1:
                                st.subheader("Most Talkative Members")
                                sns.barplot(x=user_freq.index, y=user_freq.values, ax=ax6, palette="viridis")
                                plt.xticks(rotation="vertical", fontsize=32)
                                ax6.set_ylabel("No. of Messages", fontsize=36)
                                st.pyplot(fig6)
                                with st.expander("What is this?"):
                                    st.markdown("""<p class="content">The "Most Active Members" plot lists users who send the most messages, 
                                    from top to bottom. It's like a leaderboard of the chattiest folks!</p>""", unsafe_allow_html=True)

                            with col2:
                                st.subheader("Ratios of Activity")
                                fig7, ax7 = plt.subplots()
                                ax7.pie(activity_pct, radius=2, autopct='%1.2f%%', startangle=30)
                                ax7.legend(activity_pct.index, loc="center left", bbox_to_anchor=(1, 0, 0.5, 2.5))
                                st.pyplot(fig7, dpi=200, bbox_inches="tight")
                                with st.expander("What is this?"):
                                    st.markdown("""<p class="content">The "Ratio of Activity" graph examines message distribution among 
                                    WhatsApp group members, providing insights into their engagement levels. This 
                                    visual representation reveals individual contributions to group conversations, 
                                    offering valuable data on group dynamics and member involvement.</p>""", unsafe_allow_html=True)

                if shape != "No WordCloud":
                    # Word Cloud
                    st.title("Word Cloud")
                    word_cloud, wc_loaded = helper.create_word_cloud(df_text, shape)
                    fig8, ax8 = plt.subplots()
                    ax8.imshow(word_cloud, interpolation='bilinear')
                    plt.axis("off")
                    st.pyplot(fig8, dpi=600)
                    with st.expander("What is this?"):
                        st.markdown("""<p class="content">Picture this as a colorful cloud of words! We've taken out the common words and 
                        created a playful visual where word size shows how often they're used. The bigger, the more 
                        frequent. It's like a word party where the popular words steal the show. Our "Word Cloud"
                        feature offers various shapes to visualize your chat content. Try them out for a unique and 
                        visually engaging perspective on your conversations.</p>""", unsafe_allow_html=True)
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
                    with st.expander("What is this?"):
                        st.markdown("""<p class="content">Get ready to uncover the chat's star words! We've sorted through the chatter to 
                        find the top 20 words that pop up the most. It's like a highlight reel of the hottest chat 
                        topics. Let's see what everyone's been talking about!</p>""", unsafe_allow_html=True)

                    # Emoji Analysis
                    emoji_set = helper.emoji_helper(df_emoji)

                    st.header("Excessive Emojis")
                    fig10, ax10 = plt.subplots(figsize=(12, 9))
                    sns.barplot(data=emoji_set, y="count", x="emoji", ax=ax10, palette="autumn")
                    ax10.set_xticklabels(emoji_set["emoji"].tolist(), rotation=0)
                    sns.despine()
                    plt.grid(visible=True, linewidth=1, axis="y")
                    plt.xticks(fontsize=20, fontproperties=custom_font)
                    plt.yticks(fontsize=14)
                    plt.xlabel("")
                    plt.ylabel("")
                    st.pyplot(fig10)
                    with st.expander("What is this?"):
                        st.markdown("""<p class="content">Discover the chat's emoji superstars! We've rounded up the 
                        ten most-used emojis, each with its own count. It's like a peek into the emotional 
                        roller-coaster and expressions of your chat participants. Get ready to decode 
                        the emoji vibes!</p>""", unsafe_allow_html=True)

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

                    with st.expander("What is this?"):
                        st.markdown("""<p class="content">We're decoding the chat's emotional rollercoaster! Dive into the spectrum of 
                        feelings with vibrant green bars for positive vibes and striking red bars for not-so-happy 
                        moments. This visual insight reveals the emotional tone of the conversation and who's 
                        contributing to the chat's overall mood.</p>""", unsafe_allow_html=True)
