"""
TODO: Add file header
"""


class Utils:
    @staticmethod
    def next_index(
        current_index: int,
        length: int,
        direction: int = 1,
        loop_behavior: bool = True
    ) -> int:
        """
        Calculates the next index in a list based on the current index,
        the length of the list and the direction of movement.

        Args:
            current_index: The current index in the list.
            length: The length of the list.
            direction: The direction of movement
                (1 for forward, -1 for backward).
            loop_behavior: If True, the index will wrap around when reaching
                the start or end of the list. If False, the index will be
                clamped within the bounds of the list.

        Note:
            When `loop_behavior` is `True`, the expression
            `(current_index + direction) % length` ensures that the index
            always stays within the valid range from `0` to `length - 1`.
            The modulo operator (%) makes the index "wrap around":

                - If the index moves past the end of the list, it wraps back
                  to 0.
                - If the index moves before the beginning, it wraps to the
                last position.

            Examples:
                For a list of length 5 (indices 0 to 4):
                (4 + 1) % 5 = 0   → moves from the end to the start
                (0 - 1) % 5 = 4   → moves from the start to the end
                (2 + 1) % 5 = 3   → normal forward movement
                (2 - 1) % 5 = 1   → normal backward movement

        Returns:
            The calculated next index.
        """
        if loop_behavior:
            return (current_index + direction) % length

        if direction < 0:
            return max(current_index - 1, 0)
        else:
            return min(current_index + 1, length - 1)