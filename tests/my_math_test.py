from my_math import *


def test():
    sa = 0.14465
    sb = 0.1415
    apex = [0, 0.3, 0.8726]

    js = calculate_JS_partial(sa, sb, apex)
    # print(js)

    sa_1 = 0.2
    sb_1 = 0.2

    sa_2 = 0.3
    sb_2 = 0.3

    sa_3 = 0.4
    sb_3 = 0.4

    apex_1 = [0, 0.1, 0.2]
    apex_2 = [0, 0.2, 0.3]
    apex_3 = [0, 0.3, 0.4]

    js_1 = calculate_JS_partial(sa_1, sb_1, apex_1)
    js_2 = calculate_JS_partial(sa_2, sb_2, apex_2)
    js_3 = calculate_JS_partial(sa_3, sb_3, apex_3)

    # print(js_1)
    # print(js_2)
    # print(js_3)

    js = calculate_JS(sa_1, sb_1, sa_2, sb_2, sa_3, sb_3, apex_1, apex_2, apex_3)
    # print(js)


test()


def test_jc():
    jc = calculate_JC([0, 0, 0], [0, 0, 0])
    print(np.around(jc, decimals=4))
