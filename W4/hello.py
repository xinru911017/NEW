from weakref import ref


def square(y):
    print("{}的平方為{}".format(y, y*y))

x = int(input("請輸入一個整數："))

if(x <= 0):
    print("您輸入的小於等於0")
else:
    for i in range(x):
        square(i)
        # print("{}的平方為{}".format(i, i*i))
    

