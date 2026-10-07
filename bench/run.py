import argparse,csv,json,time
def record(provider,model,started,ended,ok,error=''):
 return {'provider':provider,'model':model,'ttft_ms':round((ended-started)*1000,2),'success':ok,'error':error}
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',default='results.csv');a=p.parse_args()
 with open(a.output,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['provider','model','ttft_ms','success','error']);w.writeheader()
 print('No live measurements were run; provide your own adapter and append rows.')
if __name__=='__main__':main()
