import akshare as ak
import pandas as pd
import datetime
from datetime import timedelta 
import pymysql
from sqlalchemy import create_engine

# 获取今天的日期  
today = datetime.datetime.now()
today_str = today.strftime('%Y-%m-%d')
today_str2 = today.strftime('%Y%m%d')
# 计算前N天的日期  
N_days_ago = today - timedelta(days=184)
N_days_ago_str = N_days_ago.strftime('%Y-%m-%d')
N_days_ago_str2 = N_days_ago.strftime('%Y%m%d')
# print(N_days_ago)


def execSql(vsql):
    # 建立数据库连接
    connection = pymysql.connect(
    host='localhost',  # 数据库主机名
    port=5888,               # 数据库端口号，默认为3306
    user='root',             # 数据库用户名
    passwd='123456',         # 数据库密码
    db='ak',               # 数据库名称
    charset='utf8'           # 字符编码
    )
    # 创建游标对象
    cursor = connection.cursor()
    # sql
    cursor.execute(vsql)
    connection.commit()
    results = cursor.fetchone()
    # 关闭游标和连接
    cursor.close()
    connection.close()
    return results

def execSqlDf(vsql):
    # 建立数据库连接
    engine = create_engine('mysql+pymysql://root:123456@localhost:5888/ak')
    df = pd.read_sql_query(vsql, engine)
    return df

def maxDate(v_tablename):
    # print('maxDate')
    vsql=f'select max(f_date) from {v_tablename} '
    if (execSql(vsql)[0]==None):
        return '2024-03-31'
    else:
        return execSql(vsql)[0].strftime('%Y-%m-%d')

def updateValue(v_tablename,v_id,v_amount1,v_amount2):
    print(f'update start:{v_id} {v_amount1} {v_amount2}')
    vsql=f'update `{v_tablename}` set amount1 = {v_amount1}, amount2 = {v_amount2} where id = {v_id}'
    execSql(vsql)

def getHisValue(v_tablename,v_df):
    # print('getHisValue')
    for i_date, i_value in zip(v_df['净值日期'], v_df['单位净值']): 
        sql = f"INSERT INTO {v_tablename} (f_date, f_value) VALUES ('{i_date}',{i_value} )"
        print(sql) 
        execSql(sql)

def clear(v_tablename,v_interval):
    # print('clear')
    ## break_flag
    bf_i = 1
    bf_j = 0
    bf_z = 0
    ##
    while bf_i:
        j_df=execSqlDf(f'select * from  `{v_tablename}` where amount1 <> 0 order by id')
        for j_id, j_value, j_amount1, j_amount2 in zip(j_df['id'],j_df['f_value'],j_df['amount1'],j_df['amount2']):
            if(bf_j>0):
                bf_j=0
                break
            if(j_amount1>0):
                vsql = f'select * from  `{v_tablename}` where  amount1<0 and f_value > {j_value} + {v_interval} order by f_value'
                k_df=execSqlDf(vsql)
                # print(k_df)
                for k_id,k_amount1, k_amount2 in zip(k_df['id'],k_df['amount1'],k_df['amount2']):
                    if (j_amount1 + k_amount1 >= 0):
                        j_id,j_amount1,j_amount2,k_id,k_amount1,k_amount2=j_id,j_amount1+k_amount1,j_amount2-k_amount1,k_id,0,k_amount2+k_amount1
                        updateValue(v_tablename,j_id,j_amount1,j_amount2)
                        updateValue(v_tablename,k_id,k_amount1,k_amount2)
                        bf_j = bf_j+1
                    if (j_amount1 + k_amount1 < 0 ):
                        j_id,j_amount1,j_amount2,k_id,k_amount1,k_amount2=j_id,0,j_amount2+j_amount1,k_id,k_amount1+j_amount1,k_amount2-j_amount1
                        updateValue(v_tablename,j_id,j_amount1,j_amount2)
                        updateValue(v_tablename,k_id,k_amount1,k_amount2)
                        bf_j = bf_j+1
                    if(j_amount1 == 0):
                        break
            if(j_amount1<0):
                vsql = f'select * from  `{v_tablename}` where  amount1>0 and f_value < {j_value} - {v_interval} order by f_value desc'
                k_df=execSqlDf(vsql)
                for k_id,k_amount1, k_amount2 in zip(k_df['id'],k_df['amount1'],k_df['amount2']):
                    if (j_amount1 + k_amount1 <= 0):
                        j_id,j_amount1,j_amount2,k_id,k_amount1,k_amount2=j_id,j_amount1+k_amount1,j_amount2-k_amount1,k_id,0,k_amount2+k_amount1
                        updateValue(v_tablename,j_id,j_amount1,j_amount2)
                        updateValue(v_tablename,k_id,k_amount1,k_amount2)
                        bf_j = bf_j+1
                    if (j_amount1 + k_amount1 > 0 ):
                        j_id,j_amount1,j_amount2,k_id,k_amount1,k_amount2=j_id,0,j_amount2+j_amount1,k_id,k_amount1+j_amount1,k_amount2-j_amount1
                        updateValue(v_tablename,j_id,j_amount1,j_amount2)
                        updateValue(v_tablename,k_id,k_amount1,k_amount2)
                        bf_j = bf_j+1
                    if(j_amount1 == 0):
                        break
            if(j_id==j_df['id'].max()):
                bf_i = 0
        bf_z = bf_z+1
        if(bf_z == 3):
            bf_i = 0

