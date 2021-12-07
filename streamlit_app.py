import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

nooftemperature = []
nooftests = []
testkeys = []


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

def plot_functionaltests(df):

    #st.write(testkeys)
    powertest = df.loc[(df['TestType'] == 1) & (df['TestID'] == 1)]
    plot_quicktest(powertest)

    powertestresult = df.loc[ (df['TestID']==1) & (df['TestType']==2)]
    displayresult = powertestresult[['SBV', 'TargSBV', 'Time', 'Date', 'TargTemp',
       'OvenTemp', 'ToolTemp', 'SubbusV', 'SubbusI', '3.6V', '11V', '6.8V',
       'DAC_0.0V', 'DAC_1.4V', 'DAC_2.2V', 'DAC_2.8V', 'DAC_4.3V']].set_index('TargTemp').T
    #displaypowertest = displayresult.to_frame()
    st.table(displayresult)

    for i in range(1, nooftemperature + 1):
        for ts in range(2,10):
            st.write(testnames[ts])
            bwtestresult = df.loc[(df['TestID']==ts) & (df['TestType']==2)].copy()
            bwtestresult.head()
            if (ts in [2,3]):
                xlabel = 'InFrequency'
                refcolumns = ['NearRMS','FarRMS']
                normalizedcolumns = ['NormalizedNearRMS','NormalizedFarRMS']
                columntodisplay =['InFrequency','ExPhase','StPhase','NearAGC','FarAGC','NormalizedNearRMS','NormalizedFarRMS']
                hlimits = []
                llimits = []
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
                columntodisplay = ['InAmp','ExPhase', 'StPhase', 'NearAGC', 'FarAGC', 'NormalizedExPhase', 'NormalizedStPhase']
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
                columntodisplay = ['InAmp', 'NearRMS', 'FarRMS', 'CorrectedNearRMS', 'CorrectedFarRMS']
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
                columntodisplay = ['InPhase','ExPhase', 'StPhase','NormalizedExPhase', 'NormalizedStPhase']
                calresultcolumn = []
                yrange = [-1, 1]
                lookupreference = 0.0
                xreverse = False

            ExPhaseOffset = []
            StPhaseOffset = []
            currenttemp = temperatures.loc[temperatures['Segment']==i]
            titletext = testnames[ts] + " at " + currenttemp['TargTemp'].to_string(index=False) + "degC"

            currentbw = bwtestresult.loc[bwtestresult['Segment']==i]
            bwcenter = currentbw.loc[currentbw[xlabel]==lookupreference]
            for colcount in range (0,len(refcolumns)):
                currentbw[normalizedcolumns[colcount]]=currentbw[refcolumns[colcount]] - bwcenter.iloc[0][refcolumns[colcount]]
            tabletodisplay = currentbw[columntodisplay].copy()
            st.table(tabletodisplay.assign(hack='').set_index('hack'))
            #st.table(tabletodisplay)
            fig, ax1= plt.subplots(figsize=(8,4))
            for colcount in range (0,len(refcolumns)):
                ax1.plot(currentbw[xlabel], currentbw[normalizedcolumns[colcount]], label=normalizedcolumns[colcount]+str(i))
            ax1.set_ylim(yrange[0],yrange[1])
            ax1.legend()
            ax1.grid()
            ax1.set_title(titletext)
            if (xreverse): plt.gca().invert_xaxis()
            #pdf.savefig()
            plt.show()
            st.pyplot(fig)

with header:
    st.title('Welcom to my project!')

with dataset:
    st.header("This is the dataset!")
    uploadedFile = st.file_uploader("Upload CSV data", type=['csv'], accept_multiple_files=False, key="fileUploader")
    if uploadedFile is not None:
        df = pd.read_csv(uploadedFile, error_bad_lines=True, warn_bad_lines=False, sep=',')
        df.columns = df.columns.str.strip()

        if ((df.shape[1] != 34) | (df.shape[0] <= 2) | (columnset.issubset(df.columns) == False)):
            st.error('CSV structure not recognized!')
        else:
            st.success('All required columns were found!')
            lastrun = df['RunNumber'].unique()[-1]
            st.write('Plotting for RUN :',lastrun)
            df = df.loc[df['RunNumber']==lastrun]
            nooftemperature = df.nunique()[4]
            nooftests = df.nunique()[6]
            temperatures = df[['Segment','TargTemp']].drop_duplicates()
            testtemp = ""
            st.info("Test Temperatures :", testtemp)
            styler = temperatures['TargTemp'].to_frame().T
            st.dataframe(styler.assign(hack='').set_index('hack'))
            st.write("Quick test include:", "yes" if df.nunique()[5] > 1 else "no")
            st.write("Number of tests   :", df.nunique()[6])
            testkeys = df['TestID'].value_counts().index.tolist()
            testkeys.sort()
            plot_functionaltests(df)

