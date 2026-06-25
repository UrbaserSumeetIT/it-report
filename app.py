try:
    import pandas as pd
    import streamlit as st
    import openpyxl
except ImportError as e:
    print(f'Error: {e}')


st.set_page_config(
    page_title= "Urbaser Sumeet | RCV Report Generator",
    page_icon= "logo.png",
    layout= 'wide'
)

st.title("RCV Report Generator")

with st.container(border=True,width=300 ):
    #decalared variable for File Handling
    binunloading = st.file_uploader("Upload BinUnloading .xlsx File"    )
    kpi72 = st.file_uploader("Upload KPI72 .xlsx File")
    vehicle_master = st.file_uploader("Upload Vehicle master .xlsx File")
    
    

try:
   
    

    if binunloading is not None and kpi72 is not None and vehicle_master is not None:
        #binunloading
        bu = pd.read_excel(binunloading)
        #kpi72
        k72 = pd.read_excel(kpi72)
        #vehicle_master
        vm = pd.read_excel(vehicle_master,sheet_name='vehiclemaster',skiprows=3)
        
        count = (
            bu['Vehicle RTO']
            .value_counts()
            .reset_index()
        )
        count.columns = ['Vehicle Number', 'count']    
        #KPI7.2 processing data
        kpi72_d = k72.loc[
            k72['Zone'].notna(),
            [
                'Kpi Date', 
                'Vehicle Number',
                'Zone',
                'Vehicle Category',
                ' Out In Timings'
            ]
                
        ]

        kpi72_d['Kpi Date'] = pd.to_datetime(kpi72_d['Kpi Date']).dt.strftime('%d-%m-%Y')

        df = pd.merge(kpi72_d,count,how='left',on='Vehicle Number')

        df['count'] = df['count'].fillna(0)
        
        vm.columns = ['Vehicle Number',	'V ID','Vehicle Type',	'Zone_',	'Facility',	'Technician']


        df = pd.merge(df,vm,how='left',on='Vehicle Number')

        less_30 = df[df['count']<=30]

        less_30 = less_30[['Kpi Date','Vehicle Number','Vehicle Category' ,'Marching In Out Timings','Zone','Facility','count','Technician']]


        unique_vehicle = (
            less_30
            .drop_duplicates(subset=['Vehicle Number'])
            .reset_index(drop=True)
        )
        
        
        
        
        
        
        #less 30 count Vehicle list
        unique_vehicle.sort_values(by=['Facility','count'],inplace=True)
        unique_vehicle.index = range(1,len(unique_vehicle)+1)

        with st.container(border=True,width=800):
            col1, col2, col3 = st.columns(3)

        with st.container(border=True):
            st.header("RCV Less 30 Bin Count Vehicle List")
            st.metric("Total Vehicles",unique_vehicle['Vehicle Number'].nunique(),width="content",height='content')
            st.markdown("---")
            st.dataframe(
            unique_vehicle,
            width='stretch',
            hide_index=False)
        
        #less all Vehicle List
        r = df.drop_duplicates(subset=['Vehicle Number']).reset_index(drop=True)
        r = r[['Kpi Date','Vehicle Number','Vehicle Category' ,'Marching In Out Timings','Zone','Facility','count','Technician']]
        r.sort_values(by=['Facility','count'],inplace=True)
        r.index = range(1,len(r)+1)
        compliance = round(
            (1 - len(unique_vehicle) / len(r)) * 100,
            2
        )

        with col1:
            st.metric(
        "Total Deployed Vehicles",
        r['Vehicle Number'].nunique(),border=True
        )

        with col2:
         st.metric(
        "<=30 Bins lift RCV Vehicles",
        unique_vehicle['Vehicle Number'].nunique(),
        border=True
        )
      
        with col3:
         st.metric(
        ">30 bins lift RCV Vehicle in %",
        f'{compliance}%',border=True,
        )
        with st.container(border=True):
            st.header("All Deployed RCV Vehicles")
            st.metric("Total Vehicles",r['Vehicle Number'].nunique(),width="content",height='content')
            st.markdown("---")
            st.dataframe(r, width="stretch")
            
        
except Exception as e:
    st.error(f'Error: {e}')