def subtract_zero(a):  
    result = a  
    if result < 0:  
        return 0  
    else:  
        return result
    
def calculate(v_tablename,v_start_value,v_interval,v_times,v_increase,v_rate):
    # print('calculating')
    latest = execSql(f'select f_value from  `{v_tablename}` order by f_date desc limit 1')[0]
    f_df=execSqlDf(f'select * from  `{v_tablename}` where amount1 <> 0 order by id')
    # print(f_df)
    buy_sum = f_df[f_df['amount1']>0]['amount1'].sum()
    sell_sum = f_df[f_df['amount1']<0]['amount1'].sum()
    latest_buy_sum = f_df[(f_df['f_value']<latest-v_interval)&(f_df['amount1']>0)]['amount1'].sum()
    latest_sell_sum = f_df[(f_df['f_value']>latest+v_interval)&(f_df['amount1']<0)]['amount1'].sum()
    latest_top_buy = subtract_zero(v_start_value-v_interval-latest)*v_times*(1+(subtract_zero(v_start_value-v_interval-latest)/v_interval/v_increase))
    latest_top_sell = -subtract_zero(latest-v_start_value-v_interval)*v_times*(1+(subtract_zero(latest-v_start_value-v_interval)/v_interval/v_increase))
    # print(f'buy_sum:{buy_sum}\nsell_sum:{sell_sum}')
    # print(f'latest:{latest}\nlatest_buy_sum:{latest_buy_sum}\nlatest_sell_sum:{latest_sell_sum}\nlatest_top_buy:{latest_top_buy}\nlatest_top_sell:{latest_top_sell}')
    buy = subtract_zero(-latest_sell_sum + latest_top_buy - buy_sum)
    sell = -subtract_zero(latest_buy_sum - latest_top_sell + sell_sum)
    # print(f'buy:{buy}\nsuggest_buy:{buy*v_rate}\nsell:{sell}\nsuggest_sell:{sell*v_rate}')
    print(f'{v_tablename}:\nlatest:{latest}\nsuggest_buy:{buy*v_rate}\nsuggest_sell:{sell*v_rate}')


def cal(funds_cfg):
    # print(funds_cfg)
    # print(funds_cfg['funds_name'])
    interval = funds_cfg['interval']
    start_value = funds_cfg['start_value']
    times = funds_cfg['times']
    increase = funds_cfg['increase']
    rate = funds_cfg['rate']
    if(funds_cfg['funds_name']=='funds300'):
        tablename = 'funds300_detail'
        fund_open_fund_info_em_df = ak.fund_open_fund_info_em(symbol="000961", indicator="单位净值走势")
    elif(funds_cfg['funds_name']=='gold'):
        tablename = 'gold_detail'
        fund_open_fund_info_em_df = ak.fund_open_fund_info_em(symbol="002611", indicator="单位净值走势")
    elif(funds_cfg['funds_name']=='hk'):
        tablename = 'hk_detail'
        fund_open_fund_info_em_df = ak.fund_open_fund_info_em(symbol="005734", indicator="单位净值走势")
    elif(funds_cfg['funds_name']=='ger'):
        tablename = 'ger_detail'
        fund_open_fund_info_em_df = ak.fund_open_fund_info_em(symbol="015016", indicator="单位净值走势")
    elif(funds_cfg['funds_name']=='usa'):
        tablename = 'usa_detail'
        fund_open_fund_info_em_df = ak.fund_open_fund_info_em(symbol="006479", indicator="单位净值走势")
    # 获取数据库中最大日期
    v_maxdate = maxDate(tablename)
    v_maxdate2 = datetime.datetime.strptime(v_maxdate,'%Y-%m-%d').date()
    # 获取最大日期后新增的数据
    f_df = fund_open_fund_info_em_df.loc[fund_open_fund_info_em_df['净值日期']>v_maxdate2]
    # print(f_df)
    # 插入新增数据到数据库
    getHisValue(tablename,f_df)
    # 将正负相抵
    clear(tablename,interval)
    # 预估计算
    calculate(tablename,start_value,interval,times,increase,rate)


