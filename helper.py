from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
from PIL import Image
import pandas as pd
import numpy as np
import string
import emoji

url_extract = URLExtract()
sia = SentimentIntensityAnalyzer()


def change_user(selected_user, df):
    if selected_user != "General":
        df = df[df["user"] == selected_user].reset_index(drop=True)
    return df


def fetch_stats(selected_user, df):
    df = change_user(selected_user, df)

    # Dropping voice and video call notifications
    df = df[(df["message"] != "Missed voice call\n") & (df["message"] != "Missed video call\n")].reset_index(drop=True)

    # 1. Fetch total number of messages
    total_messages = df.shape[0]

    # 2. Fetch total number of media messages
    total_media = df[(df["message"] == "<Media omitted>\n") | (df["message"] == "<Video message omitted>\n")].shape[0]
    df_text = df[(df["message"] != "<Media omitted>\n") & (df["message"] != "<Video message omitted>\n")].reset_index(drop=True)


    # 3. Fetch total number of links shared
    links = 0
    messages = []
    for message in df_text["message"]:
        if url_extract.has_urls(message):
            urls = url_extract.find_urls(message)
            links += 1
            for url in urls:
                # Replaced by a stopword, so it does not come up in the wordcloud later
                message.replace(url, "uss")
        messages.append(message)

    df_text["message"] = messages
    df_text = df_text[df_text["message"] != "null\n"].reset_index(drop=True)

    # 4. Fetch total number of words
    words = 0
    tags_len = 0
    con_len = 0
    for message in df_text['message']:
        if message.find("(file attached)\n") != -1:
            con_len += 1
        for word in message.lower().split():
            if word[0] == "@" and len(word) != 1:
                tags_len += 1
            else:
                words += 1

    return total_messages, words, total_media, links, tags_len, df_text, con_len


def message_frequency(df):
    ratio = df["user"].value_counts() / df.shape[0]
    return df["user"].value_counts(), ratio


def refine_text(selected_user, df):
    df = change_user(selected_user, df)

    indices = []
    new_messages = []

    table = str.maketrans("", "", string.punctuation)
    with open("./stop_words.txt", "r", encoding="utf-8") as file:
        stop_words = file.read().splitlines()

    for i in range(df.shape[0]):
        words = []
        for word in df["message"][i].lower().split():
            if word[0] == "@" and len(word) != 1:
                if i not in indices:
                    indices.append(i)
            else:
                # Here, I replaced a special type of apostrophe I found only in case of apple users
                words.append(word.replace("’", ""))
        stripped = [w.translate(table) for w in words]  # Stripping of punctuations
        cleaned = [word for word in stripped if word not in stop_words]  # Cleaning of the stop words
        denumbered = [word for word in cleaned if not word.isdigit()]
        new_messages.append(" ".join(denumbered))

    df_tags = df.iloc[indices, :].reset_index(drop=True)
    df["message"] = new_messages
    df_text = df[df["message"] != ""]
    return  df_text, df_tags


def create_word_cloud(df_text, mask):

    if mask == "Square":
        wc = WordCloud(width=1368, height=1024, min_font_size=12, background_color="white")
    else:
        if mask == "Thought Cloud":
            wc_mask = np.array(Image.open("icons/chat-icon-vector-illustration (2600).jpg"))
            wc = WordCloud(width=1368, height=1024, mask=wc_mask, min_font_size=12, background_color="white")
        else:
            wc_mask = np.array(Image.open("icons/OIP (1902).png"))
            wc = WordCloud(width=1368, height=1024, mask=wc_mask, min_font_size=12, background_color="white")

    df_wc = wc.generate(df_text['message'].str.cat(sep=" "))
    return df_wc, True


def most_common_words(df_text):
    words = []
    for message in df_text["message"]:
        for word in message.split():
            words.append(word)

    return pd.DataFrame(Counter(words).most_common(20), columns=["word", "frequency"])


def emoji_helper(df_emoji):

    emojis = []
    for message in df_emoji["message"]:
        emojis_dict = emoji.emoji_list(message)
        for i in range(len(emojis_dict)):
            emojis.append(emojis_dict[i]["emoji"])

    my_df = pd.DataFrame(Counter(emojis).most_common(10), columns=["emoji", "count"])

    return my_df


def monthly_timeline(selected_user, df):
    df = change_user(selected_user, df)

    m_timeline = df.groupby(["year", "month_num", "month"]).count()["message"].reset_index()

    time = []
    for i in range(m_timeline.shape[0]):
        time.append(m_timeline["month"][i][:3] + "-" + str(m_timeline["year"][i])[2:])

    m_timeline["time"] = time

    return m_timeline


def daily_timeline(selected_user, df):
    df = change_user(selected_user, df)
    d_timeline = df.groupby("only_date").count()["message"].reset_index()

    return d_timeline


def activity_per_day(selected_user, df):
    df = change_user(selected_user, df)

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    day_counts = df["day_name"].value_counts()
    day_counts_map = {day: day_counts.get(day, 0) for day in day_order}

    # Create the DataFrame from the day_counts_map
    df_d = pd.DataFrame({"day_freq": day_counts_map.values(), "day_num": range(1, len(day_counts_map) + 1)},
                        index=day_counts_map.keys())
    df_d = df_d[df_d['day_freq'] != 0]
    # Create a shorter label for the days
    df_d.index = [x[:3] for x in df_d.index]

    return df_d


def activity_per_month(selected_user, df):
    df = change_user(selected_user, df)

    df_month = pd.DataFrame({"month_name": df["month"].value_counts().values,
                             "month_num": [(list(df.sort_values(by="month_num")["month"].unique()).index(mon) + 1)
                                           for mon in df["month"].value_counts().index]},
                            index=df["month"].value_counts().index)

    df_month.sort_values(by="month_num", inplace=True)
    df_month.index = [x[:3] for x in df_month.index]

    return df_month


def activity_heatmap(selected_user, df):
    df = change_user(selected_user, df)
    period = []
    for hour in df[["day_name", "hour"]]["hour"]:
        if hour == 23:
            period.append(str(hour) + "-" + "00")
        elif hour < 9:
            period.append("0" + str(hour) + "-0" + str(hour + 1))
        elif hour == 9:
            period.append("0" + str(hour) + "-" + str(hour + 1))
        elif hour > 9:
            period.append(str(hour) + "-" + str(hour + 1))

    df["period"] = period

    activity = df.pivot_table(index="day_name", columns="period", values="message", aggfunc="count").fillna(0)

    return activity


def message_sa(message):
    compound_sentiment = sia.polarity_scores(message)["compound"]
    if compound_sentiment > 0:
        return "Positive"
    elif compound_sentiment < 0:
        return "Negative"
    else:
        return "Neutral"


def sentiment_analysis(df_text):
    df_sa = df_text[["user", "message"]]
    df_sa["sentiments"] = df_sa["message"].apply(message_sa)
    df_sa = df_sa[df_sa["sentiments"] != "Neutral"]
    df_sa.sort_values(by=["sentiments"], ascending=True, inplace=True)
    return df_sa
