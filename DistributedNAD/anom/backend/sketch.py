import hashlib


class AnomalyCountSketch(object):

    def __init__(self, m, d):
        """ `m` is the size of the hash tables, larger implies smaller
        overestimation. `d` the amount of hash tables, larger implies lower
        probability of overestimation.
        """
        if not m or not d:
            raise ValueError("Table size (m) and amount of hash functions (d)"
                             " must be non-zero")
        self.m = m
        self.d = d
        self.n = 0
        self.tables = []
        self.keys = []

        for _ in xrange(d):
            table = []
            for __ in xrange(m):
                port_table = {'total': 0}
                table.append(port_table)
            self.tables.append(table)

    def add(self, x, y, value=1):
        """
        Count element `x:y` as if had appeared `value` times.
        By default `value=1` so:
            sketch.add(x, y)
        Effectively counts `x:y` as occurring once.
        """
        self.n += value
        if x not in self.keys:
            self.keys.append(x)

        for table, i in zip(self.tables, self._hash(x)):
            if y not in table[i]:
                table[i][y] = 0
            table[i][y] += value
            table[i]["total"] += value

    def remove(self, x):
        """
        Remove element x and all subelements from the sketch.
        """
        value = self.query(x)
        self.n -= value['total']
        self.keys.remove(x)

        for table, i in zip(self.tables, self._hash(x)):
            for v in value:
                if v in table[i]:
                    table[i][v] -= value[v]

    def query(self, x):
        """
        Return an estimation of the amount of times `x` has ocurred.
        The returned value always overestimates the real value.
        """
        tuples = zip(self.tables, self._hash(x))
        for table, i in tuples:
            if table[i]['total'] == min(table[i]['total'] for table, i in tuples):
                return table[i]

    def get_keys(self):
        return self.keys

    def _hash(self, x):
        md5 = hashlib.md5(str(hash(x)))
        for i in xrange(self.d):
            md5.update(str(i))
            yield int(md5.hexdigest(), 16) % self.m

    def __getitem__(self, x):
        """
        A convenience method to call `query`.
        """
        return self.query(x)

    def __len__(self):
        """
        The amount of things counted. Takes into account that the `value`
        argument of `add` might be different from 1.
        """
        return self.n
