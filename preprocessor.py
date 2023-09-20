import re
import emoji
import pandas as pd


def preprocess(data, time_format):
    """It preprocesses the given input file to form a DataFrame of meaningful features"""

    pattern = ""
    if time_format == "12 hour clock":
        pattern = "\d{1,4}\/\d{1,4}\/\d{1,4},\s\d{1,2}:\d{1,2}\s\w{2}\s-\s"
    elif time_format == "24 hour clock":
        pattern = "\d{1,4}/\d{1,4}/\d{1,4},\s\d{1,2}:\d{1,2}\s-\s"
    user_messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({"user_message": user_messages, "message_date": dates})

    if time_format == "24 hour clock":
        try:  # DD/MM/YY, HH:MM -
            df["message_date"] = pd.to_datetime(df["message_date"], format='%-d/%-m/%y, %H:%M - ')
        except ValueError:
            try:  # DD/MM/YY, HH:MM -
                df["message_date"] = pd.to_datetime(df["message_date"], format='%d/%m/%y, %H:%M - ')
            except ValueError:
                try:  # MM/DD/YY, HH:MM -
                    df["message_date"] = pd.to_datetime(df["message_date"], format='%-m/%-d/%y, %H:%M - ')
                except ValueError:
                    try:  # MM/DD/YY, HH:MM -
                        df["message_date"] = pd.to_datetime(df["message_date"], format='%m/%d/%y, %H:%M - ')
                    except ValueError:
                        try:  # MM/DD/YYYY, HH:MM -
                            df["message_date"] = pd.to_datetime(df["message_date"], format='%-m/%-d/%Y, %H:%M - ')
                        except ValueError:
                            try:  # MM/DD/YYYY, HH:MM -
                                df["message_date"] = pd.to_datetime(df["message_date"], format='%m/%d/%Y, %H:%M - ')
                            except ValueError:
                                try:  # DD/MM/YYYY, HH:MM -
                                    df["message_date"] = pd.to_datetime(df["message_date"], format='%-d/%-m/%Y, %H:%M - ')
                                except ValueError: # DD/MM/YYYY, HH:MM -
                                    df["message_date"] = pd.to_datetime(df["message_date"], format='%d/%m/%Y, %H:%M - ')

    elif time_format == "12 hour clock":
        try:  # DD/MM/YY, hh:mm (AM/PM) -
            df["message_date"] = pd.to_datetime(df["message_date"], format='%-d/%-m/%y, %-I:%M %p - ')
        except ValueError:
            try:  # DD/MM/YY, hh:mm (AM/PM) -
                df["message_date"] = pd.to_datetime(df["message_date"], format='%d/%m/%y, %-I:%M %p - ')
            except ValueError:
                try:  # MM/DD/YY, hh:mm (AM/PM) -
                    df["message_date"] = pd.to_datetime(df["message_date"], format='%-m/%-d/%y, %-I:%M %p - ')
                except ValueError:
                    try:  # MM/DD/YY, hh:mm (AM/PM) -
                        df["message_date"] = pd.to_datetime(df["message_date"], format='%m/%d/%y, %-I:%M %p - ')
                    except ValueError:
                        try: # MM/DD/YYYY, hh:mm (AM/PM) -
                            df["message_date"] = pd.to_datetime(df["message_date"], format='%-m/%-d/%Y, %-I:%M %p - ')
                        except ValueError:
                            try:  # MM/DD/YYYY, hh:mm (AM/PM) -
                                df["message_date"] = pd.to_datetime(df["message_date"], format='%m/%d/%Y, %-I:%M %p - ')
                            except ValueError:
                                try:  # DD/MM/YYYY, hh:mm (AM/PM) -
                                    df["message_date"] = pd.to_datetime(df["message_date"], format='%-d/%-m/%Y, %-I:%M %p - ')
                                except ValueError:
                                    try:  # DD/MM/YYYY, hh:mm (AM/PM) -
                                        df["message_date"] = pd.to_datetime(df["message_date"], format='%d/%m/%Y, %-I:%M %p - ')
                                    except ValueError:
                                        try:  # DD/MM/YY, hh:mm (AM/PM) -
                                            df["message_date"] = pd.to_datetime(df["message_date"], format='%-d/%-m/%y, %I:%M %p - ')
                                        except ValueError:
                                            try:  # DD/MM/YY, hh:mm (AM/PM) -
                                                df["message_date"] = pd.to_datetime(df["message_date"], format='%d/%m/%y, %I:%M %p - ')
                                            except ValueError:
                                                try:  # MM/DD/YY, hh:mm (AM/PM) -
                                                    df["message_date"] = pd.to_datetime(df["message_date"], format='%-m/%-d/%y, %I:%M %p - ')
                                                except ValueError:
                                                    try:  # MM/DD/YY, hh:mm (AM/PM) -
                                                        df["message_date"] = pd.to_datetime(df["message_date"], format='%m/%d/%y, %I:%M %p - ')
                                                    except ValueError:
                                                        try:  # MM/DD/YYYY, hh:mm (AM/PM) -
                                                            df["message_date"] = pd.to_datetime(df["message_date"], format='%-m/%-d/%Y, %I:%M %p - ')
                                                        except ValueError:
                                                            try:  # MM/DD/YYYY, hh:mm (AM/PM) -
                                                                df["message_date"] = pd.to_datetime(df["message_date"], format='%m/%d/%Y, %I:%M %p - ')
                                                            except ValueError:
                                                                try:  # DD/MM/YYYY, hh:mm (AM/PM) -
                                                                    df["message_date"] = pd.to_datetime(df["message_date"], format='%-d/%-m/%Y, %I:%M %p - ')
                                                                except ValueError:  # DD/MM/YYYY, hh:mm (AM/PM) -
                                                                    df["message_date"] = pd.to_datetime(df["message_date"], format='%d/%m/%Y, %I:%M %p - ')

    df.rename(columns={"message_date": "date"}, inplace=True)

    # Separating Users and Text Messages
    users = []
    messages = []
    for message in df["user_message"]:
        entry = re.split("([\w\W]+?):\s", message)
        if entry[1:]:  # User Name
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
    df_deleted = df[(df["message"] == "This message was deleted\n") | (df["message"] == "You deleted this message\n")]\
        .reset_index(drop=True)
    df = df[(df["message"] != "This message was deleted\n") & (df["message"] != "You deleted this message\n")]\
        .reset_index(drop=True)

    df["year"] = df["date"].dt.year
    df["day"] = df["date"].dt.day
    df["hour"] = df["date"].dt.hour
    df["minute"] = df["date"].dt.minute
    df["month_num"] = df["date"].dt.month
    df["only_date"] = df["date"].dt.date
    df["day_name"] = df["date"].dt.day_name()

    months = []
    month_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                  "November", "December"]

    for date in df["date"]:
        months.append(month_list[int(date.month) - 1])

    df["month"] = months

    # Creating a separate Dataframe for emojis and removing from the current dataframe
    df["emojis"] = df["message"].apply(emoji.emoji_count)

    # Extracting rows with emojis in message
    df_emoji = df[df['emojis'] != 0].reset_index(drop=True)

    # Dropping extra feature
    df.drop(["emojis"], axis=1, inplace=True)

    # Removing emojis from current dataframe
    df["message"] = df["message"].apply(emoji.replace_emoji)

    # Till we don't have a use for the deleted messages dataset, we will only return its length.
    return df, df_deleted, df_emoji
