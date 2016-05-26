"""
Run the interpreter from the command line.
"""

import sys
import absyntax, parser

def main(argv):
    defs = []
    for filename in argv[1:]:
        with open(filename) as f:
            text = f.read()
        try:
            defs.extend(parser.parse(text))
        except parser.Unparsable as e:
            syntax_error(e, filename)
            return 1
    absyntax.run(defs)
    return 0

def syntax_error(e, filename):
    line_no, prefix, suffix = where(e)
    print "%s:%d:%d: Syntax error" % (filename, line_no, len(prefix))
    prefix, suffix = sanitize(prefix), sanitize(suffix)
    print '  ', prefix + suffix
    print '  ', ' '*len(prefix) + '^'

def where(e):
    before, after = e.failure
    line_no = before.count('\n')
    prefix = (before+'\n').splitlines()[line_no]
    suffix = (after+'\n').splitlines()[0] # XXX what if right on newline?
    return line_no+1, prefix, suffix

def sanitize(s):
    "Make s predictably printable, sans control characters like tab."
    return ''.join(c if ' ' <= c < chr(127) else ' ' # XXX crude
                   for c in s)

if __name__ == '__main__':
    sys.exit(main(sys.argv))