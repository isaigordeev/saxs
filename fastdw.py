from fastdtw import fastdtw

la3d = [1, 1.1547,
        1.5275,
        1.632,
        1.82,
        1.914,
        2.0]

pn = [1.224744871391589,
      1.414213562373095,
      1.732050807568877,
      2.0,
      2.1213203435596424,
      2.23606797749979,
      2.3452078799117144,
      2.449489742783178,
      2.6457513110645903,
      2.82842712474619]

in2 = [1.414213562373095,
       1.732050807568877,
       2.0,
       2.23606797749979,
       2.449489742783178,
       2.6457513110645903,
       2.82842712474619,
       2.9999999999999996,
       3.162277660168379,
       3.3166247903554,
       3.464101615137754]

sequence2 = [1.0, 1.53, 1.78, 2.1, 2.3, 2.7]
sequence3 = [1.0, 1.53, 1.6, 1.8, 1.92, 2.1]
sequence4 = [
    1., 1.56495475, 2.05343457, 2.24253277, 2.46711076,
    2.71422773
]

distance, path = fastdtw(la3d, sequence4, dist=lambda x, y: abs(x - y))
print("DTW distance:", distance)
print(path)
distance, path = fastdtw(pn, sequence4, dist=lambda x, y: abs(x - y))
print("DTW distance:", distance)
print(path)
distance, path = fastdtw(in2, sequence4, dist=lambda x, y: abs(x - y))
print("DTW distance:", distance)
print(path)
# for x,y in path:
#     print(sequence1[0])
