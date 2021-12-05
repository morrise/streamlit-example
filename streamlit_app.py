import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, HTML

st.set_option('deprecation.showPyplotGlobalUse', False)

header = st.container()
dataset = st.container()
features = st.container()
modelTraining = st.container()

columnset = set(['RunNumber', 'Mother_SN', 'Daugther_SN', 'Cycle', 'Segment', 'TestType',
                 'TestID', 'ELS', 'SBV', 'TargSBV', 'Time', 'Date', 'TargTemp',
                 'OvenTemp', 'ToolTemp', 'SubbusV', 'SubbusI', '3.6V', '11V', '6.8V',
                 'DAC_0.0V', 'DAC_1.4V', 'DAC_2.2V', 'DAC_2.8V', 'DAC_4.3V',
                 'InFrequency', 'InAmp', 'InPhase', 'ExPhase', 'StPhase', 'NearAGC',
                 'FarAGC', 'NearRMS', 'FarRMS'])

testnames = ["", "Power", "2MHz Band Width", "1MHz Band Width",
             "2MHz Phase vs Amplitude", "1MHz Phase vs Amplitude",
             "2MHz Corrected Amplitude", "1MHz corrected amplitude",
             "2MHz Phase Linearity", "1MHz Phase Linearity"]

def plot_quicktest(powertest):
    leftside = ['OvenTemp', 'ToolTemp', 'SubbusI']
    rightside = ['SubbusV','11V', '6.8V','DAC_0.0V', 'DAC_1.4V', 'DAC_2.2V', 'DAC_2.8V', 'DAC_4.3V']
    fig,ax1 = plt.subplots(figsize=(8,6))
    ax2 = ax1.twinx()
    for i in leftside:
        ax1.plot(powertest['ELS'],powertest[i],label=i)
    for i in rightside:
        ax2.plot(powertest['ELS'],powertest[i],label=i)
    ax1.set_xlabel("ELS")
    ax1.set_ylabel("Temperature (C) / Current (mA)")
    ax2.set_ylabel("Voltage (V)")
    ax2.set_ylim(0,21)
    ax1.legend()
    ax2.legend(loc="right")
    ax1.set_title("QUICK TEST PLOT")
    #fig.tight_layout()
    #pdf.savefig()  # saves the current figure into a pdf page
    plt.show()
    st.pyplot(fig)

def show_powertest(df):
    powertestresult = df.loc[ (df['TestID']==1) & (df['TestType']==2)]
    displayresult = powertestresult[['SBV', 'TargSBV', 'Time', 'Date', 'TargTemp',
       'OvenTemp', 'ToolTemp', 'SubbusV', 'SubbusI', '3.6V', '11V', '6.8V',
       'DAC_0.0V', 'DAC_1.4V', 'DAC_2.2V', 'DAC_2.8V', 'DAC_4.3V']].set_index('TargTemp').T
    st.dataframe(displayresult)   
    
def plot_functionaltests(df):
    nooftemperature = df.nunique()[4]
    nooftests = df.nunique()[6]
    st.write("no of temperature :", df.nunique()[4])
    st.write("quick test include:", "yes" if df.nunique()[5] > 1 else "no")
    st.write("no of tests       :", df.nunique()[6])
    testkeys = df['TestID'].value_counts().index.tolist()
    testkeys.sort()
    #st.write(testkeys)
    powertest = df.loc[(df['TestType'] == 1) & (df['TestID'] == 1)]
    plot_quicktest(powertest)
    show_powertest(df)
    for ts in range(2,10):
        st.write(testnames[ts])
        bwtestresult = df.loc[(df['TestID']==ts) & (df['TestType']==2)].copy()
        bwtestresult.head()
        if (ts in [2,3]):
            xlabel = 'InFrequency'
            refcolumns = ['NearRMS','FarRMS']
            normalizedcolumns = ['NormalizedNearRMS','NormalizedFarRMS']
            yrange = [-2, 2]
            calresultcolumn = []
            if (ts == 2):
                lookupreference = 2000000.0
            else:
                lookupreference = 1000000.0
            xreverse = False
        elif (ts in [4,5]):
            xlabel = 'InAmp'
            refcolumns = ['ExPhase','StPhase']
            normalizedcolumns = ['NormalizedExPhase','NormalizedStPhase']
            yrange = [-1, 1]
            calresultcolumn = []
            if (ts == 4):
                lookupreference = -65.0
            else:
                lookupreference = -75.0
            xreverse = True
        elif (ts in [6,7]):
            xlabel = 'InAmp'
            refcolumns = ['NearRMS','FarRMS']
            normalizedcolumns = ['CorrectedNearRMS','CorrectedFarRMS']
            calresultcolumn = ['Ratio']
            yrange = [-1, 1]
            if (ts == 4):
                lookupreference = -65.0
            else:
                lookupreference = -75.0
            xreverse = True
        elif (ts in [8,9]):
            xlabel = 'InPhase'
            refcolumns = ['ExPhase','StPhase']
            normalizedcolumns = ['NormalizedExPhase','NormalizedStPhase']
            calresultcolumn = []
            yrange = [-1, 1]
            lookupreference = 0.0
            xreverse = False

        ExPhaseOffset = []
        StPhaseOffset = []
        fig, ax1= plt.subplots(figsize=(8,4))
        for i in range(1,nooftemperature+1):
            currentbw = bwtestresult.loc[bwtestresult['Segment']==i]
            bwcenter = currentbw.loc[currentbw[xlabel]==lookupreference]
            for colcount in range (0,len(refcolumns)):
                currentbw[normalizedcolumns[colcount]]=currentbw[refcolumns[colcount]] - bwcenter.iloc[0][refcolumns[colcount]]
                ax1.plot(currentbw[xlabel], currentbw[normalizedcolumns[colcount]], label=normalizedcolumns[colcount]+str(i))
        ax1.set_ylim(yrange[0],yrange[1])
        ax1.legend()
        ax1.grid()
        ax1.set_title(testnames[ts])
        if (xreverse): plt.gca().invert_xaxis()
        #pdf.savefig()
        plt.show()
        st.pyplot(fig)

with dataset:
    uploadedFile = st.file_uploader("Upload CSV data", type=['csv'], accept_multiple_files=False, key="fileUploader")
    if uploadedFile is not None:
        df = pd.read_csv(uploadedFile, error_bad_lines=True, warn_bad_lines=False, sep=',')
        st.write(df.head())
        df = df.loc[df['RunNumber'] == df['RunNumber'].iloc[-1]]
        df.columns = df.columns.str.strip()
        
        if ((df.shape[1]!=34) & (df.shape[0]<2) & (columnset.issubset(df.columns)!=True)): 
            st.write('CSV structure not recognized!')
        else:
            st.write('All required columns were found!')
            plot_functionaltests(df)

