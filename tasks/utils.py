from b3.utils import ensure

def prompt(fn=None, default=0xDEADBEEF):
    has_default = default != 0xDEADBEEF
    while True:
        prompt = '> '
        if has_default:
            prompt = "(%r) > " % default

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

def pick(choice_type, choices, default=0xDEADBEEF):
    ensure(choices, "no %ss to choose from" % choice_type)
    has_default = default != 0xDEADBEEF
    if len(choices) == 1:
        return choices[0]
    has_default and ensure(default in choices, "default (%r) isn't in list of choices (%s)" % (default, choices))

    for i, x in enumerate(choices):
        print("[%s] %s" % (i, x))

    def validator(uin):
        ensure(uin.isdigit(), 'a number between 0 and %s is required' % (len(choices) - 1,))
        uin = int(uin)
        ensure(uin in range(0, len(choices)), 'a number between 0 and %s is required' % (len(choices) - 1,))
        return uin

    idx = prompt(validator)
    return choices[idx]
