from Game2048 import *

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        self._nodeCount = 0
        self._parentCount = 0
        self._childCount = 0
        self._depthCount = 0
        self._count = 0

    def findMove(self, state):
        self._count += 1
        depth = 1

        while self.timeRemaining():
            self._depthCount += 1
            self._parentCount += 1
            self._nodeCount += 1

            best = -float('inf')
            bestMove = None

            for a in self.moveOrder(state):
                if not self.timeRemaining():
                    return
                result, _ = state.result(a)
                v = self.value(result, depth - 1, -float('inf'), float('inf'))
                if v is None:
                    return
                if v > best:
                    best = v
                    bestMove = a

            if bestMove:
                self.setMove(bestMove)

            depth += 1

    def value(self, state, depth, alpha, beta):
        self._nodeCount += 1
        self._childCount += 1

        if state.gameOver():
            return state.getScore()

        if depth == 0:
            return self.heuristic(state)

        self._parentCount += 1

        best = -float('inf')
        for a in self.moveOrder(state):
            if not self.timeRemaining():
                return None
            result, _ = state.result(a)
            v = self.value(result, depth - 1, alpha, beta)
            if v is None:
                return None
            best = max(best, v)
            alpha = max(alpha, best)
            if beta <= alpha:
                break  # prune

        return best

    def heuristic(self, state):
        score = state.getScore()
        empty = sum(
            1 for i in range(4) for j in range(4) if state.getTile(i, j) == 0
        )
        max_tile = max(state.getTile(i, j) for i in range(4) for j in range(4))
        corners = [state.getTile(0, 0), state.getTile(0, 3),
                   state.getTile(3, 0), state.getTile(3, 3)]
        corner_bonus = max_tile if max_tile in corners else 0
        mono = self.monotonicity(state)
        smooth = self.smoothness(state)

        # Strong weights, carefully balanced
        return score + empty * 50 + corner_bonus * 200 + mono * 10 - smooth * 3

    def monotonicity(self, state):
        total = 0
        # Rows
        for i in range(4):
            line = [2 ** state.getTile(i, j) if state.getTile(i, j) > 0 else 0 for j in range(4)]
            total += self.lineMonotonicity(line)
        # Columns
        for j in range(4):
            line = [2 ** state.getTile(i, j) if state.getTile(i, j) > 0 else 0 for i in range(4)]
            total += self.lineMonotonicity(line)
        return total

    def lineMonotonicity(self, line):
        inc = 0
        dec = 0
        for k in range(1, len(line)):
            diff = line[k] - line[k - 1]
            if diff > 0:
                inc += diff
            else:
                dec -= diff
        return max(inc, dec)

    def smoothness(self, state):
        smooth = 0
        for i in range(4):
            for j in range(3):
                t1 = 2 ** state.getTile(i, j) if state.getTile(i, j) > 0 else 0
                t2 = 2 ** state.getTile(i, j + 1) if state.getTile(i, j + 1) > 0 else 0
                smooth += abs(t1 - t2)
        for j in range(4):
            for i in range(3):
                t1 = 2 ** state.getTile(i, j) if state.getTile(i, j) > 0 else 0
                t2 = 2 ** state.getTile(i + 1, j) if state.getTile(i + 1, j) > 0 else 0
                smooth += abs(t1 - t2)
        return smooth

    def moveOrder(self, state):
        actions = state.actions()
        scored = []
        for a in actions:
            result, _ = state.result(a)
            scored.append((result.getScore(), a))
        scored.sort(reverse=True)
        return [a for (_, a) in scored]

    def stats(self):
        print(f'Average depth: {self._depthCount / self._count:.2f}')
        print(f'Branching factor: {self._childCount / self._parentCount:.2f}')
