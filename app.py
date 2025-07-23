import streamlit as st
import random
from time import sleep
from utils import Tester
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()


st.set_page_config(layout="wide")

if 'tester' not in st.session_state:
    st.session_state.tester = Tester()

st.markdown("<h1 style='text-align: center;'>Nokia Test Suite</h1>", unsafe_allow_html=True)

tab_reqs, tab_test, tab_vis = st.tabs(["Requirements", "Testing", "Visualize"])

with tab_reqs:
    st.markdown("<h2 style='text-align: center;'>Requirements</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Inputs</h3>", unsafe_allow_html=True)
    
    # Initialize inputs table in session state if not exists
    if 'inputs_table' not in st.session_state:
        st.session_state.inputs_table = {
            "Name": ["Rx Power (dBm)", "Tx Power (dBm)", "Frequency (GHz)", "Bandwidth (MHz)"],
            "Min": [-9, -28, 190000, 125],
            "Max": [+3, 0, 360000, 10000]
        }
    
    # Editable inputs table
    st.session_state.inputs_table = st.data_editor(
        st.session_state.inputs_table,
        disabled=["Name"],
        use_container_width=True,
        key="inputs_editor",
        column_config={
            "Min": st.column_config.NumberColumn("Min", step=0.001, format="%.2f"),
            "Max": st.column_config.NumberColumn("Max", step=0.001, format="%.2f")
        }
    )
 
    st.markdown("<h3 style='text-align: center;'>Outputs</h3>", unsafe_allow_html=True)
    
    # Initialize outputs table in session state if not exists
    if 'outputs_table' not in st.session_state:
        st.session_state.outputs_table = {
            "Name": ["Boot Time (s)", "Temperature (°C)", "Data Throughput (Mbps)", "Error Rate (%)"],
            "Min": [0.0, -15.0, 0.0, 0.0],
            "Max": [10.0, 45.0, 1.0, 5.0]
        }
    
    # Editable outputs table
    st.session_state.outputs_table = st.data_editor(
        st.session_state.outputs_table,
        disabled=["Name"],
        use_container_width=True,
        key="outputs_editor",
        column_config={
            "Min": st.column_config.NumberColumn("Min", step=0.001, format="%.2f"),
            "Max": st.column_config.NumberColumn("Max", step=0.001, format="%.2f")
        }
    )


