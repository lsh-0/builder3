from b3.utils import ensure

def pick(choice_type, choices, default=0xDEADBEEF):
    ensure(choices, "no %s to choose from" % choice_type)
    has_default = default != 0xDEADBEEF
    if len(choices) == 1:
        return choices[0]
    has_default and ensure(default in choices, "default (%r) isn't in list of choices (%s)" % (default, choices))

    print("%s:" % choice_type)
    for i, x in enumerate(choices):
        print("[%s] %s" % (i, x))

    while True:
        prompt = '> '
        if has_default:
            prompt = "(%s) > " % default

        uin = input(prompt)
        if not uin:
            if default != 0xDEADBEEF:
                return default
            print('input required')
            continue

        uin = uin.strip()
        if not uin.isdigit():
            print('a number between 0 and %s is required' % (len(choices) - 1,))
            continue

        uin = int(uin)
        if not uin in range(0, len(choices)):
            print('a number between 0 and %s is required' % (len(choices) - 1,))
            continue

        return choices[uin]
