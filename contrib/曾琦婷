import random
import os
import json
def get_number(prompt):
    while True:
        uinput=input(prompt)
        if not uinput.isdigit():
            print('####请输入数字####')
            continue
        elif int(uinput)<0 :
             print('####数字应不小于零####') 
             continue  
        else:
            return int(uinput)
def save_data(day,money,stock,weather,target,random_thing,reputation,debt):
     game_data={}
     game_data['day']=day
     game_data['money']=money
     game_data['stock']=stock
     game_data['weather']=weather
     game_data['target']=target
     game_data['random_thing']=random_thing
     game_data['reputation']=reputation
     game_data['debt']=debt
     with open('user_data.json','w',encoding='utf-8')as f:
          f.write(json.dumps(game_data,ensure_ascii=False))
def load_data():
     try:
          with open('user_data.json','r',encoding='utf-8')as f:
               return(json.load(f))
     except:
          return None
money=100
stock=0 
day=1
weather='晴天'
target=500
random_thing='无事发生'
reputation=0 
debt=0 
game_data=load_data()
if game_data is not None:
     day=game_data['day']
     money=game_data['money']
     stock=game_data['stock']
     weather=game_data['weather']
     target=game_data['target' ]
     random_thing=game_data['random_thing']
     reputation=game_data['reputation']
     debt=game_data['debt']