with tab_test:
    ## Two columns in the test tab: One for testing inputs and one to resemble a terminal output to show logs live...
    col_input, col_output = st.columns(2)
    with col_input:
        st.markdown("<h3 style='text-align: center;'>Manual Testing</h3>", unsafe_allow_html=True)
        # Create four columns for buttons
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
        
        input_list = st.text_input("Enter sensor inputs (comma-separated):")
        
        with btn_col1:
            if st.button("🔦 Test LED", use_container_width=True, type="primary"):
                st.session_state.tester.testLED()
        with btn_col2:
            if st.button("⚡ Test Power", use_container_width=True, type="primary"):
                st.session_state.tester.testPower()
        with btn_col3:
            if st.button("📡 Test Ping", use_container_width=True, type="primary"):
                st.session_state.tester.testPing()
        with btn_col4:
            if st.button("🔧 Test Paramaters", use_container_width=True, type="primary"):
                if input_list:
                    input_list = list(map(int, input_list.split(',')))
                    st.session_state.tester.testSensors(input_list)
        
        ##  Automated Testing Section
        st.markdown("<h3 style='text-align: center;'>Automated Testing</h3>", unsafe_allow_html=True)
        ##  Random Search Section
        st.markdown("<h4 style='text-align: center;'>Random Search</h4>", unsafe_allow_html=True)
        random_left, random_middle, random_right = st.columns(3)
        with random_left:
            st.markdown("#### Number of tests to run:")
        with random_middle:
            num_tests = st.number_input(label="", min_value=1, max_value=100, value=10, label_visibility="collapsed")
        with random_right:
            random_test_button = st.button("Generate Tests", use_container_width=True, type="primary")

        if random_test_button:
            ##  Generate random tests based on the input ranges
            inputs = st.session_state.inputs_table
            test_input_list = []
            for _ in range(num_tests):
                test_input = []
                for i in range(len(inputs["Name"])):
                    min_val = inputs["Min"][i]
                    max_val = inputs["Max"][i]
                    test_input.append(round(random.uniform(min_val, max_val), 3))
                test_input_list.append(test_input)
            ##  Log the generated tests
            st.session_state.tester.log(f"Generated {num_tests} random tests!")
            
            ##  Show a progress bar and do each test
            progress_bar = st.progress(0)
            for i, test_input in enumerate(test_input_list):
                st.session_state.tester.testSensors(test_input)
                progress_bar.progress((i + 1) / num_tests)
                sleep(0.5)
        
    with col_output:
        st.markdown("""
        <style>
        .stCode > div > div > div > div {
            background-color: black !important;
            color: #00ff00 !important;
        }
        div[data-testid="stCode"] > div {
            background-color: black !important;
                    
        }
        div[data-testid="stCode"] pre {
            background-color: black !important;
            color: #00ff00 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        log_output = st.session_state.tester.log_file
        try:
            with open(log_output, 'r') as f:
                logs = f.read()
                st.code(logs, language=None, height=500)
        except FileNotFoundError:
            st.code("Log file not found. Please run tests first.", language=None)


with tab_vis:
    st.markdown("<h2 style='text-align: center;'>Visualize</h2>", unsafe_allow_html=True)
    input_df, output_df = st.session_state.tester.getSensorLogs()
    ##  Overall Report 
    ###  Show number of test runs, number of tests with all passed outputs and number of tests with failed outputs for each output
    st.markdown("<h3 style='text-align: center;'>Test Reports</h3>", unsafe_allow_html=True)
    ##  Show number of test runs
    total_tests = len(input_df)
    st.markdown(f"**Total Tests Run:** {total_tests}")
    ##  Show number of tests with all passed outputs
    passed_tests = 0
    for i in range(total_tests):
        passed = True
        for col in output_df.columns:
            min_val = st.session_state.outputs_table["Min"][st.session_state.outputs_table["Name"].index(col)]
            max_val = st.session_state.outputs_table["Max"][st.session_state.outputs_table["Name"].index(col)]
            if not (min_val <= output_df[col][i] <= max_val):
                passed = False
                break
        if passed:
            passed_tests += 1
    st.markdown(f"**Tests with All Outputs Passed:** {passed_tests}")
    ##  Show number of tests with failed outputs
    # Create data for the statistics table
    stats_data = []
    for col in output_df.columns:
        min_val = st.session_state.outputs_table["Min"][st.session_state.outputs_table["Name"].index(col)]
        max_val = st.session_state.outputs_table["Max"][st.session_state.outputs_table["Name"].index(col)]
        failed_count = sum((output_df[col] < min_val) | (output_df[col] > max_val))
        passed_count = total_tests - failed_count
        
        stats_data.append({
            "Output Parameter": col,
            "Passed Tests": f"{passed_count} ({(passed_count / total_tests) * 100:.1f}%)",
            "Failed Tests": f"{failed_count} ({(failed_count / total_tests) * 100:.1f}%)"
        })
    
    # Create and display the statistics table
    stats_df = pd.DataFrame(stats_data)
    
    
    def color_columns(col):
        if col.name == "Passed Tests":
            return ['background-color: lightgreen; color: black'] * len(col)
        elif col.name == "Failed Tests":
            return ['background-color: lightcoral; color: black'] * len(col)
        return [''] * len(col)
    
    # Apply styling and display
    styled_stats = stats_df.style.apply(color_columns, axis=0)
    st.dataframe(styled_stats, use_container_width=True, hide_index=True)
    
    ##  Input DataFrame
    st.markdown("<h3 style='text-align: center;'>Test Input Distribution</h3>", unsafe_allow_html=True)
    ####  Boxplots for each sensor input (displayed in a single row)
    ##  Show each sensor input with a different beautiful color
    colors = sns.color_palette("Set2", n_colors=len(input_df.columns))
    fig, axes = plt.subplots(nrows=1, ncols=len(input_df.columns), figsize=(20, 5))
    for i, col in enumerate(input_df.columns):
        sns.boxplot(data=input_df, x=col, ax=axes[i], color=colors[i])
        axes[i].set_title(col)
        
        # Add vertical lines for min/max requirements
        input_names = st.session_state.inputs_table["Name"]
        if col in input_names:
            idx = input_names.index(col)
            min_req = st.session_state.inputs_table["Min"][idx]
            max_req = st.session_state.inputs_table["Max"][idx]
            axes[i].axvline(x=min_req, color='green', linestyle='--', alpha=0.7, linewidth=2, label=f'Min: {min_req}')
            axes[i].axvline(x=max_req, color='green', linestyle='--', alpha=0.7, linewidth=2, label=f'Max: {max_req}')
            axes[i].legend()
    st.pyplot(fig)

    ##  Output DataFrame
    st.markdown("<h3 style='text-align: center;'>Test Output Distribution</h3>", unsafe_allow_html=True)
    ####  Boxplots for each sensor output (displayed in a single row)
    colors_output = sns.color_palette("Set1", n_colors=len(output_df.columns))
    fig, axes = plt.subplots(nrows=1, ncols=len(output_df.columns), figsize=(20, 5))
    for i, col in enumerate(output_df.columns):
        sns.boxplot(data=output_df, x=col, ax=axes[i], color=colors_output[i])
        axes[i].set_title(col)
        
        # Add vertical lines for min/max requirements
        output_names = st.session_state.outputs_table["Name"]
        if col in output_names:
            idx = output_names.index(col)
            min_req = st.session_state.outputs_table["Min"][idx]
            max_req = st.session_state.outputs_table["Max"][idx]
            axes[i].axvline(x=min_req, color='green', linestyle='--', alpha=0.7, linewidth=2, label=f'Min: {min_req}')
            axes[i].axvline(x=max_req, color='green', linestyle='--', alpha=0.7, linewidth=2, label=f'Max: {max_req}')
            axes[i].legend()
    st.pyplot(fig)
    
    ##  Input-Output DataFrame
    st.markdown("<h3 style='text-align: center;'>Test Reports</h3>", unsafe_allow_html=True)
    input_output_df = pd.concat([input_df, output_df], axis=1)
    
    # Define styling function for output columns
    def highlight_outputs(val, col_name):
        if col_name in output_df.columns:
            # Get the index of this output column
            output_names = st.session_state.outputs_table["Name"]
            if col_name in output_names:
                idx = output_names.index(col_name)
                min_val = st.session_state.outputs_table["Min"][idx]
                max_val = st.session_state.outputs_table["Max"][idx]
                
                if min_val <= val <= max_val:
                    return 'background-color: lightgreen'
                else:
                    return 'background-color: lightcoral'
        return ''
    
    # Apply styling to the dataframe
    styled_df = input_output_df.style.apply(lambda x: [highlight_outputs(val, x.name) for val in x], axis=0)
    
    st.dataframe(styled_df, use_container_width=True)



