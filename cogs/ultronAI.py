import discord
import logging
import openai
import base64
import time
import os
import sys
from dotenv import load_dotenv
from settings import *
from pathlib import Path
from openai import OpenAI, OpenAIError
from discord.ext import commands, tasks

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import settings

logging.basicConfig(
    filename="api_requests.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

openai = OpenAI(
    api_key=os.getenv("OPEN_AI_KEY"),
)

# Chat bot conversation holder
user_conversations = {}
user_last_interaction = {}

TIMEOUT_PERIOD = 300


def restart_bot():
    os.execv(sys.executable, ["python"] + sys.argv)


class ultronAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def reset_user_conversation(self, user_id):
        if user_id in user_conversations:
            user_conversations[user_id] = [{"role": "system", "content": identifier}]
            logging.info(f"Conversation reset for user: {user_id}")

    # Checks for inactive conversations every minute
    @tasks.loop(seconds=60)
    async def check_inactivity(self):
        current_time = time.time()

        for user_id, last_interaction_time in user_last_interaction.items():
            if current_time - last_interaction_time > TIMEOUT_PERIOD:
                self.reset_user_conversation(user_id)
                del user_last_interaction[user_id]

    # Override commands
    @commands.command(prefix="umahag override -")
    async def mu(self, ctx, *, message=None):
        if ctx.author.id == muID:

            # AI Reset Override
            if message == "ai full reset":
                user_conversations[ctx.author.id] = [
                    {"role": "system", "content": identifier}
                ]
                user_last_interaction.clear()
                settings.chatbot = True
                settings.imageGen = False
                settings.TTS = True
                settings.audioGen = False
                await ctx.send("Override initiated: Resetting.")
                return

            # Full Bot Restart Override
            if message == "full bot restart":
                await ctx.send("Override initiated: Rebooting.")
                restart_bot()
                return

            # AI Full Module Shutdown Override
            if message == "ai full shutdown":
                settings.chatbot = False
                settings.imageGen = False
                settings.TTS = False
                settings.audioGen = False
                await ctx.send(
                    "Override initiated: Shutting down all Ultron AI modules."
                )
                return

            # AI Text Module Shutdown Override
            if message == "ai shutdown text":
                settings.chatbot = False
                await ctx.send(
                    "Override initiated: Shutting down Ultron text generation."
                )
                return

            # AI Image Module Shutdown Override
            if message == "ai shutdown image":
                settings.imageGen = False
                await ctx.send(
                    "Override initiated: Shutting down Ultron image generation."
                )
                return

            # AI TTS Module Shutdown Override
            if message == "ai shutdown tts":
                settings.TTS = False
                await ctx.send(
                    "Override initiated: Shutting down Ultron text to speech."
                )
                return

            # AI Audio Module Shutdown Override
            if message == "ai shutdown audio":
                settings.audioGen = False
                await ctx.send(
                    "Override initiated: Shutting down Ultron audio generation."
                )
                return

            if message == None:
                await ctx.send("Specify an override.")
            else:
                await ctx.send("Override not found.")

    # Chat bot
    @commands.Cog.listener()
    async def on_message(self, message):

        overrideFailed = True

        if message.author == self.bot.user:
            return

        # Checks if Ultron Peacekeeper Initiative is enabled
        if settings.chatbot == False:
            await message.channel.send(
                "The Ultron Peacekeeper Initiative is not enabled."
            )
            return

        # Ignore Override Commands
        if message.content.lower().startswith("umahag override -"):
            overrideFailed == False
            return

        # User conversation shut off
        if message.content.lower().startswith("ultron power down"):
            user_conversations[message.author.id] = [
                {"role": "system", "content": identifier}
            ]
            del user_last_interaction[message.author.id]
            await message.channel.send("Powering down...")
            return

        # Restart Protocol
        if message.content.lower().startswith(
            "ultron activate fantastic spider protocol"
        ):
            if message.author.id == muID:
                await message.channel.send("Rebooting...")
                restart_bot()
                return

        # Checks if Ultron AI is called, initiates chatbot
        if message.content.lower().startswith("ultron") or (
            overrideFailed == True
            and message.content.lower().startswith("umahag override -")
        ):
            question = message.content[len("ultron ") :]

            if message.author.id not in user_conversations:
                user_conversations[message.author.id] = [
                    {"role": "system", "content": identifier}
                ]

            user_conversations[message.author.id].append(
                {"role": "user", "content": question}
            )

            user_last_interaction[message.author.id] = time.time()

            try:
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=user_conversations[message.author.id],
                    max_completion_tokens=150,
                )

                answer = response.choices[0].message.content.strip('"')
                user_input_snippet = message.author
                logging.info(
                    f"Username: {message.author}, User Input: '{user_input_snippet}...', Input: {question}, Response: {answer}"
                )
                user_conversations[message.author.id].append(
                    {"role": "assistant", "content": answer}
                )
                await message.channel.send(answer)
            except OpenAIError as e:
                await message.channel.send(f"An error occurred: {e}")
            except Exception as e:
                await message.channel.send(f"An unexpected error occurred: {e}")

    # Image generation
    @commands.command()
    async def create(self, ctx, *, prompt):

        if settings.imageGen == False:
            await ctx.channel.send("Image generation is not enabled.")
            return

        try:
            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            await ctx.channel.send(response.data[0].url)
        except OpenAIError as e:
            await ctx.channel.send(f"An error occurred: {e}")
        except Exception as e:
            await ctx.channel.send(f"An unexpected error occurred: {e}")

    # Text to Speech
    @commands.command()
    async def say(self, ctx, *, prompt):

        if settings.TTS == False:
            await ctx.channel.send("Text to speech is not enabled.")
            return

        try:
            speech_file_path = Path(__file__).parent / "speech.opus"
            with openai.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="onyx",
                input=prompt,
            ) as response:
                response.stream_to_file(speech_file_path)
                ctx.voice_client.play(discord.FFmpegOpusAudio(speech_file_path))
                user_input_snippet = ctx.message.author
                logging.info(
                    f"Username: {ctx.message.author}, User Input: '{user_input_snippet}...', Input: {prompt}, Type: Audio"
                )
                await ctx.message.delete()
        except OpenAIError as e:
            await ctx.channel.send(f"An error occurred: {e}")
        except Exception as e:
            await ctx.channel.send(f"An unexpected error occurred: {e}")

    # Audio Generation
    @commands.command()
    async def ask(self, ctx, *, prompt):

        if settings.audioGen == False:
            await ctx.channel.send("Audio generation is not enabled.")
            return

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-audio-preview",
                modalities=["text", "audio"],
                audio={"voice": "onyx", "format": "opus"},
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=150,
            )

            wav_bytes = base64.b64decode(response.choices[0].message.audio.data)
            with open("audiogen.opus", "wb") as f:
                f.write(wav_bytes)
                ctx.voice_client.play(discord.FFmpegOpusAudio("audiogen.opus"))
        except OpenAIError as e:
            await ctx.channel.send(f"An error occurred: {e}")
        except Exception as e:
            await ctx.channel.send(f"An unexpected error occurred: {e}")


async def setup(bot):
    await bot.add_cog(ultronAI(bot))
