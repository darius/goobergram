"""
Basic example figures, for testing.
"""

from linear_constraints import Number, Compound, equate

class Figure(Compound):
    def __init__(self):
        super(Figure, self).__init__({})
    def add_parts(self, dict):
        super(Figure, self).add_parts(nonself(dict))
    def draw(self):
        for part in self.get_parts():
            if hasattr(part, 'draw'):
                part.draw()

def nonself(d):
    return {k: v for k, v in d.iteritems() if k != 'self'}

class Point(Figure):
    def __init__(self):
        super(Point, self).__init__()
        x, y = Number(), Number()
        self.add_parts(locals())

class Label(Point):
    def __init__(self, text):
        super(Label, self).__init__()
        self.text = text
    def draw(self):
        if any(v.get_value() is None
               for v in [self.x, self.y]):
            print '// undetermined Label'
        else:
            print 'ctx.fillText(%r, %g, %g' % (self.text,
                                               self.x.get_value(),
                                               self.y.get_value())

class Line(Figure):
    def __init__(self):
        super(Line, self).__init__()
        start = Point()
        end = Point()
        center = Point()
        self.add_parts(locals())
        center ^ (start + end) / 2
    def draw(self):
        if any(v.get_value() is None
               for v in [self.start.x, self.start.y,
                         self.end.x, self.end.y]):
            print '// undetermined Line'
        else:
            print 'ctx.moveTo(%g, %g)' % (self.start.x.get_value(),
                                          self.start.y.get_value())
            print 'ctx.lineTo(%g, %g)' % (self.end.x.get_value(),
                                          self.end.y.get_value())

class HLine(Line):
    def __init__(self):
        super(HLine, self).__init__()
        y, length = Number(), Number()
        self.add_parts(locals())
        self.start.y ^ y
        self.end.y   ^ y
        self.start.x + length ^ self.end.x

class VLine(Line):
    def __init__(self):
        super(VLine, self).__init__()
        x, length = Number(), Number()
        self.add_parts(locals())
        self.start.x ^ x
        self.end.x   ^ x
        self.start.y + length ^ self.end.y

class Box(Figure):
    def __init__(self):
        super(Box, self).__init__()
        left, right = VLine(), VLine()
        top, bottom = HLine(), HLine()
        nw, n, ne, e, se, s, sw, w, c = tuple(Point() for _ in range(9))
        ht, wd = Number(), Number()
        self.add_parts(locals())

        nw ^ left.start
        nw ^ top.start
        ne ^ right.start
        ne ^ top.end
        sw ^ left.end
        sw ^ bottom.start
        se ^ right.end
        se ^ bottom.end

        n ^ (nw + ne) / 2
        s ^ (sw + se) / 2
        w ^ (nw + sw) / 2
        e ^ (ne + se) / 2

        c ^ (n + s) / 2

        ht ^ left.length
        wd ^ top.length

class LabelBox(Box):
    def __init__(self, text):
        super(LabelBox, self).__init__()
        label = Label(text)
        self.add_parts(locals())
        label ^ self.c # XXX does this work?

l1 = Line()
l1.end.x ^ 5
l1.end.y ^ (l1.start.y + 10)
l1.start ^ Compound(dict(x=3, y=4))
l1.draw()

print
l2 = HLine()
l2.draw()                       # XXX should raise an error
l2.y ^ 42
l2.length ^ 10
l2.start.x ^ 1
l2.draw()

print
lb = LabelBox('Aloha')
lb.top ^ l2
lb.ht ^ 100
lb.draw()
#. ctx.moveTo(3, 4)
#. ctx.lineTo(5, 14)
#. 
#. // undetermined Line
#. ctx.moveTo(1, 42)
#. ctx.lineTo(11, 42)
#. 
#. ctx.moveTo(1, 142)
#. ctx.lineTo(11, 142)
#. ctx.moveTo(1, 42)
#. ctx.lineTo(11, 42)
#. ctx.moveTo(11, 42)
#. ctx.lineTo(11, 142)
#. ctx.fillText('Aloha', 6, 92
#. ctx.moveTo(1, 42)
#. ctx.lineTo(1, 142)
