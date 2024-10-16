import asyncio
import websockets
import wave
import io
import subprocess
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

# 初始化模型
model_dir = "iic/SenseVoiceSmall"
model = AutoModel(
    model=model_dir,
    vad_model="fsmn-vad",
    vad_kwargs={"max_single_segment_time": 30000},
    device="cuda:0",
)

def webm_to_wav(webm_data):
    input_stream = io.BytesIO(webm_data)
    output_stream = io.BytesIO()
    process = subprocess.Popen(
        ['ffmpeg', '-i', 'pipe:0', '-f', 'wav', 'pipe:1'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    wav_data, stderr = process.communicate(input=input_stream.read())
    if process.returncode != 0:
        raise Exception(f"ffmpeg error: {stderr.decode()}")
    output_stream.write(wav_data)
    output_stream.seek(0)
    return output_stream

def recognize_speech_offline(wav_file_path):
    res = model.generate(
        input=wav_file_path,
        cache={},
        language="auto",
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,
        merge_length_s=15,
    )
    text = rich_transcription_postprocess(res[0]["text"])
    return text

async def recognize(websocket, path):
    async for message in websocket:
        try:
            wav_data = webm_to_wav(message)
            with open("converted_output.wav", "wb") as f:
                f.write(wav_data.getbuffer())
            result_text = recognize_speech_offline("converted_output.wav")
            await websocket.send(result_text)
        except Exception as e:
            await websocket.send(f"Error: {str(e)}")

async def main():
    async with websockets.serve(recognize, "localhost", 8000):
        await asyncio.Future()  # 保持服务器运行

asyncio.run(main())
