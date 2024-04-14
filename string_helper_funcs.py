def rm_extra_spaces(string_):
    while "  " in string_:
        string_ = string_.replace("  ", " ")
    if string_.startswith(" "):
        string_ = string_[1:]
    return string_

if __name__ == '__main__':
    s = "sdnakn djadnjndf      sajdna djsdja   jsdnanda       sjdnadn              djnsa   s  sdad    da"
    print(rm_extra_spaces(s))