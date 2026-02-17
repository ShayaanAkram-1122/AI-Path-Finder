import heapq
from collections import deque
from grid import get_neighbors, path_from_parents, MOVE_ORDER

DIAG_COST = 1.414
CARDINAL_COST = 1.0


def _is_diagonal(dr, dc):
    return dr != 0 and dc != 0


def _step_cost(dr, dc):
    return DIAG_COST if _is_diagonal(dr, dc) else CARDINAL_COST


def bfs(start, goal, rows, cols, is_wall):
    parent = {start: None}
    frontier = deque([start])
    frontier_set = {start}
    explored = set()
    while frontier:
        node = frontier.popleft()
        frontier_set.discard(node)
        if node in explored:
            continue
        explored.add(node)
        if node == goal:
            yield (set(frontier) | frontier_set, explored, path_from_parents(parent, start, goal))
            return
        for nr, nc in get_neighbors(node[0], node[1], rows, cols, is_wall):
            if (nr, nc) not in parent:
                parent[(nr, nc)] = node
                frontier.append((nr, nc))
                frontier_set.add((nr, nc))
        yield (set(frontier) | frontier_set, explored, None)
    yield (set(), explored, None)


def dfs(start, goal, rows, cols, is_wall):
    parent = {start: None}
    stack = [start]
    frontier_set = {start}
    explored = set()
    while stack:
        node = stack.pop()
        frontier_set.discard(node)
        if node in explored:
            continue
        explored.add(node)
        if node == goal:
            yield (frontier_set | set(stack), explored, path_from_parents(parent, start, goal))
            return
        for nr, nc in get_neighbors(node[0], node[1], rows, cols, is_wall):
            if (nr, nc) not in parent:
                parent[(nr, nc)] = node
                stack.append((nr, nc))
                frontier_set.add((nr, nc))
        yield (frontier_set | set(stack), explored, None)
    yield (set(), explored, None)


def ucs(start, goal, rows, cols, is_wall):
    parent = {start: None}
    heap = [(0.0, start)]
    cost_so_far = {start: 0.0}
    frontier_set = {start}
    explored = set()
    while heap:
        c, node = heapq.heappop(heap)
        frontier_set.discard(node)
        if node in explored:
            continue
        explored.add(node)
        if node == goal:
            yield (set(n for _, n in heap) | frontier_set, explored, path_from_parents(parent, start, goal))
            return
        r, c = node
        for dr, dc in MOVE_ORDER:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols) or is_wall(nr, nc):
                continue
            new_cost = cost_so_far[node] + _step_cost(dr, dc)
            if (nr, nc) not in cost_so_far or new_cost < cost_so_far[(nr, nc)]:
                cost_so_far[(nr, nc)] = new_cost
                parent[(nr, nc)] = node
                heapq.heappush(heap, (new_cost, (nr, nc)))
                frontier_set.add((nr, nc))
        yield (set(n for _, n in heap) | frontier_set, explored, None)
    yield (set(), explored, None)


def dls(start, goal, rows, cols, is_wall, limit):
    for state in dls_generator_fixed(start, goal, rows, cols, is_wall, limit):
        yield state


def dls_generator_fixed(start, goal, rows, cols, is_wall, limit):
    parent = {start: None}
    stack = [(start, 0)]
    frontier_set = {start}
    explored = set()
    while stack:
        node, d = stack.pop()
        frontier_set.discard(node)
        if node in explored:
            continue
        explored.add(node)
        if node == goal:
            yield (set(), explored, path_from_parents(parent, start, goal))
            return
        if d >= limit:
            yield (frontier_set | set(n for n, _ in stack), explored, None)
            continue
        for nr, nc in get_neighbors(node[0], node[1], rows, cols, is_wall):
            if (nr, nc) not in parent:
                parent[(nr, nc)] = node
                stack.append(((nr, nc), d + 1))
                frontier_set.add((nr, nc))
        yield (frontier_set | set(n for n, _ in stack), explored, None)
    yield (set(), explored, None)


def iddfs(start, goal, rows, cols, is_wall):
    depth = 0
    while True:
        for frontier, explored, path in dls_generator_fixed(start, goal, rows, cols, is_wall, depth):
            yield (frontier, explored, path)
            if path is not None:
                return
        depth += 1


def bidirectional(start, goal, rows, cols, is_wall):
    parent_f = {start: None}
    parent_b = {goal: None}
    q_f = deque([start])
    q_b = deque([goal])
    frontier_f = {start}
    frontier_b = {goal}
    explored_f = set()
    explored_b = set()
    meeting = None
    while q_f and q_b:
        if q_f:
            node = q_f.popleft()
            frontier_f.discard(node)
            if node in explored_f:
                pass
            else:
                explored_f.add(node)
                if node in explored_b or node in frontier_b:
                    meeting = node
                    break
                for nr, nc in get_neighbors(node[0], node[1], rows, cols, is_wall):
                    if (nr, nc) not in parent_f:
                        parent_f[(nr, nc)] = node
                        q_f.append((nr, nc))
                        frontier_f.add((nr, nc))
        yield (frontier_f | set(q_f), frontier_b | set(q_b), explored_f, explored_b, None)
        if meeting is not None:
            break
        if q_b:
            node = q_b.popleft()
            frontier_b.discard(node)
            if node in explored_b:
                pass
            else:
                explored_b.add(node)
                if node in explored_f or node in frontier_f:
                    meeting = node
                    break
                for nr, nc in get_neighbors(node[0], node[1], rows, cols, is_wall):
                    if (nr, nc) not in parent_b:
                        parent_b[(nr, nc)] = node
                        q_b.append((nr, nc))
                        frontier_b.add((nr, nc))
        yield (frontier_f | set(q_f), frontier_b | set(q_b), explored_f, explored_b, None)
    if meeting is not None:
        path_f = path_from_parents(parent_f, start, meeting)
        path_b = path_from_parents(parent_b, goal, meeting)
        if path_f and path_b:
            path = path_f[:-1] + path_b[::-1]
        else:
            path = None
    else:
        path = None
    yield (set(), set(), explored_f, explored_b, path)


def bidirectional_unified(start, goal, rows, cols, is_wall):
    for frontier_f, frontier_b, explored_f, explored_b, path in bidirectional(start, goal, rows, cols, is_wall):
        yield (frontier_f | frontier_b, explored_f | explored_b, path)
