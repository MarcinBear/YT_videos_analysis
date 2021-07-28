# this code is based on great yt API tutorials made by "Python Engineer"
# https://www.youtube.com/playlist?list=PLqnslRFeH2UpC8EqlF2aax9A-VLiPDwxP

import requests
import json
from tqdm import tqdm


class YoutubeStats:

    def __init__(self, api_key, channel_id):
        self.api_key = api_key
        self.channel_id = channel_id
        self.video_data = None

    def get_channel_video_data(self):
        channel_videos = self._get_channel_videos(limit=50)
        parts = ["snippet", "statistics", "contentDetails"]
        for video_id in tqdm(channel_videos):
            for part in parts:
                data = self._get_single_video_data(video_id, part)
                channel_videos[video_id].update(data)
        self.video_data = channel_videos
        return channel_videos

    def _get_single_video_data(self, video_id, part):
        url = f'https://www.googleapis.com/youtube/v3/videos?part={part}&id={video_id}&key={self.api_key}'
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        try:
            data = data['items'][0][part]
        except KeyError:
            print('expected part not found')
            data = dict()
        return data

    def _get_channel_videos(self, limit=None, max_pages=10):
        url = f'https://www.googleapis.com/youtube/v3/search?key={self.api_key}&channelId={self.channel_id}&part=id&order=date'
        if limit is not None and isinstance(limit, int):
            url += "&maxResults=" + str(limit)
        videos, npt = self._get_channel_videos_per_page(url)  # npt - next page token (results are by default limited to 50 per page)
        index = 0
        while npt is not None and index < max_pages:
            nexturl = url + '&pageToken=' + npt
            next_videos, npt = self._get_channel_videos_per_page(nexturl)
            videos.update(next_videos)
            index += 1
        return videos

    def _get_channel_videos_per_page(self, url):
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        channel_videos = dict()
        if 'items' not in data:
            return channel_videos, None
        item_data = data['items']
        nextPageToken = data.get("nextPageToken", None)
        for item in item_data:
            try:
                kind = item['id']['kind']
                if kind == 'youtube#video':
                    video_id = item['id']['videoId']
                    channel_videos[video_id] = dict()
            except KeyError:
                pass
        return channel_videos, nextPageToken

    def dump(self):
        if self.video_data is None:
            print('data not found')
            return

        channel_title = self.video_data.popitem()[1].get('channelTitle', self.channel_id)
        channel_title = channel_title.replace(' ', '_').lower()
        file_name = channel_title + '.json'
        with open(file_name, 'w') as f:
            json.dump(self.video_data, f, indent=4)
        print('file dumped')
