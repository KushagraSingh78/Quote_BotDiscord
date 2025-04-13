import discord
import os
import random
import aiohttp  # For asynchronous HTTP requests
import json
from dotenv import load_dotenv

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
QUOTES_URL = "https://raw.githubusercontent.com/KushagraSingh78/HollowQuotes/refs/heads/main/quotes.json"

# --- Bot Setup ---
# Define the intents your bot needs
intents = discord.Intents.default()
intents.message_content = True  # <<< REQUIRED TO READ MESSAGE CONTENT

# Create the Bot instance (using discord.Client as we only need on_message)
# Using commands.Bot would also work if you plan to add commands later
client = discord.Client(intents=intents)

# --- Quote Fetching Function ---
async def fetch_quotes():
    """Fetches the quotes list from the specified URL."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(QUOTES_URL) as response:
                if response.status == 200:
                    try:
                        # Read the response text and parse it as JSON
                        data = await response.json(content_type=None) # content_type=None bypasses strict content type check
                        if isinstance(data, list):
                            return data # Return the list of quotes
                        else:
                            print(f"Error: Fetched data is not a list.")
                            return None
                    except json.JSONDecodeError:
                        print(f"Error: Failed to decode JSON from {QUOTES_URL}")
                        return None
                else:
                    print(f"Error: Failed to fetch quotes. Status code: {response.status}")
                    return None
        except aiohttp.ClientError as e:
            print(f"Error: Network error while fetching quotes: {e}")
            return None

# --- Event Handlers ---
@client.event
async def on_ready():
    """Runs when the bot is connected and ready."""
    print(f'Logged in as {client.user.name} ({client.user.id})')
    print('Bot is ready to listen for mentions!')
    print('------')

@client.event
async def on_message(message):
    """Runs whenever a message is sent in a channel the bot can see."""
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # Check if the bot was mentioned in the message
    if client.user in message.mentions:
        # The bot was mentioned. Now check if "quote" follows the mention.

        # Get the mention string for the bot (handles nicknames too)
        bot_mention_string = client.user.mention

        # Clean the message content slightly for easier parsing
        # Remove the bot's mention from the start/within the message text
        # Using partition allows us to get text reliably *after* the first mention
        _, _, text_after_mention = message.content.partition(bot_mention_string)
        cleaned_text = text_after_mention.strip() # Remove leading/trailing whitespace

        # Check if the first word after the mention is "quote" (case-insensitive)
        if cleaned_text.lower().startswith("quote"):
            print(f"Mention detected with 'quote' from {message.author.name}")

            # Fetch the quotes
            quotes_list = await fetch_quotes()

            if quotes_list:
                # Select a random quote dictionary from the list
                random_quote_dict = random.choice(quotes_list)

                # Extract text and author, providing defaults if keys are missing
                quote_text = random_quote_dict.get('text', 'Quote text not found.')
                quote_author = random_quote_dict.get('author', 'Unknown Author')

                # Format the reply
                reply = f'> "{quote_text}"\n> \n> – *{quote_author}*' # Using Discord blockquote formatting

                # Send the reply to the channel where the message was sent
                await message.channel.send(reply)
                print(f"Replied with quote by {quote_author}")
            else:
                # Send an error message if quotes couldn't be fetched or parsed
                await message.channel.send("Sorry, I couldn't fetch a quote right now.")
                print("Failed to fetch or parse quotes.")

# --- Running the Bot ---
if TOKEN is None:
    print("ERROR: DISCORD_TOKEN environment variable not found.")
    print("Make sure you have created a .env file with DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE")
else:
    try:
        print("Attempting to log in...")
        client.run(TOKEN)
    except discord.errors.LoginFailure:
        print("\nERROR: Improper token passed.")
        print("Make sure you have the correct bot token in your .env file and that it's spelled DISCORD_TOKEN.")
    except discord.errors.PrivilegedIntentsRequired:
        print("\nERROR: Privileged Intents (like Message Content) are required but not enabled.")
        print("Go to your bot's settings on the Discord Developer Portal and enable the 'Message Content Intent'.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")