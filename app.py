import sys
import os
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import ConversationChain
from langchain.chat_models.openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.memory.motorhead_memory import MotorheadMemory
import dotenv
from simple_chalk import chalk
import asyncio



dotenv.load_dotenv()

# Create a class for the Readline Interface
class ReadlineInterface:
    def __init__(self):
        pass

    def question(self, text):
        sys.stdout.write(chalk.green(text + ' '))
        return input()
rl = ReadlineInterface()

# Set up the input and output
input_stream = sys.stdin
output_stream = sys.stdout


# Create a New Chat Instance

chat = ChatOpenAI(
    temperature=0,
    streaming=True,
    callbacks= [StreamingStdOutCallbackHandler()],
)

# Create a New Memory Instance

memory = MotorheadMemory(
    return_messages=True,
    memory_key="history",
    session_id=os.getenv("SESSION_ID"),
    url=os.getenv("MOTORHEAD_URL"),
)


async def initialize_memory():
    await memory.init()

# Set up the Chat Prompt Template

context = ""

if memory.context:
    context = f"Here's previous context: {memory.context}"

system_prompt = f"You are a helpful assistant.{context}"

chat_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}"),
    ]
)

# Set up the Conversation Chain
chain = ConversationChain(memory=memory, prompt=chat_prompt, llm=chat)

# Create a Function to Post Messages to Shell

async def post_to_shell(res):
    answer = rl.question(chalk.green("\n"))
    res = chain.run(input=answer)
    await post_to_shell(res)

# Start the Conversation

async def start_conversation():
    answer = rl.question(chalk.blue("\nMotorhead 🤘chat start\n"))
    res = chain.run(input=answer)
    await post_to_shell(res)

# Run the Conversation
async def main():
    await initialize_memory()
    await start_conversation()

asyncio.run(main())
