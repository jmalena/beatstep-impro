def rescale(min_in: float, max_in: float, min_out: float, max_out: float, value: float) -> float:
    ratio = (value - min_in) / (max_in - min_in)
    return ratio * (max_out - min_out) + min_out
