# Clockwise from Up, then all 8 directions (cardinals + diagonals)
MOVE_ORDER = [
    (-1, 0), (0, 1), (1, 0), (1, 1), (0, -1), (-1, -1), (-1, 1), (1, -1),
]


def get_neighbors(row, col, rows, cols, is_wall_fn):
    out = []
    for dr, dc in MOVE_ORDER:
        r, c = row + dr, col + dc
        if 0 <= r < rows and 0 <= c < cols and not is_wall_fn(r, c):
            out.append((r, c))
    return out


def path_from_parents(parent, start, goal):
    if goal not in parent:
        return None
    rev = []
    cur = goal
    while cur is not None:
        rev.append(cur)
        cur = parent.get(cur)
    rev.reverse()
    return rev if rev and rev[0] == start else None
