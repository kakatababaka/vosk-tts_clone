#!/usr/bin/env python3
#
# Copyright 2023 Alpha Cephei Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the gRPC TTS server."""

from concurrent import futures
import os
import sys
import time
import math
import logging
import grpc
import time

import tts_service_pb2
import tts_service_pb2_grpc

from vosk_tts import Model, Synth

vosk_interface = os.environ.get('VOSK_SERVER_INTERFACE', '0.0.0.0')
vosk_port = int(os.environ.get('VOSK_SERVER_PORT', 5001))
vosk_model_path = os.environ.get('VOSK_MODEL_PATH', 'vosk-model-tts-ru-0.1-natasha')
vosk_threads = int(os.environ.get('VOSK_SERVER_THREADS', os.cpu_count() or 1))

class SynthesizerServicer(tts_service_pb2_grpc.SynthesizerServicer):
    def __init__(self):
        self.model = Model(model_path=vosk_model_path)
        self.synth = Synth(self.model)

    def UtteranceSynthesis(self, request, context):
        print (request)
        audio = self.synth.synth_audio(request.text)
        yield tts_service_pb2.UtteranceSynthesisResponse(audio_chunk=tts_service_pb2.AudioChunk(data=audio.tobytes()))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(vosk_threads))
    tts_service_pb2_grpc.add_SynthesizerServicer_to_server(SynthesizerServicer(), server)

    server.add_insecure_port('{}:{}'.format(vosk_interface, vosk_port))
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()