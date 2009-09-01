import linear_constraints as lc


x = lc.Number()
print 'x', x
#lc.zero(x)
lc.zero(x - 3)
print x.get_value()


class VisiblePoint(lc.Compound):
    def __init__(self):
        lc.Compound.__init__(self, dict(x=lc.Number(),
                                        y=lc.Number()))
    def draw(self):
        print 'point', self.x.get_value(), self.y.get_value()

p = VisiblePoint()
lc.zero(p.x - 3)
lc.zero(p.y - 5)
p.draw()


def Point():
    return lc.Compound(dict(x=lc.Number(), y=lc.Number()))

class Line(lc.Compound):
    def __init__(self):
        lc.Compound.__init__(self, dict(start=Point(), end=Point()))
    def draw(self):
        x0 = self.start.x
        y0 = self.start.y
        x1 = self.end.x
        y1 = self.end.y
        print 'draw', \
            x0.get_value(), y0.get_value(), \
            x1.get_value(), y1.get_value()

l1 = Line()
lc.zero(l1.end.x - 5)
lc.zero(l1.end.y - (l1.start.y + 10))
lc.zero(l1.start - dict(x=3, y=4))

l1.draw()
