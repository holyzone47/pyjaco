n = [10000000, 1000000, 100000, 10000, 1000, 100, 10, 1, 0.1, 0.12, 0.123, 0.1234, 0.00001, 0.000001, 0.0000001, 0.00000001, 0.000000001]

for i, x in enumerate(n):
    print "Number %d" % i
    print "%%s: %s" % x
    print "%%f: %f" % x
    print "%%g: %g" % x
    print "%%e: %e" % x