def sim_update(v_tablename,v_id,v_amount1):
    print(f'sim update start:{v_id} {v_amount1} ')
    vsql=f'update `{v_tablename}` set amount1 = {v_amount1} where id = {v_id}'
    execSql(vsql)

def sim_calculate(v_tablename,v_start_value,v_interval,v_times,v_increase,v_rate,v_id):
    # print('sim calculating')
    latest = execSql(f'select f_value from  `{v_tablename}` where id = {v_id} limit 1')[0]
    f_df=execSqlDf(f'select * from  `{v_tablename}`  order by id')
    buy_sum = f_df[f_df['amount1']>0]['amount1'].sum()
    sell_sum = f_df[f_df['amount1']<0]['amount1'].sum()
    latest_buy_sum = f_df[(f_df['f_value']<latest-v_interval)&(f_df['amount1']>0)]['amount1'].sum()
    latest_sell_sum = f_df[(f_df['f_value']>latest+v_interval)&(f_df['amount1']<0)]['amount1'].sum()
    latest_top_buy = subtract_zero(v_start_value-v_interval/2-latest)*v_times*(1+(subtract_zero(v_start_value-v_interval/2-latest)/v_interval/v_increase))
    latest_top_sell = -subtract_zero(latest-v_start_value-v_interval/2)*v_times*(1+(subtract_zero(latest-v_start_value-v_interval/2)/v_interval/v_increase))
    buy = round(subtract_zero(-latest_sell_sum + latest_top_buy - buy_sum)*v_rate)
    sell = round(-subtract_zero(latest_buy_sum - latest_top_sell + sell_sum)*v_rate)
    if (buy != 0):
        sim_update(v_tablename,v_id+1,buy)
        return
    if (sell != 0):
        sim_update(v_tablename,v_id+1,sell)
        return
    
def sim_calculate2(v_tablename,v_start_value,v_interval,v_times,v_increase,v_rate,v_id):
    # print('sim calculating')
    latest = execSql(f'select f_value from  `{v_tablename}` where id = {v_id} limit 1')[0]
    f_df=execSqlDf(f'select * from  `{v_tablename}`  order by id')
    buy_sum = f_df[f_df['amount1']>0]['amount1'].sum()
    sell_sum = f_df[f_df['amount1']<0]['amount1'].sum()
    latest_buy_sum = f_df[(f_df['f_value']<latest)&(f_df['amount1']>0)]['amount1'].sum()
    latest_sell_sum = f_df[(f_df['f_value']>latest)&(f_df['amount1']<0)]['amount1'].sum()
    latest_top_buy = subtract_zero(v_start_value-latest)*v_times*(1+(subtract_zero(v_start_value-latest)/v_interval/v_increase))
    latest_top_sell = -subtract_zero(latest-v_start_value)*v_times*(1+(subtract_zero(latest-v_start_value)/v_interval/v_increase))
    buy = round(subtract_zero(-latest_sell_sum + latest_top_buy - buy_sum)*v_rate)
    sell = round(-subtract_zero(latest_buy_sum - latest_top_sell + sell_sum)*v_rate)
    if (buy != 0):
        sim_update(v_tablename,v_id+1,buy)
        return
    if (sell != 0):
        sim_update(v_tablename,v_id+1,sell)
        return

