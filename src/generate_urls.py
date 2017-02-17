from datetime import datetime, timedelta
from dateutil import rrule

def generate_urls(start_date,end_date,sampling, interval=1):
    sampling_dict = {'DAILY':rrule.DAILY,'MONTHLY':rrule.MONTHLY,'YEARLY':rrule.YEARLY}

    dates = [datetime.strftime(dt,'%Y/%m/%d') for dt in rrule.rrule(sampling_dict[sampling],
                          dtstart=datetime.strptime(start_date, '%Y/%m/%d'),
                          until=datetime.strptime(end_date, '%Y/%m/%d'),interval=interval)]

    IPAddress = 'https://lazycache-dot-ferrous-ranger-158304.appspot.com/v1/org/oceanobservatories/rawdata/'
    # IPAddress = 'https://rawdata.oceanobservatories.org/'
    base_url = IPAddress+'files/RS03ASHS/PN03B/06-CAMHDA301/'

    urls = []
    for date in dates:
        urls.append(base_url+date+'/CAMHDA301-'+date.replace("/","")+'T000000Z.mov')

    return(urls)

if __name__ == '__main__':
  import argparse
  from datetime import datetime, timedelta
  from collections import OrderedDict

  parser = argparse.ArgumentParser(description="Format is mm/yy")
  parser.add_argument('-start_date','--start_date',type=str,required=True)
  parser.add_argument('-end_date','--end_date',type=str,required=True)
  parser.add_argument('-sampling','--sampling',type=str,required=True)
  args = parser.parse_args()


  # transfer files by months

  urls = generate_urls(args.start_date,args.end_date,args.sampling)
