import telebot
import telebot.apihelper
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Your bot token
TOKEN = '8109938861:AAFKL0m1VLW5f5j6URcCDiLLXpcoZRX9MUA'

# SOCKS Proxy Configuration
socks_proxy = "socks5://127.0.0.1:10808"  # Example: "socks5://127.0.0.1:1080"

# Enable SOCKS proxy for requests (telebot uses requests internally)
telebot.apihelper.proxy = {
    'http': socks_proxy,
    'https': socks_proxy
}

# Initialize the bot with the provided token
bot = telebot.TeleBot(TOKEN)

# Game state variables
board = [" "] * 9  # 3x3 Tic-Tac-Toe grid (empty at start)
player_turn = "X"  # Player X starts


# Function to create the board with buttons
def create_board_markup():
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []

    for i in range(9):
        button = InlineKeyboardButton(board[i], callback_data=str(i))  # Use the index as callback data
        buttons.append(button)

    markup.add(*buttons)
    return markup


# Function to handle the callback when a player clicks a button
@bot.callback_query_handler(func=lambda call: True)
def handle_move(call):
    global player_turn

    # Get the position (index) of the button clicked
    position = int(call.data)

    # If the cell is already filled, inform the user and return
    if board[position] != " ":
        bot.answer_callback_query(call.id, "Cell already occupied!")
        return

    # Update the board with the player's move
    board[position] = player_turn

    # Send an updated board
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Player {player_turn}'s turn\n\n" ,
        reply_markup=create_board_markup()
    )

    # Switch to the next player's turn
    player_turn = "O" if player_turn == "X" else "X"



# Handler for the /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        f"Welcome to Tic-Tac-Toe!\n\nPlayer {player_turn}'s turn\n\n" ,
        reply_markup=create_board_markup()
    )


# Start the bot
bot.polling()
