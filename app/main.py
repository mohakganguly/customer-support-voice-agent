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
from app.session_state import SupportSessionState

from app.memory import MemoryExtractor
from backend.memory_repository import save_memory

load_dotenv()


server = AgentServer()

async def extract_and_save_memories(session):
    customer_id = session.userdata.customer_id

    if not customer_id:
        print("🧠 No customer identified. Skipping memory extraction.")
        return

    history = session.history

    conversation = "\n".join(
        f"{item.role}: {item.content}"
        for item in history.items
        if item.content
    )

    if not conversation.strip():
        return

    extractor = MemoryExtractor()

    memories = await extractor.extract(conversation)

    for memory in memories:
        save_memory(
            customer_id=customer_id,
            key=memory.key,
            value=memory.value,
            category=memory.category,
        )

        print(
            f"🧠 Saved memory: "
            f"{memory.key} = {memory.value}"
        )

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
        userdata=SupportSessionState(),
    )
    @session.on("close")
    async def on_session_close(event):
        print("🔴 Session closed")
        await extract_and_save_memories(session)

    await session.start(
        room=ctx.room,
        agent=CustomerSupportAgent(),
    )
    try:
        await session.shutdown()
    finally:
        await extract_and_save_memories(session)


    print("🤖 Customer Support Agent session started")


if __name__ == "__main__":
    cli.run_app(server)