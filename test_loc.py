import requests
h={'User-Agent':'M','Accept':'a/j','Origin':'https://jobvision.ir','Referer':'https://jobvision.ir/'}
r=requests.post('https://candidateapi.jobvision.ir/api/v1/JobPost/List',json={'page':1,'pageSize':5,'sort':0,'keyword':'python','filters':{'locationSlugs':['in-all-cities-of-tehran']}},headers=h,timeout=15)
d=r.json()
print('total',d['data']['jobPostCount'])
for j in d['data']['jobPosts'][:5]:
  loc=j.get('location',{})
  c=loc.get('city',{}) or {}
  print(c.get('titleFa',''))
