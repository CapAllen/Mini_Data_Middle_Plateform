# 本脚本包含函数是对database.py中的个性化拓展
# 主要针对个性化要求较强的数据库

def unstack_20192020_nmntdfsx(result):
    '''
    对『2019-2020年模拟投档分数线』数据库的横向展开函数
    '''
    result_test = result.set_index(['院校代码', '院校名称','批次','科类','年份','模拟次数'])
    result_test = result_test.unstack().unstack().unstack()

    level,code = list(zip(result_test.columns.levels,result_test.columns.codes))[-1]

    new_cols = []
    for levels,codes in list(zip(result_test.columns.levels,result_test.columns.codes))[::-1]:
        level_cols = []
        for code in codes:
            level_cols.append(levels[code])
        if new_cols:
            new_cols = [str(new)+str(level) for new,level in zip(new_cols,level_cols)]
        else:
            new_cols = level_cols

    result_test.columns = new_cols
    result_test = result_test[sorted(new_cols)].fillna('-1').reset_index()
    result_test['院校代码'] = result_test['院校代码'].astype(str).str.zfill(4)

    return result_test