def print_bounded_multiline_message(input_lines, maxlength=200):
    lines = []
    for line in input_lines:
        while len(line) > maxlength:
            lines += [line[0:maxlength]]
            line = line[maxlength:-1]
        if len(line) > 0:
            lines += [line]

    max_line_length = max(len(line) for line in lines)
    border = "#" * (max_line_length + 4)
    print(border)

    for line in lines:
        formatted_line = f"# {line.ljust(max_line_length)} #"
        print(formatted_line)

    print(border)
