from Game2048 import *
import math

class Player(BasePlayer):
    def __init__(self, timeLimit):
        super().__init__(timeLimit)
        self._nodeCount = 0
        self._parentCount = 0
        self._childCount = 0
        self._depthCount = 0
        self._count = 0

    def findMove(self, state):
        self._count += 1
        bestMove = None
        depth = 1
        maxDepth = 3 if state._board.count(0) < 5 else 4

        while self.timeRemaining() and depth <= maxDepth:
            best = float('-inf')
            alpha = -float('inf')
            beta = float('inf')
            for a in self.moveOrder(state):
                if not self.timeRemaining():
                    return
                result = state.move(a)
                if result._board == state._board:
                    continue
                val = self.chancePlayer(result, depth - 1, alpha, beta)
                if val is None:
                    return
                if val > best:
                    best = val
                    bestMove = a
                alpha = max(alpha, best)
            if bestMove:
                self.setMove(bestMove)
            depth += 1

    def maxPlayer(self, state, depth, alpha, beta):
        if state.gameOver():
            return state.getScore()
        if depth == 0:
            return self.heuristic(state)

        best = float('-inf')
        for a in self.moveOrder(state):
            result = state.move(a)
            if result._board == state._board:
                continue
            val = self.chancePlayer(result, depth - 1, alpha, beta)
            if val is None:
                return None
            best = max(best, val)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best

    def chancePlayer(self, state, depth, alpha, beta):
        if state.gameOver():
            return state.getScore()
        if depth == 0:
            return self.heuristic(state)

        zeros = [i for i, v in enumerate(state._board) if v == 0]
        if not zeros:
            return self.heuristic(state)

        total = 0
        for i in zeros:
            for v, p in [(1, 0.9), (2, 0.1)]:
                newBoard = state._board[:]
                newBoard[i] = v
                newState = Game2048(newBoard, state._score)
                val = self.maxPlayer(newState, depth - 1, alpha, beta)
                if val is None:
                    return None
                total += p * val / len(zeros)
        return total

    def heuristic(self, state):
        board = [state.getTile(r, c) for r in range(4) for c in range(4)]
        actual = [0 if v == 0 else 2 ** v for v in board]

        maxTile = max(actual)
        corners = [0, 3, 12, 15]
        cornerBonus = 5000 if maxTile in [actual[i] for i in corners] else -1000

        emptyTiles = board.count(0)
        emptyBonus = math.log2(emptyTiles + 1) * 800

        snakeWeights = [
            100, 90, 80, 70,
            50, 60, 65, 75,
            30, 20, 10, 5,
            2, 3, 4, 1
        ]
        snakeScore = sum(actual[i] * snakeWeights[i] for i in range(16))

        mono = self.monotonicity(actual)
        smooth = self.smoothness(actual)
        merge = self.mergePotential(actual)

        return (
            state.getScore()
            + emptyBonus
            + cornerBonus
            + snakeScore * 0.05
            + mono * 5
            + smooth * 3
            + merge * 200
        )

    def monotonicity(self, actual):
        total = 0
        for i in range(4):
            row = actual[i*4:(i+1)*4]
            col = actual[i::4]
            total += self.lineMono(row)
            total += self.lineMono(col)
        return total

    def lineMono(self, line):
        inc = dec = 0
        for i in range(3):
            diff = line[i] - line[i+1]
            if diff > 0:
                inc += diff
            else:
                dec -= diff
        return max(inc, dec)

    def smoothness(self, actual):
        penalty = 0
        for r in range(4):
            for c in range(3):
                penalty -= abs(actual[r*4 + c] - actual[r*4 + c + 1])
        for c in range(4):
            for r in range(3):
                penalty -= abs(actual[r*4 + c] - actual[(r+1)*4 + c])
        return penalty

    def mergePotential(self, actual):
        count = 0
        for r in range(4):
            for c in range(3):
                if actual[r*4 + c] == actual[r*4 + c + 1] and actual[r*4 + c] != 0:
                    count += 1
        for c in range(4):
            for r in range(3):
                if actual[r*4 + c] == actual[(r+1)*4 + c] and actual[r*4 + c] != 0:
                    count += 1
        return count

    def moveOrder(self, state):
        pref = {'U': 0, 'L': 1, 'R': 2, 'D': 3}
        return sorted(state.actions(), key=lambda a: pref.get(a, 4))

    def stats(self):
        if self._count:
            print(f'Average depth: {self._depthCount/self._count:.2f}')
