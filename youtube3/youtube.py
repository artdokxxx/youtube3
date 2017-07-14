#!/usr/bin/python
import httplib2
import os
import sys
from youtube3.common import *
from apiclient import discovery
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow


def get_authenticated_service( args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=YOUTUBE_READ_WRITE_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                           http=credentials.authorize(httplib2.Http()))


class Youtube :
    def __init__(self,youtube):
        self.youtube = youtube

    def list_channels(self,id):
        return self.youtube.channels().list(part="contentDetails",id=id).execute()

    def like_video(self, video_id):
        self.youtube.videos().rate(
        id=video_id,
        rating="like"
      ).execute()


    def get_video(self, video_id):
      return self.youtube.videos().list(
        id=video_id,
        part='snippet'
      ).execute()

    def get_recommended(self):
        return self.youtube.activities().list(
            part='snippet',mine=True
        ).execute()

    def get_channel_id(self, videoId):
        result = self.get_video(videoId)
        channelId= result['items'][0]['snippet']['channelId']
        return channelId

    def get_related_videos(self, videoId,nextPageToken=None):
        return self.youtube.search().list(
            part='snippet', type="video", relatedToVideoId=videoId, pageToken=nextPageToken
        ).execute()


    def get_channels(self):
        return self.youtube.channels().list(
            part='contentDetails', mine="true"
        ).execute()

    def liked_channel(self):
        channels = self.youtube.channels().list(
            part='snippet,contentDetails', mine="true"
        ).execute()
        try:
            return channels['items'][0]['contentDetails']['relatedPlaylists']['likes']
        except:
            return None

    def videos_in_channels(self, channelId, nextPageToken=None):

        playlistItems = self.youtube.playlistItems().list(
            part='snippet,contentDetails', playlistId=channelId, pageToken=nextPageToken
        ).execute()
        return playlistItems

    def iterate_videos_in_channel(self, channelId,maxCount=None):
        count = 0
        videos = self.videos_in_channels(channelId)
        yield videos
        count += 1
        while 'nextPageToken' in videos:
            videos = self.videos_in_channels(channelId,videos['nextPageToken'])
            yield videos
            count += 1
            if maxCount and count > int(maxCount):
                break

    def iterate_related_videos(self, videoId,maxCount=None):
        count = 0
        videos = self.get_related_videos(videoId)
        yield videos
        count += 1
        while 'nextPageToken' in videos:
            videos = self.get_related_videos(videoId,videos ['nextPageToken'])
            yield videos
            count  += 1
            if maxCount and count > int(maxCount):
                break

    def subscribe_channel(self, channelId):
        self.youtube.subscriptions().insert(
            part='snippet',
            body=dict(
                snippet=dict(
                    resourceId=dict(
                        channelId=channelId
                    )
                )
            )).execute()
