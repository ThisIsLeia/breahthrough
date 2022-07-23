# 價格突破區間順勢策略
# 交易策略為偵測當日行情並順勢而為
# 進場:
#     當價格突破某區間(定義上下界為九點之前的最高最低點)，順勢做多或做空
#
# 出場:
#     停利點30點
#     停損點10點
import sys


class StrategyBase:
    """流程定義(基類)"""
    NAME = None

    def __init__(self):
        if self.NAME is None:
            raise TypeError('NAME argument must be defined')

    def _getdata(self, filename):
        """讀取資料"""
        raise NotImplementedError

    def _strategy(self, tidy_data):
        raise NotImplementedError

    def _performance(self, profit_list):
        raise NotImplementedError

    def result(self):
        """入口"""
        data = self._getdata()
        profit = self._strategy(data)
        self._performance(profit)
        return 'success!'


class TaiwanFuture(StrategyBase):
    """台灣指數期貨"""
    NAME = 'future'
    def _getdata(self, filename='D:/Course/python/strategies/crawler/tidied/taiwanfuture_all_TX.csv'):
        # 0日期 1商品 2到期 3時間 4價格
        data = open(filename).readlines()
        tidy_data = [line.strip('\n').split(',') for line in data]
        return tidy_data
    def _strategy(self, tidy_data):
        """策略內容"""
        profit_list = []
        date_list = sorted(set([line[0] for line in tidy_data]))
        for date_ in date_list:
            # 取得當日資料
            day_data = [i for i in tidy_data if i[0] == date_]

            # 取得當日九點前股價資料 判斷行情
            data_before9 = [int(i[4]) for i in day_data if int(
                i[3]) >= 84500 and int(i[3]) < 90000]

            # 取得當日九點到十一點資料
            data_before11 = [i for i in day_data if int(
                i[3]) >= 90000 and int(i[3]) <= 110000]

            # 定義上下界為九點之前的最高最低點
            ceil = max(i for i in data_before9)
            floor = min(i for i in data_before9)

            # 可調整的停損停利點數
            take_profit = 30
            stop_loss = 10

            # 進場建倉
            index = 0
            # 開始判斷
            for i in range(len(data_before11)):
                # 當前時間
                time = data_before11[i][3]
                price = int(data_before11[i][4])
                # 建倉判斷
                if index == 0:
                    # 多單進場
                    if price > int(ceil):
                        index = 1
                        order_time = time
                        order_price = price
                    # 空單進場
                    elif price < int(floor):
                        index = -1
                        order_time = time
                        order_price = price
                    # 當日沒有交易 ##不明
                    elif i == len(data_before11)-1:
                        print(data_before11, 'No Trade')
                        break
                # 平倉
                elif index != 0:
                    # 多單出場
                    if index == 1:
                        # 停利停損
                        if price >= order_price + take_profit or price <= order_price - stop_loss:
                            cover_time = time
                            cover_price = price
                            profit = cover_price - order_price
                            print('日期:', date_, 'Buy', '下單時間:', order_time, '下單價:', order_price,
                                  '賣出時間:', cover_time, '賣出價:', cover_price, '損益:', profit)
                            break
                        # 11:00出場
                        elif i == len(data_before11) - 1:
                            cover_time = time
                            cover_price = price
                            profit = cover_price - order_price
                            print('日期:', date_, 'Buy', '下單時間:', order_time, '下單價:', order_price,
                                  '賣出時間:', cover_time, '賣出價:', cover_price, '損益:', profit)
                    # 空單出場
                    if index == -1:
                        # 停利停損
                        if price <= order_price + take_profit or price <= order_price - stop_loss:
                            cover_time = time
                            cover_price = price
                            profit = order_price - cover_price
                            print('日期:', date_, 'Sell', '下單時間:', order_time, '下單價:', order_price,
                                  '賣出時間:', cover_time, '賣出價:', cover_price, '損益:', profit)
                            break
                    # 11:00出場
                        elif i == len(data_before11) - 1:
                            cover_time = time
                            cover_price = price
                            profit = order_price - cover_price
                            print('日期:', date_, 'Sell', '下單時間:', order_time, '下單價:', order_price,
                                  '賣出時間:', cover_time, '賣出價:', cover_price, '損益:', profit)
            profit_list.append(profit)
        return profit_list
    def _performance(self, profit_list):
        """績效"""
        # 總損益
        total_profit = sum([i for i in profit_list])
        # 總交易次數
        total_num = len(profit_list)
        # 平均損益
        average_profit = round(total_profit/total_num, 2)
        # 總勝率
        win_num = len([i for i in profit_list if i > 0])
        win_rate = round(win_num/total_num, 2)

        # 最大連續虧損
        max_continue_loss = 0
        # 當前的連續虧損
        dropdown = 0
        for profit in profit_list:
            # 計算連續虧損
            if profit <= 0:
                dropdown += profit
                # 判斷 當前連續虧損 是否為 最大連續虧損
                if dropdown < max_continue_loss:
                    max_continue_loss = dropdown
            # 重置
            else:
                dropdown = 0

        # 印出績效
        print('TotalProfit:', total_profit)
        print('TotalNum:', total_num)
        print('AvgProfit:', average_profit)
        print('WinRate:', win_num)
        print('MaxConLoss:', win_rate)
        return 'analysis finished'



class StockFuture(StrategyBase):
    """股票期貨"""
    NAME = 'stock'

    def _getdata(self, filename):
        print('股期資料讀取')

    def _strategy(self, tidy_data):
        print('股期策略回測')

    def _performance(self, profit_list):
        print('股期績效')


class StrategyManager:
    """標的類別管理者"""

    def __init__(self):
        self._implemented_targets = {}   # 已經實作的標的
        for class_ in StrategyBase.__subclasses__():    # StrategyBase的子類別們
            self._implemented_targets[class_.NAME] = class_()

    @property
    def targets(self):
        """檢視已被實作的標的物件"""
        return self._implemented_targets

    def get_target(self, target_name):
        """取得標的"""
        return self._implemented_targets.get(target_name)   # get(key)好處是當key不在字典中時 會返還None 不會觸發error


strategy_manager = StrategyManager()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        name = sys.argv[1]  # python3 檔名.py [標的參數]
        target_class = strategy_manager.get_target(name)
        target_class.result()
    else:
        print(strategy_manager.targets)  # 印出可選擇標的
