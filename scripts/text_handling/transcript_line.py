class TranscriptLine:
    text: str
    start: float
    duration: float

    def __init__(self, text: str, start: float, duration: float):
        self.text = text
        self.start = start
        self.duration = duration
