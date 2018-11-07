import qi.data.loader as WindLoader
import pandas as pd
import yaml
import logging

from jt.operate.data_loader import DataLoader
from jt.app.check_trading import check_position_transaction, cal_turnover
from jt.app.etl_data import import_from_file
from jt.utils.db.loader import PgSQLLoader
from jt.utils.misc import read_yaml, Logger
from jt.utils.fs.utils import Utils
from pkg_resources import resource_filename
from jt.operate.gql_loader import GqlLoader
from jt.utils.mail.mailplus import mailplus

# data_loader = DataLoader()
# gql_loader = GqlLoader()

# from_date = '20180725'
# to_date = '20180725'

# filt_symbol = ('204001.SZ')
# result = check_position_transaction('20180611',['64'])
# result['flag'] = result['symbol'].apply(lambda x: 0 if x in filt_symbol else 1)
# print(result.loc[result['flag']==1,:].drop(['flag'], axis=1))

# result = cal_turnover('20180927')
# print(result)

# PgSQLLoader.upsert测试
# pgl = PgSQLLoader('jtder')
# data = pgl.read('select * from public.users')
# df = pd.DataFrame({'id' : pd.Series([1,2,5]),
#                     'name' : pd.Series(['ed','wendy','neo']),
#                     'fullname' : pd.Series(['Eda Jones','Wendy Will','Neo Lin'])})
# pgl.upsert('public.users',df,['id'])

# Logger的应用
# LOG = Logger(__name__)
# LOG.info('this is in test.py')
# logging.getLogger('jt.operate.data_loader').setLevel(logging.DEBUG)
# print(data_loader.get_position_gql(from_date=from_date, to_date=to_date))

# 读文件，写数据库实例
# asset_id_map = read_yaml('cfg/asset_id_map.yaml')
# config_dict = read_yaml('cfg/xt_asset.yaml')
# file_ = r'C:\Users\dell\Desktop\x\account\Account.csv'
# data = import_from_file(file_, config_dict)
# data.product_id = data.product_id.apply(lambda x : asset_id_map.get(x, ''))
# data['currency'] = 'CNY'
# data['date'] = '20180803'
# print(data)
# pgloader = PgSQLLoader('jtder')
# pgloader.upsert('public.product_asset', data, ['product_id','date','currency'])

# data = data_loader.get_actual_trading_calendar(date_='20180808') #date_默认值为当天
# print(data)

# data = gql_loader.AShareEODPrices(symbols='000002.SZ',from_='20180824',to_='20180824')
# print(data)

# 发送邮件实例
df=pd.DataFrame([['one', '1'], ['two', '2']], columns=['name', 'value']) #表格
m = mailplus()
m.newemail(to_=['neo.lin@jaspercapital.com'], subject_='Test from python')
m.add_content('这是一封测试邮件')
m.add_title('这是一个标题')
m.add_table(df)
m.add_images([r'C:\Users\dell\Pictures\2018-07-23\017.JPG',r'C:\Users\dell\Pictures\2018-07-23\016.JPG'])
m.add_attachments([r'C:\Users\dell\Desktop\x\1.xlsx',r'C:\Users\dell\Pictures\2018-07-23\016.JPG',r'C:\Users\dell\Desktop\x\产品佣金表.xlsx'])
m.add_href(r'http://www.jaspercapital.com/index.php/')
m.add_href(r'http://www.jaspercapital.com/index.php/', '大岩资本')
m.add_content('谢谢大家，测试结束')
m.sendmail()