def sim(funds_cfg):
    # print(funds_cfg)
    # print(funds_cfg['funds_name'])
    interval = funds_cfg['interval']
    start_value = funds_cfg['start_value']
    times = funds_cfg['times']
    increase = funds_cfg['increase']
    rate = funds_cfg['rate']
    if(funds_cfg['funds_name']=='funds300'):
        tablename = 'funds300_detail'
        fund_open_fund_info_em_df = ak.fund_open_fund_info_em(symbol="000961", indicator="单位净值走势")
    elif(funds_cfg['funds_name']=='gold'):
        tablename = 'gold_detail'
        fund_open_fund_info_em_df = ak.fund_open_fund_info_em(symbol="002611", indicator="单位净值走势")
    elif(funds_cfg['funds_name']=='hk'):
        tablename = 'hk_detail'
        fund_open_fund_info_em_df = ak.fund_open_fund_info_em(symbol="005734", indicator="单位净值走势")
    elif(funds_cfg['funds_name']=='ger'):
        tablename = 'ger_detail'
        fund_open_fund_info_em_df = ak.fund_open_fund_info_em(symbol="015016", indicator="单位净值走势")
    elif(funds_cfg['funds_name']=='usa'):
        tablename = 'usa_detail'
        fund_open_fund_info_em_df = ak.fund_open_fund_info_em(symbol="006479", indicator="单位净值走势")
    # 获取数据库中最大日期
    v_maxdate = maxDate(tablename)
    v_maxdate2 = datetime.datetime.strptime(v_maxdate,'%Y-%m-%d').date()
    # 获取最大日期后新增的数据
    f_df = fund_open_fund_info_em_df.loc[fund_open_fund_info_em_df['净值日期']>v_maxdate2]
    # print(f_df)
    # 插入新增数据到数据库
    getHisValue(tablename,f_df)
    # init
    execSql(f"UPDATE `{tablename}` SET `amount1` = '0',`amount2` = '0'")
    vsql = f'select * from  `{tablename}` order by id'
    s_df=execSqlDf(vsql)
    for s_id in s_df.loc[:, 'id']:  
        # print(s_id)
        # 将正负相抵
        clear(tablename,interval)
        # 预估计算
        sim_calculate(tablename,start_value,interval,times,increase,rate,s_id) 
        # print(execSql(f"select sum(amount2*f_value),sum(amount2),count(*),sum(case when amount1 + amount2 <> 0 then 1 else 0 end) from {tablename}"))

def sim_test_update(v_id,v_profit,v_sim_check,v_cnt_day,v_cnt_oper,v_cost,v_profit_rate):
    print('sim_test_update')
    vsql=f'update `sim_test` set profit = {v_profit},sim_check = {v_sim_check},cnt_day = {v_cnt_day},cnt_oper={v_cnt_oper},cost={v_cost},profit_rate={v_profit_rate} where id = {v_id}'
    execSql(vsql)

def simtest(v_fund_name):
    print('simtest')
    vsql = f'select * from  `sim_test` order by id'
    st_df=execSqlDf(vsql)
    for st_id, st_times, st_start_value,st_sim_interval, st_increase,st_rate in zip(st_df['id'],st_df['times'],st_df['start_value'],st_df['sim_interval'],st_df['increase'],st_df['rate']):
        print(st_id, st_times, st_start_value, st_sim_interval,st_increase,st_rate)
        v_funds_cfg = {'funds_name': v_fund_name,'start_value':st_start_value, 'interval': st_sim_interval,'times':st_times,'increase':st_increase,'rate':st_rate}
        sim(v_funds_cfg)
        latest = execSql(f"""select f_value from  `{v_fund_name}_detail` order by f_date desc limit 1""")[0]
        result_df=execSqlDf(f"""select sum((amount1+amount2)*({latest}-f_value)) profit,
                            sum( (amount1 + amount2)*f_value ) sim_check,
                            count(*) cnt_day,
sum(case when amount1 + amount2 <> 0 then 1 else 0 end) cnt_oper,
sum(case when amount1 + amount2 > 0 then (amount1 + amount2)*f_value else 0 end) cost,
round(sum((amount1+amount2)*({latest}-f_value))/sum(case when amount1 + amount2 > 0 then (amount1 + amount2)*f_value else 0 end)*100,2)  profit_rate 
 from {v_fund_name}_detail""")
        for r_profit,r_sim_check,r_cnt_day,r_cnt_oper,r_cost,r_profit_rate in zip(result_df['profit'],result_df['sim_check'],result_df['cnt_day'],result_df['cnt_oper'],result_df['cost'],result_df['profit_rate']):
            sim_test_update(st_id,r_profit,r_sim_check,r_cnt_day,r_cnt_oper,r_cost,r_profit_rate)
        
        