import chess
import random
from stockfish import Stockfish

# Set the path to your Stockfish binary (update this path as needed)
STOCKFISH_PATH = "./stockfish"  # Replace with your actual path, e.g., "/usr/local/bin/stockfish"


####################################
# Fake Leaderboard Implementation  #
####################################
class FakeLeaderboard:
    def __init__(self):
        # Pre-generated competitor ratings
        self.competitors = [
            {"name": "Grandmaster Gizmo", "rating": 2800},
            {"name": "Pawnstar Prodigy", "rating": 2650},
            {"name": "Knightmare", "rating": 2500},
            {"name": "Queen's Gambit", "rating": 2400},
            {"name": "Rook 'n Roll", "rating": 2300},
        ]
        # Initialize player's fake rating
        self.player_rating = 2000

    def update_rating(self, result):
        # Adjust player rating based on game result.
        # (These are arbitrary numbers for fun.)
        if result == "win":
            self.player_rating += random.randint(5, 15)
        elif result == "loss":
            self.player_rating -= random.randint(5, 15)
        elif result == "draw":
            self.player_rating += random.randint(-5, 5)
        self.player_rating = max(self.player_rating, 0)  # never negative

    def display(self):
        print("\nFake Leaderboard:")
        print("-----------------")
        sorted_competitors = sorted(self.competitors, key=lambda x: x["rating"], reverse=True)
        for competitor in sorted_competitors:
            print(f"{competitor['name']} - {competitor['rating']}")
        print(f"YOU - {self.player_rating}\n")


####################################
# Chess Game with Stockfish Engine #
####################################
class ChessGame:
    def __init__(self, mode="classic", difficulty=5):
        self.mode = mode
        self.board = chess.Board()
        # Initialize Stockfish engine with given depth.
        self.stockfish = Stockfish(path=STOCKFISH_PATH, depth=15)
        self.difficulty = difficulty
        self.set_difficulty(self.difficulty)
        self.dynamic_difficulty = difficulty  # Used only in Dynamic Mode

    def set_difficulty(self, difficulty):
        # Map difficulty (1-10) to Stockfish's "Skill Level"
        # Stockfish accepts a skill level from 0 to 20.
        skill_level = min(max(difficulty * 2, 0), 20)
        self.stockfish.set_skill_level(skill_level)
        print(f"Set difficulty to {difficulty} (Skill Level: {skill_level})")

    def update_stockfish_position(self):
        # Update stockfish with the current board state (FEN format)
        self.stockfish.set_fen_position(self.board.fen())

    def print_board(self):
        # Print the board (uses python-chess textual board)
        print(self.board)

    def player_move(self):
        # Request a move from the player (input in UCI format, e.g., e2e4)
        move_input = input("Your move (in UCI format, e.g., e2e4): ")
        try:
            move = chess.Move.from_uci(move_input)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            else:
                print("Illegal move. Try again.")
                return False
        except Exception:
            print("Invalid input. Try again.")
            return False

    def ai_move(self):
        # Let Stockfish choose a move
        self.update_stockfish_position()
        best_move = self.stockfish.get_best_move()
        if best_move is None:
            print("AI cannot find a move. Game over?")
            return False
        move = chess.Move.from_uci(best_move)
        self.board.push(move)
        print(f"AI plays: {best_move}")
        return True

    def play_classic(self):
        print("Starting Classic Mode...")
        while not self.board.is_game_over():
            self.print_board()
            valid = False
            # Keep asking for a valid move
            while not valid:
                valid = self.player_move()
            if self.board.is_game_over():
                break
            self.ai_move()
        print("Game over!")
        print("Result:", self.board.result())

    def play_puzzle(self):
        # For demonstration, we insert a fixed puzzle.
        print("Starting Puzzle Mode...")
        # Example FEN for a simple tactical puzzle (White to move).
        puzzle_fen = "rnb1kbnr/pppp1ppp/8/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3"
        self.board.set_fen(puzzle_fen)
        self.print_board()
        move_input = input("Enter your move to solve the puzzle: ")
        try:
            move = chess.Move.from_uci(move_input)
            if move in self.board.legal_moves:
                self.board.push(move)
                # For our demo, we consider the puzzle solved if the move results in checkmate.
                if self.board.is_checkmate():
                    print("Puzzle solved! Checkmate.")
                else:
                    print("That move did not result in checkmate. Puzzle failed.")
            else:
                print("Illegal move.")
        except Exception:
            print("Invalid input.")

    def play_twist(self):
        print("Starting Twist Mode (Custom Rules)...")
        print("Note: In this mode, pawns are allowed a special backward move if the square directly behind is empty.")
        while not self.board.is_game_over():
            self.print_board()
            valid = False
            while not valid:
                move_input = input("Your move (or type 'back' for a backward pawn move): ")
                if move_input.lower() == "back":
                    pawn_moved = False
                    # Try to find a pawn that can move backwards.
                    for move in list(self.board.legal_moves):
                        piece = self.board.piece_at(move.from_square)
                        if piece and piece.piece_type == chess.PAWN:
                            rank = chess.square_rank(move.from_square)
                            file = chess.square_file(move.from_square)
                            if piece.color == chess.WHITE:
                                target_rank = rank - 1
                            else:
                                target_rank = rank + 1
                            if 0 <= target_rank < 8:
                                target_square = chess.square(file, target_rank)
                                if self.board.piece_at(target_square) is None:
                                    backward_move = chess.Move(move.from_square, target_square)
                                    # We don't modify the rules; we simply allow this move if legal.
                                    if backward_move not in self.board.legal_moves:
                                        # Force the move even if not normally legal.
                                        self.board.push(backward_move)
                                        print(f"Pawn moved backward from {chess.square_name(move.from_square)} to {chess.square_name(target_square)}")
                                        pawn_moved = True
                                        valid = True
                                        break
                    if not pawn_moved:
                        print("No pawn can move backward at the moment.")
                else:
                    try:
                        move = chess.Move.from_uci(move_input)
                        if move in self.board.legal_moves:
                            self.board.push(move)
                            valid = True
                        else:
                            print("Illegal move. Try again.")
                    except Exception:
                        print("Invalid input. Try again.")
            if self.board.is_game_over():
                break
            self.ai_move()
        print("Game over!")
        print("Result:", self.board.result())

    def play_dynamic(self):
        print("Starting Dynamic Mode (Adaptive Difficulty)...")
        move_count = 0
        while not self.board.is_game_over():
            self.print_board()
            valid = False
            while not valid:
                valid = self.player_move()
            move_count += 1
            # Every 3 moves, adjust the difficulty upward by one (up to max 10)
            if move_count % 3 == 0:
                self.dynamic_difficulty = min(10, self.dynamic_difficulty + 1)
                self.set_difficulty(self.dynamic_difficulty)
                print(f"Dynamic Mode: Increased difficulty to {self.dynamic_difficulty}")
            if self.board.is_game_over():
                break
            self.ai_move()
        print("Game over!")
        print("Result:", self.board.result())


