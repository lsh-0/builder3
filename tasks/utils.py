from b3.utils import ensure

def pick(choice_type, choices, default=0xDEADBEEF):
    ensure(choices, "no %s to choose from" % choice_type)
    default != 0xDEADBEEF and ensure(default in choices, "default (%s) isn't in list of choices (%s)" % (default, choices))
    if len(choices) == 1:
        return choices[0]
    print("%s:" % choice_type)
    for i, x in enumerate(choices):
        print(i, x)
    while True:
        uin = input('> ')
        if not uin:
            if default != 0xDEADBEEF:
                return default
            print('input required')
            continue
        uin = uin.strip()
        if not uin.isdigit():
            print('a number between 0 and %s is required' % len(choices) - 1)
            continue
        return choices[int(uin)]
