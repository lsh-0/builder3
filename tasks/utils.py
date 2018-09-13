from b3.utils import ensure

def prompt(fn=None, default=0xDEADBEEF, default_label=None):
    has_default = default != 0xDEADBEEF
    while True:
        prompt = '> '
        if has_default:
            print()
            prompt = "> (%r) " % default_label or default

        uin = input(prompt)
        if not uin or not uin.strip():
            if has_default:
                return default
            print('input required')
            continue

        uin = uin.strip()
        if fn:
            try:
                return fn(uin)
            except AssertionError as err:
                print(str(err))
                continue
        return uin

def pick(choice_type, choices, default=0xDEADBEEF, auto_pick=False, auto_default=True):
    """
    @default allows a specific choice to be set as the default
    @auto_pick will automatically use the first choice in the list of choices if the list has a length of 1
    @auto_default is used if a default is not specified and uses the first value in the list of choices
    """
    ensure(choices, "no %ss to choose from" % choice_type)
    has_default = default != 0xDEADBEEF
    if auto_pick and len(choices) == 1:
        return choices[0]

    if not has_default and auto_default:
        default = choices[0]
        has_default = True # not really neccessary

    has_default and ensure(default in choices, "default (%r) isn't in list of choices (%s)" % (default, choices))

    for i, x in enumerate(choices):
        print("[%s] %s" % (i, x))

    def validator(uin):
        ensure(uin.isdigit(), 'a number between 0 and %s is required' % (len(choices) - 1,))
        uin = int(uin)
        ensure(uin in range(0, len(choices)), 'a number between 0 and %s is required' % (len(choices) - 1,))
        return uin

    default_idx = 0xDEADBEEF
    if has_default:
        default_idx = choices.index(default) # convert the requested default value to an index

    idx = prompt(validator, default_idx, default)
    return choices[idx]
