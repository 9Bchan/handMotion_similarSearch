from cgitb import text


def main():
    list1 = [['a',0],['b',1],['c',2]]
    print(list1)
    list1[0].append('x')
    print(list1)

main()