import datetime,xlsxwriter,glob

#Reading the list of input files
yesterday=(datetime.datetime.today() - datetime.timedelta(days=1))
folder_name=yesterday.strftime ("%b %d")
files=glob.glob(folder_name+"\\*.csv")

#Reading the list of STBdevices.
spec_mac_file=open(folder_name+"\\all_spec_macs.csv")
#count is the list containing the number of Spectrum and non spectrum macs count in the order ["spec","non-spec"]

#Populating spec_mac_list with the data from spec_mac_file
spec_mac_row=spec_mac_file.readline().split(",")
spec_mac_list=[]
while(not(spec_mac_row==['']) ):
    spec_mac_list.append(spec_mac_row[2].replace('\n',''))
    spec_mac_row=spec_mac_file.readline().split(",")
spec_mac_file.close()

chart_name_dict={}
error_name=open("error_name.csv")
for row in error_name.readlines():
    error=row.split(",")
    chart_name_dict[error[0]]=error[1].replace("\n","")
#print(chart_name_dict)

for event_file_name in files:    

    if((folder_name+"\\all_spec_macs.csv")==event_file_name):
        continue
    #Setting duration interval
    duration_step=60
    
    min_time_stamp= datetime.datetime.strptime("00:00:00","%H:%M:%S")
    max_time_stamp=min_time_stamp+datetime.timedelta(minutes=duration_step)
    event_file=open(event_file_name,"r")
    
    event_row=event_file.readline().split(",")
    event_row=event_file.readline().split(",")
    error_code=event_row[0].replace('"','')
    count_dict=dict()
    count_list=[0,0]
    while(min_time_stamp.date()==datetime.datetime(1900,1,1).date()):
        #print(event_row)
        event_time_stamp=event_row[2]
        event_date_time=event_time_stamp.split()
        event_time_str=event_date_time[1]
        
        time_format="%H:%M:%S"
        if(len(event_date_time)==3):
            #print(event_time_str)
            event_time_str=event_date_time[1]+" "+(event_date_time[2].replace('"',''))
            
            time_format="%I:%M:%S %p"
        
        try:
            event_time=datetime.datetime.strptime(event_time_str,"%H:%M:%S")
        except ValueError:
            event_time=datetime.datetime.strptime(event_time_str,"%H:%M")
        
        event_error_code=event_row[0]
        event_mac=event_row[3]
        converted_event_mac_temp=event_mac.replace('"','')
        converted_event_mac="STB"+converted_event_mac_temp.replace(":",'')
        
        if(min_time_stamp<=event_time<max_time_stamp):
            
            if(converted_event_mac in spec_mac_list):
                #if(min_time_stamp.hour==16):
                    #print(min_time_stamp,converted_event_mac)
                count_list[0]+=1    
            else:
                #print(converted_event_mac)
                count_list[1]+=1
            event_row=event_file.readline().split(",")
            #print(event_row)
            if(event_row==['']):
                #print(min_time_stamp)
                break
        else:
            hour_str=str(min_time_stamp.hour)
            if(min_time_stamp.hour==0):
                hour_str="00"
            min_str=str(min_time_stamp.minute)
            if(min_time_stamp.minute==0):
                min_str="00"
            time_format=hour_str+":"+min_str
        
            count_dict[time_format]=count_list
            #print(time_format,count_list)
            count_list=[0,0]
            min_time_stamp=min_time_stamp+datetime.timedelta(minutes=duration_step)
            max_time_stamp=max_time_stamp+datetime.timedelta(minutes=duration_step)
                   
    while(min_time_stamp.date()==datetime.datetime(1900,1,1).date()):
        
        hour_str=str(min_time_stamp.hour)
        if(min_time_stamp.hour==0):
            hour_str="00"
        min_str=str(min_time_stamp.minute)
        if(min_time_stamp.minute==0):
            min_str="00"
        time_format=hour_str+":"+min_str
        
        count_dict[time_format]=count_list
        #print(min_time_stamp)
        count_list=[0,0]
        min_time_stamp=min_time_stamp+datetime.timedelta(minutes=duration_step)
        max_time_stamp=max_time_stamp+datetime.timedelta(minutes=duration_step)
        
    
    workbook = xlsxwriter.Workbook(event_file_name[:-4]+"_Out.xlsx")
    worksheet = workbook.add_worksheet("abc")
    
    worksheet.write(0,0,"Time")
    worksheet.write(0,1,"spec")
    worksheet.write(0,2,"non-spec")
    i=1
    spec_count_sum=0
    non_spec_count_sum=0
    for count_data_time,count_data_list in count_dict.items():
        worksheet.write(i,0,count_data_time)
        worksheet.write(i,1,count_data_list[0])
        spec_count_sum+=count_data_list[0]
        worksheet.write(i,2,count_data_list[1])
        non_spec_count_sum+=count_data_list[1]
        i+=1
    
    worksheet.write(i,0,"Total")
    worksheet.write(i,1,spec_count_sum)
    worksheet.write(i,2,non_spec_count_sum)
    
    #chart2 = workbook.add_chart({'type': 'pie'})
    chart2 = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})
    chart2.add_series({
        'name':       '=abc!$B$1',
        'categories': '=abc!$A$2:$A$25',
        'values':     '=abc!$B$2:$B$25',
        'fill':       {'color': '#F79646'},
        'major_gridlines': {'visible': False},
        'gap':        15,
    })
    chart2.add_series({
        'name':       '=abc!$C$1',
        'categories': '=abc!$A$2:$A$25',
        'values':     '=abc!$C$2:$C$25',
        'fill':       {'color': '#5B9BD5'},
        'major_gridlines': {'visible': False},
        'gap':        15,
    })
    chart2.set_x_axis({
        'name': '=abc!$A$1',
        'name_font': {'size': 10, 'bold': False},
    })
    chart2.set_y_axis({
        'name': 'Failed sessions',
        'name_font': {'size': 10, 'bold': False},
    })
    chart2.set_chartarea({'border': {'none': True}})
    chart2.set_size({'width': 576, 'height': 280})
    chart2.set_legend({'position': 'bottom'})
    #chart_name="VOD Error - "+event_row[0].replace('"','')+" ("+event_row[1].replace('"','')+")"
    chart2.set_title({
            'name': "VOD Error - "+error_code+" "+chart_name_dict[error_code],
            'name_font': {'size': 12, 'bold': True},
            })
    worksheet.insert_chart('E2', chart2, {'x_offset':0, 'y_offset': 0})
    
    chart1 = workbook.add_chart({'type': 'pie'})
    chart1.add_series({
        'categories': '=abc!$B$1:$C$1',
        'values':     '=abc!$B$26:$C$26',
        #'line':   {'width': 1},
        #'name': '=DVR!$B$1',
        #'major_gridlines': {'visible': True,'color':'red'},
        'gap': 0.5,
        'points': [
        {'fill': {'color': '#F79646'}},
        {'fill': {'color': '#5B9BD5'}},
        
    ],
        'data_labels': {'percentage': True, 'value': True, 'position': 'center','separator': "\n", 
                        'font': {'color': 'white'}},       
    })
    chart1.set_chartarea({'border': {'none': True}})
    chart1.set_size({'width': 230, 'height': 280})
    chart1.set_legend({'position': 'bottom'})
    worksheet.insert_chart('N2', chart1, {'x_offset': 0, 'y_offset': 0})
    
    event_file.close()
    workbook.close()