print('=====欢迎来到奶茶店================================')
while True:
    os.system('cls')
    print(f'\n第{day}天，资金：{money}，库存：{stock}，天气：{weather}，目标：{target},随机事件：{random_thing},声望：{reputation},欠款：{debt}')
    print(f"""1,制作(成本5元/杯)
2,售卖(一天只开张一次)
3,休息(经过一天的宣传，第二天有概率触发一次随机事件！）
4,退出
5,清档重来
6,银行(当前欠款：{debt})
""")
    choice=get_number('请输入你的选择(1-6):')
    if choice==1:
          while True:
            num=get_number('请输入进货数量  (5/杯)')
            if num==0:
                print('#### 取消进货。####')
                input('\n按回车键继续')
                break
            elif money>=5*num and num>0:
                money=money-5*num 
                stock=stock+num
                print('#### 进货成功！####')
                save_data(day,money,stock,weather,target,random_thing,reputation,debt)
                input('\n按回车键继续')
                break
            else:
                print('#### 输入错误或资金不足！####')
                input('\n按回车键继续')
                continue
    elif choice==2:
         print(f'\n第{day}天，资金：{money}，库存：{stock}，天气：{weather},随机事件：{random_thing},声望：{reputation}')
         print('##### 天气和定价都会影响客流量，请合理定价 #####')
         price=get_number('请输入单杯售价 ')
         if weather=='晴天':
             max_base=25
             min_base=15
         elif weather=='雨天':
             max_base=10
             min_base=3
         elif weather=='阴天':
             max_base=16
             min_base=5
         else:
             max_base=35
             min_base=20
         price_offerset=(price-10)*2
         remax_base=max(0,max_base-price_offerset)
         remin_base=max(0,min_base-price_offerset)
         if remax_base==0:
                print('#### 价格过高,客流量为0 ####')
                input('\n按回车键继续')
                day+=1
                save_data(day,money,stock,weather,target,random_thing,reputation,debt)
                continue
         else:
                base_customer=random.randint(remin_base,remax_base)
                second_customer=int(base_customer*(1+(reputation/200)))
                if second_customer<=0:
                     second_customer=0
                     print('## 由于小店声誉太低，没有客人光顾！##')
                     day+=1
                     save_data(day,money,stock,weather,target,random_thing,reputation,debt)
                else:
                    if random_thing=='门口修路':
                       customer=max(0,second_customer-10)
                       print('## 由于门口修路,客流量减少10位 ##')
                       input('\n按回车键继续')
                    else:
                        customer=second_customer
                    print(f'## 今天有{customer}位顾客光临 ##')
                    if stock>=customer:
                      money=money+price*customer
                      stock=stock-customer
                      print(f'##卖出{customer}杯奶茶，收入{price*customer}##')
                      weather=random.choice(['晴天','雨天','阴天','学校活动'])
                      print('## 天色已晚，明天再卖吧！##')
                      day+=1
                      save_data(day,money,stock,weather,target,random_thing,reputation,debt)
                      input('\n按回车键继续')
                      continue
                    else:
                      money=money+price*stock
                      print(f'## 库存有限，卖出{stock}杯奶茶，收入{price*stock}元 ##')
                      stock=0
                      day+=1
                      weather=random.choice(['晴天','雨天','阴天','学校活动'])
                      print('## 天色已晚，明天再卖吧！##')
                      input('\n按回车键继续')
                      save_data(day,money,stock,weather,target,random_thing,reputation,debt) 
                      continue       
    elif choice==3:
        weather=random.choice(['晴天','雨天','阴天','学校活动'])
        random_thing=random.choice(['网红探店','门口修路','无事发生'])
        print(f'## 新的一天开始了！今天是{weather},今天的随机事件是{random_thing}!##')
        input('\n按回车键继续')
        if random_thing=='无事发生':
            print('## 今天没有发生任何事情 ##')
            input('\n按回车键继续')
        elif random_thing=='网红探店':
            reputation+=10
            reputation=max(-100,min(100,reputation)) 
            print(f'## 一位网红来店里！小店声誉增加为{reputation} ##')
            input('\n按回车键继续') 
        day+=1
        save_data(day,money,stock,weather,target,random_thing,reputation,debt)
        continue
    elif choice==4:
        print('#### 您已退出游戏 ####')
        save_data(day,money,stock,weather,target,random_thing,reputation,debt)
        break
    elif choice==5:
         try:
          os.remove('user_data.json')
         except:
              pass
         money=100
         stock=0 
         day=1
         weather='晴天'
         target=500
         random_thing='无事发生'
         debt=0
         reputation=0
         debt=0 
         print('#### 存档已清空，小店重新开张！####')
         input('\n按回车键继续')
         continue 
    elif choice==6:
         max_loan=max(0,reputation*5)
         print(f'##当前欠款为{debt}##')
         remaining_loan=max_loan-debt
         if remaining_loan==0:
          print('## 由于声誉和欠款额度的原因，你无法贷款！##')
          input('\n按回车键继续')
          continue
         elif remaining_loan>0:
              print('##温馨提示:贷款额度与声誉挂钩，当欠款达到一定数值,且判定你无还款能力时,你会直接破产！##')
              print(f'##当前可借额度为{remaining_loan}元##')
              bank_choice=get_number("""1.贷款\n 2.还款\n 3.离开\n
                     请输入你的选择(1-3):""")
              if bank_choice==1:
                while True:
                  bank_choice1=get_number('##请输入贷款数额 ##')
                  if bank_choice1<=remaining_loan:
                      debt+=bank_choice1
                      money+=bank_choice1
                      print(f'##贷款成功！，你现在拥有{money}元，贷款{debt}##')
                      save_data(day,money,stock,weather,target,random_thing,reputation,debt)
                      input('\n按回车键继续')
                      break
                  elif bank_choice1==0:
                      print('##你已取消贷款##')
                      input('\n按回车键继续')
                      break
                  else:
                      print('##贷款不可大于可借额度！##')
                      input('\n按回车键继续')
                      continue

              elif bank_choice==3:
                    continue
              elif bank_choice==2:
                   if debt==0:
                       print('##你当前没有欠款##')
                       input('\n按回车键继续')
                   else:
                       repay_amount=get_number('##请输入还款金额##')
                       if repay_amount<=debt and repay_amount<=money and repay_amount>0:
                           debt-=repay_amount
                           money-=repay_amount
                           print(f'##还款成功！如今欠款{debt}##')
                           save_data(day,money,stock,weather,target,random_thing,reputation,debt)
                           input('\n按回车键继续')
                           continue
                       elif repay_amount==0:
                           print('##你已取消还款##')
                           input('\n按回车键继续')
                           continue
                       elif repay_amount>money:
                           print('##你没有足够的资金还款！##')
                           input('\n按回车键继续')
                           continue
                       else:  
                           money-=debt
                           print(f'##你已还清贷款，拥有{money}元##')
                           debt=0
                           save_data(day,money,stock,weather,target,random_thing,reputation,debt)
                           input('\n按回车键继续')
              else:
                        print('#### 请输入正确的数字 ####')
                        input('\n按回车键继续')
                        continue 

    else: 
        print('#### 请输入正确的数字 ####')
        input('\n按回车键继续')
        continue

    if money>=target:
          print(f'恭喜你，达成{target}，游戏胜利！')
          free_choice=get_number('#如果您想继续,请按1,退出请按2#')
          if free_choice==2:
                print('#### 您已退出游戏 ####')
                break
          elif free_choice==1:
                target=target*2
                print(f'## 进入无尽模式，新目标是赚到{target}!##')
                input('\n按回车键继续')
          else:
                print('#### 请输入正确的数字 ####')
                input('\n按回车键继续')
                continue
    else:
        pass
    if  money<5 and stock<=0:
       max_loan=max(0,reputation*5)  
       if debt>=max_loan:
           print('##小店破产，游戏失败！##')
           input('\n按回车键继续')
           break
       else:
            print('##快去银行看看吧！##')
            print('##1.去银行 2.结束游戏##')
            end_chioce=get_number("请输入你的选择")
            if end_chioce==2:
                 print('#### 您已退出游戏 ####')
                 save_data(day,money,stock,weather,target,random_thing,reputation,debt)
                 break
            elif end_chioce==1:
                continue
            else:
                 print('#### 请输入正确的数字 ####')
                 input('\n按回车键继续')
                 continue
               
                
            
    else:
        pass
        
    
                
          



