import random
from tqdm import tqdm
import pickle

# Game and Policy Classes (same as before)
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

class ValuePolicy:
    DEFAULT_VALUE = 0.5

    def __init__(self):
        self.values = {}

    def policy(self, game):
        move_values = {}
        moves = game.valid_moves()
        for move in moves:
            next = game.make_move(move, AGENT)
            move_values[move] = self.get_state_value(next)
        return max(move_values, key=move_values.get)

    def get_state_value(self, state):
        if str(state) not in self.values:
            return self.DEFAULT_VALUE
        return self.values[str(state)]

    def set_state_value(self, state, value):
        self.values[str(state)] = value

    def learn(self, states):
        def temporal_difference(current_state_value, next_state_value):
            learning_rate = 0.1
            return current_state_value + learning_rate * (next_state_value - current_state_value)

        last_state = states[-1:][0]
        last_value = reward(last_state)
        self.set_state_value(last_state, last_value)
        for state in reversed(states[:-1]):
            value = self.get_state_value(state)
            last_value = temporal_difference(value, last_value)
            self.set_state_value(state, last_value)

# Reward function
def reward(game):
    return max(game.get_winner(), 0)

# Opponent policies
def random_policy(game):
    return random.choice(game.valid_moves())

def semi_random_policy(game):
    for move in game.valid_moves():
        next_game = game.make_move(move, OPPONENT)
        if next_game.get_winner() == OPPONENT:
            return move
    return random.choice(game.valid_moves())

def blocking_policy(game):
    for move in game.valid_moves():
        next_game = game.make_move(move, AGENT)
        if next_game.get_winner() == AGENT:
            return move
    return random.choice(game.valid_moves())

# Training function
def train(policy, opponent_policy, training_games=1000):
    for _ in tqdm(range(training_games), desc="Training", unit="game"):
        game = Game()
        if random.random() > 0.5:
            game = game.make_move(opponent_policy(game), OPPONENT)

        states = []
        while not game.is_finished():
            if random.random() < 0.1:  # Exploration
                game = game.make_move(random.choice(game.valid_moves()), AGENT)
            else:
                game = game.make_move(policy.policy(game), AGENT)
            states.append(game)
            if game.is_finished():
                break
            game = game.make_move(opponent_policy(game), OPPONENT)
            states.append(game)

        policy.learn(states)

# Main training process
if __name__ == "__main__":
    policy = ValuePolicy()

    print("🤖 Starting training process...")
    print("🔰 Phase 1/3: Training against Random Opponent")
    train(policy, random_policy, 1000)

    print("🧠 Phase 2/3: Training against Semi-Smart Opponent")
    train(policy, semi_random_policy, 1000)

    print("🛡️ Phase 3/3: Training against Defensive Opponent")
    train(policy, blocking_policy, 1000)

    # Save the trained policy
    with open("trained_policy.pkl", "wb") as f:
        pickle.dump(policy, f)

    print("🎉 Training complete! Policy saved to 'trained_policy.pkl'.")