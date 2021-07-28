from youtube_statistics import YoutubeStats

API_KEY = "****************************" # your secret API key 
channel_id = "UCYO_jab_esuFRV4b17AJtAw"  # 3Blue1Brown channel id


if __name__ == "__main__":
    yt = YoutubeStats(API_KEY, channel_id)
    yt.get_channel_video_data()
    yt.dump()
