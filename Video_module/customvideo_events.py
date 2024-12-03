import av
import time
import fractions
import asyncio
from av import VideoFrame
from vsaiortc.mediastreams import MediaStreamError
from videosdk import CustomVideoTrack, MeetingConfig, VideoSDK, Participant, MeetingEventHandler, ParticipantEventHandler

# VIDEOSDK_TOKEN = "VIDEOSDK_TOKEN"
# MEETING_ID = "MEETING_ID"
# NAME = "NAME"
loop = asyncio.get_event_loop()

class VideoFileTrack(CustomVideoTrack):

    def __init__(self, path: str):
        super().__init__()  # Initialize the parent class
        self.kind = "video"
        self.path = path
        self.container = av.open(path)
        self.stream = self.container.streams.video[0]
        self._start = time.time()
        self._timestamp = 0

    async def recv(self) -> VideoFrame:

        # Timestamp Management
        pts, time_base = await self.next_timestamp()

        # Packet Decoding & Error Handling
        # Read next frame from the video file
        frame = None
        for packet in self.container.demux(self.stream):
            try:
                for video_frame in packet.decode():
                    frame = video_frame
                    break
                if frame:
                    break
            except EOFError:
                self.container.seek(0)
            finally:
                pass

        frame.pts = pts
        frame.time_base = time_base
        return frame

    async def next_timestamp(self) -> tuple[int, fractions.Fraction]:
        VIDEO_PTIME = 1 / 30  # Packet time for 30fps
        VIDEO_CLOCK_RATE = 90000  # Clock rate for video
        VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)

        if self.readyState != "live":
            raise MediaStreamError

        if hasattr(self, "_timestamp"):
            self._timestamp += int(VIDEO_PTIME * VIDEO_CLOCK_RATE)
            wait = self._start + (self._timestamp /
                                  VIDEO_CLOCK_RATE) - time.time()
            await asyncio.sleep(max(0, wait))
        else:
            self._start = time.time()
            self._timestamp = 0
        return self._timestamp, VIDEO_TIME_BASE