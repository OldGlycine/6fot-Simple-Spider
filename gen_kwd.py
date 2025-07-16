import copy

def gen(raw_kwd, file_name):
    keyword = copy.deepcopy(raw_kwd)
    keyword.insert(0, file_name)
    # TODO：部分省市无需通过cities来扩大数据量，相反，像北京反而需要缩小数据量
    # if file_name == '青海':
    #     cities = ['西宁','海东','海北','黄南','海南','果洛','玉树','海西']
    #     keyword = cities + keyword
    # if file_name == '四川':
    #     keyword.remove('四川')
    return keyword