def string_to_hex_list(string):
    return [int(x,16) for x in string.split(',')]


# keep for odd if prev fader link is true
def link_separation(fader_list):
    result = []

    for i, f in enumerate(fader_list):
        if i % 2 == 0:
            result.append(f)
            continue

        prev = fader_list[i - 1].link

        if prev:
            result.append(f)

    return result