####################################
# Main Menu for Game Selection     #
####################################
def main():
    leaderboard = FakeLeaderboard()

    while True:
        print("===============================")
        print("         Ultimate Chess        ")
        print("===============================")
        print("Select a Game Mode:")
        print("1. Classic Mode")
        print("2. Puzzle Mode")
        print("3. Twist Mode")
        print("4. Dynamic Mode")
        print("5. Show Fake Leaderboard")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            try:
                difficulty = int(input("Enter difficulty (1-10): "))
            except ValueError:
                difficulty = 5
            game = ChessGame(mode="classic", difficulty=difficulty)
            game.play_classic()
            # Update leaderboard based on result (assumes "1-0" => player win, "0-1" => loss)
            result = game.board.result()
            if result == "1-0":
                leaderboard.update_rating("win")
            elif result == "0-1":
                leaderboard.update_rating("loss")
            else:
                leaderboard.update_rating("draw")
        elif choice == "2":
            game = ChessGame(mode="puzzle", difficulty=5)
            game.play_puzzle()
        elif choice == "3":
            try:
                difficulty = int(input("Enter difficulty (1-10): "))
            except ValueError:
                difficulty = 5
            game = ChessGame(mode="twist", difficulty=difficulty)
            game.play_twist()
        elif choice == "4":
            try:
                difficulty = int(input("Enter starting difficulty (1-10): "))
            except ValueError:
                difficulty = 5
            game = ChessGame(mode="dynamic", difficulty=difficulty)
            game.play_dynamic()
            result = game.board.result()
            if result == "1-0":
                leaderboard.update_rating("win")
            elif result == "0-1":
                leaderboard.update_rating("loss")
            else:
                leaderboard.update_rating("draw")
        elif choice == "5":
            leaderboard.display()
        elif choice == "6":
            print("Exiting game. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
              
