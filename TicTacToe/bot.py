import telebot
import telebot.apihelper
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import pickle
from teacher import ValuePolicy

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

# RL Game Logic
AGENT = 1
OPPONENT = -1
NO_PLAYER = 0

class Game:
    def __init__(self, game_state=None):
        if game_state is None:
            game_state = [
                0, 0, 0,
                0, 0, 0,
                0, 0, 0
            ]
        self.state = game_state

    def __str__(self):
        return str(self.state)

    def is_draw(self):
        return len([field for field in self.state if field == NO_PLAYER]) == 0

    def is_finished(self):
        return self.get_winner() != NO_PLAYER or self.is_draw()

    def valid_moves(self):
        return [i for i in range(9) if self.state[i] == NO_PLAYER]

    def make_move(self, field, player):
        next = list(self.state)
        next[field] = player
        return Game(next)

    def get_winner(self):
        state = self.state
        for i in range(3):
            if state[i * 3] == state[i * 3 + 1] == state[i * 3 + 2] == state[i * 3] != NO_PLAYER:
                return state[i * 3]
            if state[i] == state[i + 3] == state[i + 6] == state[i] != NO_PLAYER:
                return state[i]
            if state[0] == state[4] == state[8] == state[0] != NO_PLAYER:
                return state[0]
            if state[2] == state[4] == state[6] == state[2] != NO_PLAYER:
                return state[2]
        return NO_PLAYER

# Load the pre-trained policy
with open("trained_policy.pkl", "rb") as f:
    policy = pickle.load(f)

# Game state variables
games = {}  # Store game states for each chat

# Function to create the board with buttons
def create_board_markup(game):
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []

    for i in range(9):
        cell = " "
        if game.state[i] == AGENT:
            cell = "X"
        elif game.state[i] == OPPONENT:
            cell = "O"
        button = InlineKeyboardButton(cell, callback_data=str(i))
        buttons.append(button)

    markup.add(*buttons)
    return markup

# Function to handle the callback when a player clicks a button
@bot.callback_query_handler(func=lambda call: True)
def handle_move(call):
    chat_id = call.message.chat.id
    if chat_id not in games:
        bot.answer_callback_query(call.id, "No active game!")
        return

    game = games[chat_id]
    position = int(call.data)

    if game.state[position] != NO_PLAYER:
        bot.answer_callback_query(call.id, "Cell already occupied!")
        return

    # Player makes a move
    game = game.make_move(position, OPPONENT)
    games[chat_id] = game

    if game.is_finished():
        winner = game.get_winner()
        if winner == OPPONENT:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="You win!", reply_markup=create_board_markup(game))
        elif winner == NO_PLAYER:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="It's a draw!", reply_markup=create_board_markup(game))
        del games[chat_id]
        return

    # Agent makes a move
    agent_move = policy.policy(game)
    game = game.make_move(agent_move, AGENT)
    games[chat_id] = game

    if game.is_finished():
        winner = game.get_winner()
        if winner == AGENT:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="I win!", reply_markup=create_board_markup(game))
        elif winner == NO_PLAYER:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="It's a draw!", reply_markup=create_board_markup(game))
        del games[chat_id]
        return

    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Your turn!", reply_markup=create_board_markup(game))

# Handler for the /start command
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    games[chat_id] = Game()
    bot.send_message(chat_id, "Welcome to Tic-Tac-Toe! You are O, I am X. Your turn!", reply_markup=create_board_markup(games[chat_id]))

# Start the bot
bot.polling()