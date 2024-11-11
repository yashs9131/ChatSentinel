import re
import emoji
import pandas as pd
from datetime import datetime


def preprocess(data, time_format):
    """It preprocesses the given input file to form a DataFrame of meaningful features"""

    pattern = ""
    if time_format == "12 hour clock":
        pattern = r"\d{1,4}/\d{1,4}/\d{1,4},\s\d{1,2}:\d{1,2}\s\w{2}\s-\s"
    elif time_format == "24 hour clock":
        pattern = r"\d{1,4}/\d{1,4}/\d{1,4},\s\d{1,2}:\d{1,2}\s-\s"
    user_messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({"user_message": user_messages, "message_date": dates})

    datetime_formats = {
        "24 hour clock": [
            '%d/%m/%y, %H:%M - ',
            '%m/%d/%y, %H:%M - ',
            '%d/%m/%Y, %H:%M - ',
            '%m/%d/%Y, %H:%M - '
        ],
        "12 hour clock": [
            '%d/%m/%y, %I:%M %p - ',
            '%m/%d/%y, %I:%M %p - ',
            '%d/%m/%Y, %I:%M %p - ',
            '%m/%d/%Y, %I:%M %p - '
        ]
    }

    for fmt in datetime_formats[time_format]:
        try:
            df["message_date"] = pd.to_datetime(df["message_date"], format=fmt)
            break
        except ValueError:
            continue

    df.rename(columns={"message_date": "date"}, inplace=True)

    # Separating Users and Text Messages
    users = []
    messages = []
    for message in df["user_message"]:
        entry = re.split(r"([\w\W]+?):\s", message)
        if len(entry) > 1:  # User Name
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append("Notification")
            messages.append(entry[0])

    df["user"] = users
    df["message"] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Dropping notifications
    df = df[df["user"] != "Notification"].reset_index(drop=True)

    # Dropping and counting deleted messages by different users
    df_deleted = df[(df["message"] == "This message was deleted\n") | (df["message"] == "You deleted this message\n")].reset_index(drop=True)
    df = df[(df["message"] != "This message was deleted\n") & (df["message"] != "You deleted this message\n")].reset_index(drop=True)

    df["year"] = df["date"].dt.year
    df["day"] = df["date"].dt.day
    df["hour"] = df["date"].dt.hour
    df["minute"] = df["date"].dt.minute
    df["month_num"] = df["date"].dt.month
    df["only_date"] = df["date"].dt.date
    df["day_name"] = df["date"].dt.day_name()

    df["month"] = df["date"].dt.strftime('%B')

    # Creating a separate Dataframe for emojis and removing from the current dataframe
    df["emojis"] = df["message"].apply(lambda x: len([c for c in x if c in emoji.EMOJI_DATA]))

    # Extracting rows with emojis in message
    df_emoji = df[df['emojis'] != 0].reset_index(drop=True)

    # Dropping extra feature
    df.drop(["emojis"], axis=1, inplace=True)

    # Removing emojis from current dataframe
    df["message"] = df["message"].apply(lambda x: emoji.replace_emoji(x, replace=''))

    # Till we don't have a use for the deleted messages dataset, we will only return its length.
    return df, df_deleted, df_emoji
