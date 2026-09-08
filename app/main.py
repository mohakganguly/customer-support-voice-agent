from dotenv import load_dotenv

from livekit.agents import (
    AgentServer,
    AgentSession,
    JobContext,
    cli,
    inference
)

from livekit.plugins import groq,assemblyai

from app.agent import CustomerSupportAgent


load_dotenv()


server = AgentServer()


@server.rtc_session(agent_name="customer-support-agent")
async def entrypoint(ctx: JobContext):

    print("🚀 Agent job received!")
    print(f"📍 Room: {ctx.room.name}")

    await ctx.connect()

    print("✅ Agent connected to room")

    session = AgentSession(
        stt=assemblyai.STT(
            # model="universal-streaming-english",
        ),

        llm=groq.LLM(
            model="openai/gpt-oss-20b"
        ),

         tts=inference.TTS(
            model="deepgram/aura-2",
            voice="athena",
            language="en",
        ),
    )
    await session.start(
        room=ctx.room,
        agent=CustomerSupportAgent(),
    )

    print("🤖 Customer Support Agent session started")


if __name__ == "__main__":
    cli.run_app(server)