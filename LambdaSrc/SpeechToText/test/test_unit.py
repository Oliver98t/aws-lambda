from LambdaSrc.SpeechToText.Index import Transcribe

def test_transcribe():
    transcribe = Transcribe(bucket="ainterviewupload", user="test")
    transcription = transcribe.transcribe()
    test_trasncription = "Give me a series of Python interview questions."
    assert transcription == test_trasncription