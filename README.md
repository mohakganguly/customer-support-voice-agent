<div align="center">

# 🎙️ Customer Support Voice Agent

### ⚡ Real-Time • Low-Latency • AI-Powered • Voice-First Customer Support

An intelligent real-time customer support voice agent built using modern
Voice AI infrastructure.

The system listens to customer queries, converts speech into text,
reasons using a Large Language Model, and generates natural spoken
responses — all in real time.

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LiveKit](https://img.shields.io/badge/LiveKit-Agents-FF6B6B?style=for-the-badge)](https://livekit.io/)
[![Groq](https://img.shields.io/badge/Groq-LPU-FF6B35?style=for-the-badge)](https://groq.com/)
[![AssemblyAI](https://img.shields.io/badge/AssemblyAI-STT-7C3AED?style=for-the-badge)](https://www.assemblyai.com/)
[![Deepgram](https://img.shields.io/badge/Deepgram-TTS-13EF93?style=for-the-badge)](https://deepgram.com/)

</div>

---

# 🚀 Overview

Customer support is evolving from traditional chatbots to **real-time conversational voice agents**.

This project implements a low-latency voice pipeline capable of:

🎤 Listening to the customer in real time  
📝 Streaming speech-to-text transcription  
🧠 Understanding the customer's intent using an LLM  
💬 Generating contextual support responses  
🔊 Converting responses back into natural speech  
⚡ Delivering the response with minimal latency  

The agent is designed using a modular architecture that allows individual
components such as STT, LLM, and TTS providers to be replaced easily.

---

# 🧠 System Architecture

```text
                    🎤 CUSTOMER

                        │
                        ▼

              ┌──────────────────┐
              │  Microphone Input │
              └──────────────────┘

                        │
                        ▼

              ┌──────────────────┐
              │      LiveKit      │
              │  Real-Time Audio  │
              │    Transport      │
              └──────────────────┘

                        │
                        ▼

              ┌──────────────────┐
              │       VAD        │
              │ Voice Activity   │
              │    Detection     │
              └──────────────────┘

                        │
                        ▼

              ┌──────────────────┐
              │   AssemblyAI     │
              │ Streaming Speech │
              │    To Text       │
              └──────────────────┘

                        │
                        ▼

                 USER TRANSCRIPT

                        │
                        ▼

              ┌──────────────────┐
              │      GROQ        │
              │  Large Language  │
              │      Model       │
              └──────────────────┘

                        │
                        ▼

                 AI RESPONSE

                        │
                        ▼

              ┌──────────────────┐
              │    Deepgram      │
              │ Text To Speech   │
              └──────────────────┘

                        │
                        ▼

                 🔊 SPEAKER

                        │
                        ▼

                    CUSTOMER