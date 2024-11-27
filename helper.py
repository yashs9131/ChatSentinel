from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
from PIL import Image
import pandas as pd
import numpy as np
import string
import emoji

import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

url_extract = URLExtract()
sia = SentimentIntensityAnalyzer()


def change_user(selected_user, df):
    if selected_user != "General":
        df = df.loc[df["user"] == selected_user].reset_index(drop=True)  # Use .loc to avoid SettingWithCopyWarning
    return df


def fetch_stats(selected_user, df):
    df = change_user(selected_user, df)

    # Dropping voice and video call notifications and counting them
    call_messages = ["Missed voice call\n", "Missed video call\n", "Incoming voice call\n", "Incoming video call\n", "Outgoing voice call\n", "Outgoing video call\n"]
    total_calls = df[df["message"].isin(call_messages)].shape[0]
    df = df[~df["message"].isin(call_messages)].reset_index(drop=True)

    # Removing deleted messages
    deleted_messages = ["This message was deleted\n"]
    df = df[~df["message"].isin(deleted_messages)].reset_index(drop=True)

    # Fetching total number of messages
    total_messages = df.shape[0]

    # Fetching total number of media messages, excluding video and voice notes
    media_messages = ["<Media omitted>\n"]
    total_media = df[df["message"].isin(media_messages)].shape[0]
    df_text = df[~df["message"].isin(media_messages)].reset_index(drop=True)

    # Fetching total number of voice and video notes separately
    media_notes = ["<Video message omitted>\n", "<Video note omitted>\n"]
    total_media_notes = df[df["message"].isin(media_notes)].shape[0]
    df_text = df_text[~df_text["message"].isin(media_notes)].reset_index(drop=True)

    # Fetching total number of links shared and replace URLs in messages
    def replace_urls_and_count(message):
        urls = url_extract.find_urls(message)
        link_count = len(urls)
        for url in urls:
            message = message.replace(url, "uss")
        return message, link_count

    df_text[["message", "link_count"]] = df_text["message"].apply(lambda message: pd.Series(replace_urls_and_count(message)))

    # Sum up the link counts to get the total number of links shared
    links = df_text["link_count"].sum()

    # Filter out empty or null messages
    df_text = df_text[df_text["message"].str.strip() != ""].reset_index(drop=True)

    # Fetching total number of words
    words = df_text["message"].str.split().apply(lambda x: len([word for word in x if not word.startswith('@')])).sum()
    tags_len = df_text["message"].str.split().apply(lambda x: len([word for word in x if word.startswith('@')])).sum()
    con_len = df_text["message"].str.contains(r"\(file attached\)\n").sum()

    return total_messages, words, total_media, total_media_notes, links, tags_len, df_text, con_len, total_calls



def message_frequency(df):
    ratio = df["user"].value_counts(normalize=True)  # Use normalize=True for ratio directly
    return df["user"].value_counts(), ratio


def refine_text(selected_user, df):
    df = change_user(selected_user, df)

    table = str.maketrans("", "", string.punctuation)
    with open("./stop_words.txt", "r", encoding="utf-8") as file:
        stop_words = set(file.read().splitlines())  # Use set for faster lookup

    df["message"] = df["message"].apply(lambda message: " ".join(
        [word.translate(table).replace("’", "") for word in message.lower().split() if word not in stop_words and not word.isdigit()]))
    df_tags = df.loc[df["message"].str.contains(r"@\w+")].reset_index(drop=True)
    df_text = df.loc[df["message"] != ""].reset_index(drop=True)
    return df_text, df_tags


def create_word_cloud(df_text, mask):
    if mask == "Square":
        wc = WordCloud(width=1368, height=1024, min_font_size=12, background_color="white")
    else:
        mask_file = 'chat-icon-vector-illustration (2600).jpg' if mask == 'Thought Cloud' else 'OIP (1902).png'
        wc_mask = np.array(Image.open(f"icons/{mask_file}"))
        wc = WordCloud(width=1368, height=1024, mask=wc_mask, min_font_size=12, background_color="white")

    df_wc = wc.generate(df_text['message'].str.cat(sep=" "))
    return df_wc, True


def most_common_words(df_text):
    words = [word for message in df_text["message"] for word in message.split()]
    return pd.DataFrame(Counter(words).most_common(20), columns=["word", "frequency"])


def emoji_helper(df_emoji):
    emojis = [emoji_item["emoji"] for message in df_emoji["message"] for emoji_item in emoji.emoji_list(message)]
    return pd.DataFrame(Counter(emojis).most_common(10), columns=["emoji", "count"])


def monthly_timeline(selected_user, df):
    df = change_user(selected_user, df)
    m_timeline = df.groupby(["year", "month_num", "month"]).size().reset_index(name="message")
    m_timeline["time"] = m_timeline.apply(lambda row: f"{row['month'][:3]}-{str(row['year'])[2:]}", axis=1)
    return m_timeline


def daily_timeline(selected_user, df):
    df = change_user(selected_user, df)
    d_timeline = df.groupby("only_date").size().reset_index(name="message")
    return d_timeline


def activity_per_day(selected_user, df):
    df = change_user(selected_user, df)
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_counts = df["day_name"].value_counts()
    day_counts_map = {day: day_counts.get(day, 0) for day in day_order}
    df_d = pd.DataFrame({"day_freq": day_counts_map.values(), "day_num": range(1, len(day_counts_map) + 1)},
                        index=day_counts_map.keys())
    df_d = df_d.loc[df_d['day_freq'] != 0]
    df_d.index = [x[:3] for x in df_d.index]
    return df_d


def activity_per_month(selected_user, df):
    df = change_user(selected_user, df)
    month_counts = df["month"].value_counts()
    sorted_months = list(df.sort_values(by="month_num")["month"].unique())
    month_indices = [sorted_months.index(mon) + 1 for mon in month_counts.index]
    df_month = pd.DataFrame({"month_name": month_counts.values, "month_num": month_indices}, index=month_counts.index)
    df_month.sort_values(by="month_num", inplace=True)
    df_month.index = [x[:3] for x in df_month.index]
    return df_month


def activity_heatmap(selected_user, df):
    df = change_user(selected_user, df)
    df["period"] = df["hour"].apply(lambda hour: f"{hour:02d}-{(hour + 1) % 24:02d}")
    activity = df.pivot_table(index="day_name", columns="period", values="message", aggfunc="count").fillna(0)
    return activity


def message_sa(message):
    compound_sentiment = sia.polarity_scores(message)["compound"]
    return "Positive" if compound_sentiment > 0 else "Negative" if compound_sentiment < 0 else "Neutral"


def sentiment_analysis(df_text):
    df_sa = df_text[["user", "message"]].copy()  # Use .copy() to avoid SettingWithCopyWarning
    df_sa.loc[:, "sentiments"] = df_sa["message"].apply(message_sa)  # Use .loc to avoid SettingWithCopyWarning
    df_sa = df_sa.loc[df_sa["sentiments"] != "Neutral"].sort_values(by=["sentiments"], ascending=True)
    return df_sa
